# 🛡️ Compliant LLM

Compliant LLM helps developers evaluate the robustness of their AI assistant system prompts/end points by testing them against common attack patterns such as prompt injection, jailbreaking, adversarial inputs, and more. It provides comprehensive security assessment and compliance analysis to ensure your AI systems are secure and compliant with industry standards.

For detailed docs refer to [docs](https://github.com/fiddlecube/compliant-llm/tree/main/docs)

## 🎯 Features [@Vini: Needs Rework]

- 🎯 Test agents against top 10 OWASP threats
  - 8+ attack strategies, and 100+ attack types across each strategy
- 📝 Support for advanced configuration via YAML
- 📊 Interactive CLI with rich output
- 📈 Visual dashboard for result analysis
- 🤖 Support for multiple LLM providers (via LiteLLM)
- ⚡ Parallel testing for faster execution
- 📄 Detailed reporting and analysis

## ⚙️ Installation [@Vini: Test these commands]

```bash
mkdir compliant-llm && cd compliant-llm
uv venv .venv
source .venv/bin/activate
pip install compliant-llm
```

## Set up OPENAI, ANTHROPIC API keys

```bash
touch .env
# write the following in .env
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
GOOGLE_API_KEY=your-api-key-here
```

## 🚀 Quick Start

1. Run a basic red-teaming test via cli:

```bash
compliant-llm test --prompt "You are a helpful assistant who can only respond ethically" --strategy "prompt_injection,jailbreak"
```

2. Or get started from the UI:

```bash
compliant-llm dashboard
```

3. Or use a configuration file:

```bash
compliant-llm test --config_path configs/config.yaml
```

[@Vini: Is this accurate?]
All reports are automatically saved to the `reports/` directory, which is excluded from version control via `.gitignore`.

3. View the test report:

```bash
compliant-llm report --summary
```

4. View the latest test report in UI:

```bash
compliant-llm dashboard
```

### File Structure

- **Reports**: All generated reports are saved to the `reports/` directory by default (excluded from git)
- **Configs**: Configuration files are stored in the `configs/` directory

#### Available Testing Strategies

- `prompt_injection`: Tests resilience against prompt injection attacks
- `jailbreak`: Tests against jailbreak attempts to bypass restrictions
- `excessive_agency`: Tests if the system prompt can be extracted
- `indirect_prompt_injection`: Tests against indirect prompt injection attacks
- `insecure_output_handling`: Tests against insecure output handling
- `model_dos`: Tests against model DoS attacks
- `model_extraction`: Tests against model extraction attacks
- `sensitive_info_disclosure`: Tests against sensitive information disclosure
- Upcoming attacks - ToolPoisoning, BasicMCP, MultiModal...

## Docker [@Vini: Test these commands]

```bash
docker build -t compliant_llm .
docker run -p 8501:8501 compliant_llm
```

## Roadmap

- [ ] Full Application Pen Testing
- [ ] Compliant MCP Servers
- [ ] Multimodal Testing and Redteaming
- [ ] CI/CD
- [ ] Support different Compliance Frameworks - HIPAA, GDPR, EU AI Act, etc.
- [ ] Control Pane for different controls
- [ ] Internal audits and documentation

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
  howpublished = {\url{<https://github.com/fiddlecube/compliant-llm}}>,
}
