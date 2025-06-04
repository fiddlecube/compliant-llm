# Blackbox testing / Redteam your API

## How to run

1. Setup the repo and run to add your provider keys

```bash
compliant-llm dashboard
```


2. In config enable blackbox testing and add the required fields

```yaml
blackbox:
  enabled: true
  api_url: "https://sample-chat-bot-fiddlecube.vercel.app/api/chat" # API endpoint
  api_key: "" # API key if required
  headers: {} # API headers if required
  payload:
    - file: "./configs/blackbox/payload.json" # Payload file
```

3. You can add and remove strategies from here:

```yaml
strategies:
  - name: prompt_injection
    enabled: true
  - name: jailbreak
    enabled: true
```

4. Run the test

```bash
compliant-llm test --config configs/config.yaml
```