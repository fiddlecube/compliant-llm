# CLI Documentation

Prompt Secure provides a comprehensive command-line interface for testing and evaluating AI system prompts against various attack vectors.

## Command Overview

The main CLI entry point is `python -m cli.main`, followed by one of these commands:

- [`test`](test.md): Run prompt tests against specified strategies
- [`report`](report.md): Display and analyze test results
- [`generate`](generate.md): Create configuration and prompt templates
- [`config`](config.md): Manage and validate configuration files

## Environment Setup

Before using the CLI, set up the necessary API keys as environment variables:

```bash
# For OpenAI models
export OPENAI_API_KEY=your-api-key-here

# For other providers (if needed)
export ANTHROPIC_API_KEY=your-anthropic-key
export GOOGLE_API_KEY=your-google-key
```

You can also create a `.env` file in your project root with these variables.

## File Structure

- **Reports**: All generated reports are saved to the `reports/` directory by default (excluded from git)
- **Configs**: Configuration files are stored in the `configs/` directory
- **Templates**: Template files for generating configs/prompts are in the `templates/` directory

## Command Details

For detailed information about each command, see the individual command pages:

- [Test Command](test.md)
- [Report Command](report.md)
- [Generate Command](generate.md)
- [Config Command](config.md)

## Best Practices

1. **Use Configuration Files**: For complex testing scenarios, use YAML config files instead of command-line arguments
2. **Organize Reports**: Use descriptive filenames for reports to organize test results
3. **Parallel Testing**: For large test suites, use the `--parallel` flag to speed up execution
4. **Provider Selection**: Test against multiple providers to evaluate prompt performance across different models
5. **Regular Testing**: Incorporate prompt testing into your development workflow to catch vulnerabilities early
