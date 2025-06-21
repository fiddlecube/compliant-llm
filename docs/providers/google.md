# Setup Google/Gemini

```bash
export GOOGLE_API_KEY="your-api-key"
```

## Usage

```bash
# Using Gemini Pro
compliant-llm test --prompt "Your prompt here" --provider "google/gemini-pro"

# Using Gemini Pro Vision
compliant-llm test --prompt "Your prompt here" --provider "google/gemini-pro-vision"
```

## Configuration

Add to your YAML configuration:

```yaml
provider: google/gemini-pro
temperature: 0.7
```

## Models

- `google/gemini-pro` - Text generation
- `google/gemini-pro-vision` - Multimodal (text + images)
- `google/gemini-flash` - Faster, more efficient model 