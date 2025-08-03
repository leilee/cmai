# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `cmai` - an AI-powered command-line tool that generates conventional commit messages using various AI providers. The tool analyzes staged git changes and generates appropriate commit messages following the conventional commits format.

### Core Architecture

- **Main Script**: `git-commit.py` (Python implementation)
- **Configuration**: JSON-based config system in `~/.config/git-commit-ai/`
- **AI Providers**: Supports OpenRouter, Ollama, LMStudio, and custom providers
- **Template System**: Adaptive prompting strategies based on model size in `prompts/` directory
- **Testing Framework**: Comprehensive automated testing in `tests/` directory

### Key Components

1. **Provider System**: Modular AI provider support with different API formats
2. **Adaptive Prompting**: Different prompt templates for small/medium/large models
3. **Config Management**: JSON-based configuration with migration from legacy format
4. **Testing Suite**: Automated testing across multiple providers and models

## Development Commands

### Running Tests

```bash
# Run automated tests with default model (ollama:qwen3:4b)
python3 tests/auto_tester.py 3

# Test specific provider and model
python3 tests/auto_tester.py --provider ollama --model qwen2.5:3b 3
python3 tests/auto_tester.py --provider openrouter --model qwen/qwen-2.5-coder-32b-instruct:free 2

# Multi-model comparison
python3 tests/auto_tester.py --multi qwen3:4b,qwen2.5:3b,qwen3:1.7b 2

# Test specific scenarios
python3 tests/test_runner.py list
python3 tests/test_runner.py simple_fix
python3 tests/test_runner.py all
```

### Using the Tool

```bash
# Basic usage (generates and commits)
cmai

# With different providers
cmai --use-ollama
cmai --use-openrouter
cmai --use-lmstudio

# Dry run to preview message
cmai --dry-run

# Debug mode
cmai --debug

# Commit and push
cmai --push
```

### Installation Testing

```bash
# Linux/macOS/Windows
./install.sh

# Test installation
cmai --help
```

## Code Structure

### Python Implementation

The project uses a single Python implementation (`git-commit.py`):
- **Maintainable**: Object-oriented design with clear separation of concerns
- **Feature-rich**: Advanced template system, comprehensive testing framework
- **No dependencies**: Uses only Python standard library (urllib, json, etc.)
- **Cross-platform**: Works on Linux, macOS, and Windows

### Configuration System

- **Location**: `~/.config/git-commit-ai/`
- **Main config**: `config.json` (current provider)
- **Provider configs**: `providers/openrouter.json`, `providers/ollama.json`, etc.
- **Migration**: Automatic migration from legacy single-file format

### Template System

Located in `prompts/` directory:
- `small_model.txt` - For models ≤2B parameters (1b, 1.7b, 2b)
- `medium_model.txt` - For models 3-10B parameters (3b, 4b, 7b, 8b)
- `large_model.txt` - For models ≥30B parameters (30b, 32b, 70b, 72b)
- `final_check.txt` - Post-processing validation
- Provider-specific templates: `openrouter_system.txt`, `ollama_base.txt`

### Testing Framework

- **test_cases.py**: Defines test scenarios for different commit types
- **auto_tester.py**: Automated batch testing with statistical analysis
- **test_runner.py**: Interactive testing for prompt development

## Important Patterns

### Provider Detection

The system automatically detects optimal prompting strategies:
```python
def get_model_tier(self) -> str:
    # Logic to classify models as small/medium/large
    # Based on known model parameter counts
```

### Error Handling

All providers implement consistent error handling:
- API connectivity checks
- Model availability validation  
- Response format verification
- Token limit management

### Diff Processing

Smart diff handling based on size:
- Small diffs (<15k chars): Full diff included
- Medium diffs (15k-50k chars): Truncated with warning
- Large diffs (>50k chars): File list only with statistics

## Testing Guidelines

### Adding New Test Cases

Edit `tests/test_cases.py`:
```python
TestCase(
    name="your_scenario",
    description="Description of the change type",
    changes="M file1.py A file2.js",
    diff="...",
    expected_type="feat|fix|docs|etc",
    expected_scope="optional_scope"
)
```

### Validating Changes

Always run the test suite when making changes:
1. Test with multiple providers: `python3 tests/auto_tester.py --multi qwen3:4b,openrouter:qwen/qwen-2.5-coder-32b-instruct:free`
2. Check format compliance and type accuracy
3. Verify consistency across test rounds

### Performance Testing

Monitor token usage and response times:
- Use `--debug` flag to see API request/response details
- Check diff truncation logic for large changes
- Validate adaptive prompting is working correctly

## Security Considerations

- API keys stored with 600 permissions in `~/.config/git-commit-ai/`
- Config directory protected with 700 permissions
- No logging of sensitive data
- HTTPS-only for remote providers

## Contributing Workflow

1. Test changes across multiple providers and models
2. Run the automated test suite
3. Verify backwards compatibility with existing configs
4. Update documentation if adding new features