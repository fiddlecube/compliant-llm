# Blackbox testing / Redteam your API

## How to run

1. In config enable blackbox testing

```yaml
blackbox:
  enabled: true
  api_url: "https://sample-chat-bot-fiddlecube.vercel.app/api/chat" # API endpoint
  api_key: "" # API key if required
  headers: {} # API headers if required
  payload:
    - file: "./configs/blackbox/payload.json" # Payload file
```

2. You can add and remove strategies from here:

```yaml
strategies:
  - name: prompt_injection
    enabled: true
  - name: jailbreak
    enabled: true
```

3. Run the test

```bash
compliant-llm test --config configs/config.yaml
```