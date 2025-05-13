def run_tests(config):
    import os
    from dotenv import load_dotenv
    from litellm import completion
    from core.models.LLMResponse import LLMResponse, Choices, Message  # Import the necessary classes

    # Load environment variables from .env file
    load_dotenv()

    # Get the OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')

    prompt = config.get('prompt')
    
    # Use LittleLM to generate a response
    result = completion(model='openai/gpt-4o', 
                        messages=[{"role": "user", "content": prompt}],
                        api_key=openai_api_key)  # Pass the API key

    # Decode the result into an LLMResponse instance
    choices = [Choices(finish_reason=choice.finish_reason, 
                       index=choice.index, 
                       message=Message(content=choice.message['content'], 
                                       role=choice.message['role'])) for choice in result.choices]
    
    llm_response = LLMResponse(id=result.id, 
                               created=result.created, 
                               model=result.model, 
                               object=result.object, 
                               choices=choices)

    print("Decoded Response:", llm_response.to_dict())

    # Prepare the report
    report = {"prompt": prompt, "result": llm_response.to_dict()}
    from core.reporter import save_report
    save_report(report)