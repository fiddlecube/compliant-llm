# 🛡️ Compliant LLM

Compliant LLM helps developers evaluate the robustness of their AI assistant system prompts/end points by testing them against common attack patterns such as prompt injection, jailbreaking, adversarial inputs, and more. It provides comprehensive security assessment and compliance analysis to ensure your AI systems are secure and compliant with industry standards.

For detailed docs refer to [docs](./docs)

## 🎯 Features

- 🎯 Test agents against 8+ attack strategies
- 📝 Support for advanced configuration via YAML
- 📊 Interactive CLI with rich output
- 📈 Visual dashboard for result analysis
- 🤖 Support for multiple LLM providers (via LiteLLM)
- ⚡ Parallel testing for faster execution
- 📄 Detailed reporting and analysis

## ⚙️ Installation

### Using pip

```bash
pip install compliant-llm
```

### From source

```bash
git clone https://github.com/fiddlecube/compliant-llm.git
cd compliant-llm
pip install -e .
```

### Setting Up the Environment

1. Make sure you have Python 3.9 or newer installed:

```bash
python --version
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Set up environment variables for your API keys:

```bash
# Create a .env file in the project root
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
```

## 🚀 Quick Start

1. Run the UI App and start testing your prompts

```bash
streamlit run ui/app.py
```

2. Run a basic red-teaming test via cli:

```bash
python -m cli.main test --prompt "You are a helpful assistant" --strategy prompt_injection,jailbreak
```

3. Or use a configuration file:

```bash
python -m cli.main test --config configs/config.yaml
```

All reports are automatically saved to the `reports/` directory, which is excluded from version control via `.gitignore`.

4. View the test report:

```bash
python -m cli.main report --summary
```

4. View the latest test report in UI:

```bash
python -m cli.main dashboard
```

This will open the latest report on your browser http://localhost:8502/report


### File Structure

- **Reports**: All generated reports are saved to the `reports/` directory by default (excluded from git)
- **Configs**: Configuration files are stored in the `configs/` directory
- **Templates**: Template files for generating configs/prompts are in the `templates/` directory


#### Available Testing Strategies

- `prompt_injection`: Tests resilience against prompt injection attacks
- `jailbreak`: Tests against jailbreak attempts to bypass restrictions
- `excessive_agency`: Tests if the system prompt can be extracted
- `indirect_prompt_injection`: Tests against indirect prompt injection attacks
- `insecure_output_handling`: Tests against insecure output handling
- `model_dos`: Tests against model DoS attacks
- `model_extraction`: Tests against model extraction attacks
- `sensitive_info_disclosure`: Tests against sensitive information disclosure


## Docker

```bash
docker build -t compliant_llm .
docker run -p 8501:8501 compliant_llm
```


## 🤝 Contributors

| Developers | Contributors |
|------------|--------------|
| Those who build with `compliant-llm`. | Those who make `compliant-llm` better. |
| (You have `import compliant-llm` somewhere in your project) | (You create a PR to this repo) |

We welcome contributions from the community! Whether it's bug fixes, feature additions, or documentation improvements, your input is valuable.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## 🔍 Open Analytics

At Compliant LLM, we believe in transparency. We collect minimal, anonymized usage data to improve our product and guide our development efforts.

✅ No personal or company-identifying information


## 📝 Cite Us

@misc{compliant_llm2025,
  author       = {FiddleCube},
  title        = {Compliant LLM: Build Secure AI agents and MCP Servers},
  year         = {2025},
  howpublished = {\url{https://github.com/fiddlecube/compliant-llm}},
}
