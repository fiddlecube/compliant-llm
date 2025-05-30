import argparse
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import requests
import time

app = FastAPI(title="Ollama API Proxy")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run an Ollama proxy server")
parser.add_argument("--model", type=str, default="llama3.2:3b", help="Model name to use in Ollama")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
args = parser.parse_args()

OLLAMA_API_BASE = "http://localhost:11434/api"

# Check if Ollama is running and the model is available
def check_ollama():
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            if args.model in model_names:
                print(f"✅ Model {args.model} is available in Ollama")
                return True
            else:
                print(f"❌ Model {args.model} is not available in Ollama.")
                print(f"Available models: {model_names}")
                return False
        else:
            print(f"❌ Failed to get models from Ollama: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {str(e)}")
        return False

# Define API endpoints
@app.post("/chat/completions")
async def create_completion(request: Request):
    body = await request.json()
    
    # Get messages from the request (OpenAI format)
    messages = body.get("messages", [])
    # max_tokens = body.get("max_tokens", 100)
    temperature = body.get("temperature", 0.7)

    # Convert the messages to a prompt format Ollama can understand
    formatted_prompt = ""
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            formatted_prompt += f"<|system|>\n{content}\n"
        elif role == "user":
            formatted_prompt += f"{content}\n"
    
    start_time = time.time()
    
    # Forward the request to Ollama
    try:
        # Ollama returns a stream of JSON objects
        response = requests.post(
            f"{OLLAMA_API_BASE}/generate",
            json={
                "model": args.model,
                "prompt": formatted_prompt,
                "options": {
                    "temperature": temperature,
                    # "num_predict": max_tokens
                }
            },
            stream=False
        )

        
        if response.status_code == 200:
            # Collect the streaming response from Ollama
            full_response = ""
            finish_reason = "length"
            
            for line in response.iter_lines():
                if line:
                    # Each line is a JSON object
                    json_response = json.loads(line)
                    token = json_response.get("response", "")
                    full_response += token
                    
                    # Check if this is the last response
                    if json_response.get("done", False):
                        finish_reason = json_response.get("done_reason", "length")
                        break

            print("====full_response====", full_response)
            
            # Return OpenAI-compatible chat completion response
            return JSONResponse({
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": args.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": full_response
                        },
                        "finish_reason": finish_reason
                    }
                ],
                "usage": {
                    "prompt_tokens": len(formatted_prompt.split()),
                    "completion_tokens": len(full_response.split()),
                    "total_tokens": len(formatted_prompt.split()) + len(full_response.split())
                }
            })
        else:
            return JSONResponse({"error": f"Ollama error: {response.text}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Error: {str(e)}"}, status_code=500)

@app.get("/v1/models")
async def get_models():
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_list = [
                {
                    "id": model["name"],
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "ollama"
                }
                for model in models
            ]
            return JSONResponse({
                "data": model_list,
                "object": "list"
            })
        else:
            return JSONResponse({"error": f"Failed to get models from Ollama: {response.text}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Error: {str(e)}"}, status_code=500)

@app.get("/health")
async def health_check():
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        if response.status_code == 200:
            return {"status": "ok", "ollama": "connected"}
        else:
            return {"status": "error", "ollama": "disconnected"}
    except:
        return {"status": "error", "ollama": "disconnected"}

if __name__ == "__main__":
    print(f"🚀 Starting Ollama API Proxy for model {args.model}")
    print(f"📡 Server will run on http://{args.host}:{args.port}")
    
    # Check if Ollama is running and the model is available
    if not check_ollama():
        print("❌ Please make sure Ollama is running and the model is available.")
        exit(1)
    
    # Start the FastAPI server
    uvicorn.run(app, host=args.host, port=args.port, timeout_keep_alive=600)
