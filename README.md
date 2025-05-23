# 🛡️ Compliant LLM


Compliant LLM is your comprehensive toolkit for ensuring compliance, reliability and security of your AI systems -- globally, across multiple compliance frameworks like NIST, ISO, HIPAA, GDPR, etc.

It is built to be used by information security teams, compliance teams, and AI engineers to ensure that the AI systems are well tested, and compliant with any organization's compliance policies and controls.

It supports multiple LLM providers, and can be used to test prompts, agents, MCP servers and GenAI models.

For detailed docs refer to [docs](https://github.com/fiddlecube/compliant-llm/tree/main/docs)


## 🎯 Key Features

- 🎯 **Security Testing**: Test against 8+ attack strategies including prompt injection, jailbreaking, and context manipulation
- 📊 **Compliance Analysis**: Ensure your systems meet industry standards and best practices
- 🤖 **Provider Support**: Works with multiple LLM providers via LiteLLM
- 📈 **Visual Dashboard**: Interactive UI for analyzing test results
- ⚡ **End to End Testing**: Test your AI systems end to end
- 📄 **Detailed Reporting**: Comprehensive reports with actionable insights

## ⚙️ Installation

```bash
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

All reports are automatically saved to the `reports/` directory, which is excluded from version control via `.gitignore`.

3. View the latest test report in UI:

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
