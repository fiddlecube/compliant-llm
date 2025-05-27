[![Compliant LLM](/docs/images/github.png)](https://github.com/fiddlecube/compliant-llm)

![License](https://img.shields.io/badge/License-MIT-red)
[![GitHub Stars](https://img.shields.io/github/stars/fiddlecube/compliant-llm?style=flat)](https://github.com/fiddlecube/compliant-llm/stargazers)
[![YC](https://img.shields.io/badge/Y%20Combinator-W23-orange)](https://www.ycombinator.com/companies/fiddlecube)
[![PyPI](https://img.shields.io/pypi/dm/compliant-llm?label=pypi%20compliant-llm)](https://pypi.org/project/compliant-llm/)
[![Discord Chat](https://img.shields.io/discord/1376840449167458424?label=chat&logo=discord&color=5865F2)](https://discord.gg/yJuvmj7r)
[![Follow on X](https://img.shields.io/twitter/follow/FiddleCubeAI?style=social)](https://twitter.com/fiddlecube)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Follow-blue?logo=linkedin)](https://www.linkedin.com/company/fiddlecube)
[![Issues Closed](https://img.shields.io/github/issues-closed/fiddlecube/compliant-llm)](https://github.com/fiddlecube/compliant-llm/issues?q=is%3Aissue+is%3Aclosed)
[![Discussions](https://img.shields.io/github/discussions/fiddlecube/compliant-llm?label=discussions)](https://github.com/fiddlecube/compliant-llm/discussions)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/fiddlecube/compliant-llm?label=commit%20activity)](https://github.com/fiddlecube/compliant-llm/commits)


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

3. View the latest test report in UI:

```bash
compliant-llm dashboard
```

![](docs/gif/demo.gif)

## Roadmap

- [ ] Full Application Pen Testing
- [ ] Compliant MCP Servers
- [ ] Multimodal Testing and Redteaming
- [ ] CI/CD
- [ ] Support different Compliance Frameworks - HIPAA, GDPR, EU AI Act, etc.
- [ ] Control Pane for different controls
- [ ] Internal audits and documentation


##  Want a Self Hosted Compliant LLM?

Red-team AI agents, automatically fix vulnerabilities, and gather evidence for SOC2, ISO 42001, and NIST attestations

If you want help feel free to reach out to us at: 

🔗 [Book a slot](https://cal.com/kaushiks/fc) or drop us a line: [founders@fiddlecube.ai](mailto:founders@fiddlecube.ai).


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
