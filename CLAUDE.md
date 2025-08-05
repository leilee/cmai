# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `cmai` - an AI-powered command-line tool that generates conventional commit messages using various AI providers. The tool analyzes staged git changes and generates appropriate commit messages following the conventional commits format.

### Core Architecture

The project uses a **single-file Python implementation** (`git-commit.py`) with a sophisticated object-oriented design:

- **Main Classes**:
  - `Config`: JSON-based configuration management with automatic migration from legacy formats
  - `CommitMessageGenerator`: Core AI provider abstraction and adaptive prompting logic
  - `TestResult` & `BatchTester`: Comprehensive testing framework with statistical analysis

- **Provider System**: Unified interface supporting OpenRouter, Ollama, LMStudio, and custom APIs
- **Adaptive Prompting**: Intelligent model tier detection (small/medium/large) with context-aware prompt selection
- **Config Architecture**: Distributed JSON configs in `~/.config/git-commit-ai/providers/` with migration support
- **Testing Framework**: Automated batch testing with 9 scenarios and multi-model comparison

## Development Commands

### Testing

**Automated Batch Testing:**
```bash
# Default testing (ollama:qwen3:4b, 3 rounds)
python3 tests/auto_tester.py 3

# Provider-specific testing
python3 tests/auto_tester.py --provider ollama --model qwen2.5:3b 3
python3 tests/auto_tester.py --provider openrouter --model qwen/qwen-2.5-coder-32b-instruct:free 2

# Multi-model comparison (generates comparative analysis)
python3 tests/auto_tester.py --multi qwen3:4b,qwen2.5:3b,qwen3:1.7b 2

# Cross-provider comparison
python3 tests/auto_tester.py --multi qwen3:4b,openrouter:qwen/qwen-2.5-coder-32b-instruct:free 3
```

**Interactive Testing:**
```bash
# List all test scenarios
python3 tests/test_runner.py list

# Run specific scenario
python3 tests/test_runner.py simple_fix

# Run all scenarios interactively
python3 tests/test_runner.py all
```

**Test Reports:** Generated in `tests/test_report_YYYYMMDD_HHMMSS.txt` with accuracy metrics and analysis.

### Tool Usage & Installation

**Basic Commands:**
```bash
# Generate and commit
cmai

# Provider switching (saves preference)
cmai --use-ollama
cmai --use-openrouter  
cmai --use-lmstudio
cmai --use-custom http://your-api-endpoint

# Model selection
cmai --model qwen2.5:3b
cmai --model qwen/qwen-2.5-coder-32b-instruct:free

# Development options
cmai --dry-run    # Preview without committing
cmai --debug      # Verbose API/diff analysis
cmai --push       # Commit and push to remote
```

**Installation:**
```bash
./install.sh        # Cross-platform installer
cmai --help         # Verify installation
```

## Code Architecture

### Key Design Patterns

**Single-File Architecture:** `git-commit.py` contains all core logic (no external dependencies beyond Python stdlib)

**Config Class Pattern:**
- JSON-based distributed configuration in `~/.config/git-commit-ai/providers/`
- Automatic migration from legacy single-file configs
- Provider-specific settings with fallback to defaults

**Adaptive Prompting System:**
- `get_model_tier()`: Automatic model classification (small ≤2B, medium 3-10B, large ≥30B)
- `detect_change_context()`: Smart context detection for medium/small models
- Template selection from `prompts/` directory based on model tier

**Provider Abstraction:**
- Unified `make_api_request()` interface for all providers (OpenRouter, Ollama, LMStudio, custom)
- Provider-specific request formatting in `build_request_data()`
- Consistent error handling across all providers

### Template System Architecture

**Prompt Templates** in `prompts/`:
- `small_model.txt` - Heavy guidance for ≤2B models (detailed examples, strict format rules)
- `medium_model.txt` - Balanced approach for 3-10B models (context hints, format reminders)  
- `large_model.txt` - Minimal prompting for ≥30B models (brief format specification)
- `final_check.txt` - Post-processing validation for all models
- Provider-specific: `openrouter_system.txt`, `ollama_base.txt`, `openrouter_user.txt`

**Context Detection** (`git-commit.py:424-444`):
- Smart diff analysis for formatting vs. logic changes
- Dependency file detection for proper `chore` vs `fix` classification
- Performance optimization pattern recognition
- Large refactor detection across multiple files

### Testing Architecture

**Test Case System** (`tests/test_cases.py`):
- 9 predefined scenarios covering all conventional commit types
- Each test case includes expected type, scope, realistic diffs
- Scenarios: simple_fix, new_feature, documentation_update, refactor_large, etc.

**Batch Testing** (`tests/auto_tester.py`):
- Statistical analysis across multiple rounds
- Multi-model comparison with accuracy metrics
- Automated report generation with detailed analysis
- Format compliance validation and type accuracy tracking

## Important Implementation Details

### Model Tier Detection (`git-commit.py:405-422`)

Automatic classification based on parameter count patterns in model names:
```python
def get_model_tier(self) -> str:
    # Large: 32b, 30b, 70b, 72b → minimal prompting
    # Small: 1.7b, 1b, 2b → heavy prompting with examples  
    # Medium: 3b, 4b, 7b, 8b → balanced approach
    # Default: medium for unknown models
```

### Smart Diff Processing

Size-based diff handling to manage token limits:
- **Small diffs** (<15k chars): Full diff included in prompt
- **Medium diffs** (15k-50k chars): Truncated with warning notice
- **Large diffs** (>50k chars): File statistics only with change summary

### Context Detection Logic (`git-commit.py:424-444`)

For medium/small models, provides smart hints to avoid common misclassifications:
- **Formatting changes**: Detects spacing/indentation → suggests `style` not `fix`
- **Dependencies**: Detects package files → suggests `chore` not `fix`  
- **Performance**: Detects optimization patterns → suggests `perf` not `refactor`
- **Large refactors**: Multiple file changes → suggests `refactor` not `fix`

## Development Workflow

### Adding Test Cases

Add to `tests/test_cases.py`:
```python
TestCase(
    name="scenario_name",
    description="Description",
    changes="M file1.py A file2.js",  # git status format
    diff="...",                      # realistic git diff
    expected_type="feat|fix|docs|etc",
    expected_scope="optional_scope"
)
```

### Validating Changes

**Required testing when modifying prompts or core logic:**
```bash  
# Multi-provider validation
python3 tests/auto_tester.py --multi qwen3:4b,openrouter:qwen/qwen-2.5-coder-32b-instruct:free 3

# Check format compliance and accuracy trends
python3 tests/auto_tester.py --provider ollama --model qwen2.5:3b 5
```

**Performance validation:**
- Use `--debug` to verify diff truncation and token management
- Test with various diff sizes (small <15k, medium 15k-50k, large >50k chars)
- Verify adaptive prompting tier detection with different model names

### Adding New Providers

1. **Add default config** in `Config.__init__()` → `self.default_configs`
2. **Implement API format** in `build_request_data()` method  
3. **Add provider-specific templates** in `prompts/` directory if needed
4. **Test across all scenarios** with the automated testing framework

### Prompt Template Development

**Template hierarchy** (most to least verbose):
1. `small_model.txt` - Extensive examples and format enforcement
2. `medium_model.txt` - Context hints and gentle guidance  
3. `large_model.txt` - Minimal specification

**Context detection tuning** in `detect_change_context()`:
- Add pattern detection for new commit types
- Test detection accuracy with `--debug` flag
- Validate hints improve classification for medium/small models