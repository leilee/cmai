# `cmai` - AI Commit Message Generator

A command-line tool that automatically generates conventional commit messages using AI, based on your staged git changes.

Your commit messages will look like this:

![Example Git Commit Messages](./example-commit-message.png)

## Features

- 🤖 AI-powered commit message generation with multiple options:
  - Local [Ollama](https://ollama.ai/) support - **Completely FREE and private!**
    - No API key required
    - Works offline
    - Supports various models (codellama, llama2, etc.)
  - Local [LMStudio](https://lmstudio.ai/) support - **Completely FREE and private!**
    - Works with any model you have in LMStudio
    - Uses the OpenAI-compatible API
    - Great for privacy and offline use
  - OpenRouter (default) using `google/gemini-flash-1.5-8b` - SUPER CHEAP!
    - Around $0.00001/commit -> $1 per 100K commit messages!
  - Custom API support - Bring your own provider!
- 🧠 Adaptive prompting strategies based on model size (small/medium/large)
- 📝 Follows [Conventional Commits](https://www.conventionalcommits.org/) format
- 🔒 Secure local API key storage
- 🚀 Automatic git commit and push
- 🐛 Debug mode for troubleshooting
- 💻 Cross-platform support (Windows, Linux, macOS)

## Prerequisites

- Git installed and configured
- For Windows: Git Bash or WSL installed
- For Linux/macOS: Bash shell environment
- `curl` installed
- One of the following:
  - An [OpenRouter](https://openrouter.ai/) API key (default)
  - [Ollama](https://ollama.ai/) installed and running locally
  - [LMStudio](https://lmstudio.ai/) installed and running locally

## Installation

### Linux/macOS

1. Clone this repository: 

```bash
git clone https://github.com/mrgoonie/cmai.git
cd cmai
```

2. Run the installation script:

```bash
./install.sh
```

This will:
- Create necessary directories
- Install the script globally as `cmai`
- Set up proper permissions

### Windows

1. Clone this repository:

```bash
git clone https://github.com/mrgoonie/cmai.git
cd cmai
```

2. Run the installation script in Git Bash:

```bash
./install.sh
```

Or manually:
- Copy `git-commit.sh` to `%USERPROFILE%\git-commit-ai\`
- Add the directory to your PATH environment variable
- Rename `git-commit.sh` to `cmai.sh`

This will:
- Create necessary directories
- Install the script globally as `cmai`
- Set up proper permissions

## Configuration

### OpenRouter (Default)

Set up your OpenRouter API key:

```bash
cmai <your_openrouter_api_key>
```

The API key will be securely stored in:
- Linux/macOS: `~/.config/git-commit-ai/config`
- Windows: `%USERPROFILE%\.config\git-commit-ai\config`

### Ollama (Local)

1. Install Ollama from https://ollama.ai/
2. Pull your preferred model (e.g., codellama):
```bash
ollama pull deepseek-r1:7b
```
3. Make sure Ollama is running in the background

### LMStudio (Local)

1. Install LMStudio from https://lmstudio.ai/
2. Download and load your preferred model in LMStudio
3. Start the local server in LMStudio by clicking on "Start Server" in the Chat tab
4. The server will run on http://localhost:1234/v1 by default

## Usage

![Usage Demonstration](./usage.png)

1. Make your code changes
2. Generate commit message and commit changes:

```bash
cmai
```

To also push changes to remote:
```bash
cmai --push
# or
cmai -p
```

### AI Provider Options

By default, CMAI uses OpenRouter with the `google/gemini-flash-1.5-8b` model. You can switch between different providers:

```bash
# Use Ollama (local)
cmai --use-ollama

# Use LMStudio (local)
cmai --use-lmstudio

# Switch back to OpenRouter
cmai --use-openrouter

# Use a custom provider
cmai --use-custom http://your-api-endpoint
```

The provider choice is saved for future use, so you only need to specify it once.

### Model Selection

#### OpenRouter Models
When using OpenRouter, you can choose from their available models:
```bash
cmai --model qwen/qwen-2.5-coder-32b-instruct
```
List of available models: https://openrouter.ai/models

#### Ollama Models
When using Ollama, first pull your desired model:
```bash
# Pull the model
ollama pull deepseek-r1:7b

# Use the model
cmai --model deepseek-r1:7b
```
List of available models: https://ollama.ai/library

Popular models for commit messages:
- `deepseek-r1` - Optimized for code understanding
- `llama2` - Good all-around performance
- `mistral` - Fast and efficient

This will:
- Stage all changes
- Generate a commit message using AI
- Commit the changes
- Push to the remote repository (if --push flag is used)

### Debug Mode

To see detailed information about what's happening:

```bash
cmai --debug
```

You can combine flags:
```bash
cmai --debug --push
```

## Command Line Options

```bash
Usage: cmai [options] [api_key]

Options:
  --debug               Enable debug mode
  --push, -p            Push changes after commit
  --model <model>       Use specific model (default: google/gemini-flash-1.5-8b)
  --use-ollama          Use Ollama as provider (saves for future use)
  --use-lmstudio        Use LMStudio as provider (saves for future use)
  --use-openrouter      Use OpenRouter as provider (saves for future use)
  --use-custom <url>    Use custom provider with base URL (saves for future use)
  -h, --help            Show this help message
```

## Examples

### OpenRouter (Default)
```bash
# First time setup with API key
cmai <your_openrouter_api_key>

# Normal usage
cmai

# Use a different OpenRouter model
cmai --model "google/gemini-flash-1.5-8b"

# Debug mode with push
cmai --debug --push
```

### Ollama (Local)
```bash
# Switch to Ollama provider
cmai --use-ollama

# Use a specific deepseek-r1 model
cmai --model deepseek-r1:7b

# Debug mode with Ollama
cmai --debug --use-ollama
```

### LMStudio (Local)
```bash
# Switch to LMStudio provider
cmai --use-lmstudio

# Use a specific model in LMStudio
cmai --model "your-model-name"

# Debug mode with LMStudio
cmai --debug --use-lmstudio
```

### Custom Provider
```bash
# Use a custom API provider
cmai --use-custom http://my-api.com

# Use custom provider with specific model
cmai --use-custom http://my-api.com --model my-custom-model
```

### Common Options
```bash
# Commit and push
cmai --push
# or
cmai -p

# Debug mode
cmai --debug

# Use a different API endpoint
cmai --base-url https://api.example.com/v1

# Combine multiple flags
cmai --debug --push --model your-model --base-url https://api.example.com/v1
```

Example generated commit messages:
- `feat(api): add user authentication system`
- `fix(data): resolve memory leak in data processing`
- `docs(api): update API documentation`
- `style(ui): improve responsive layout for mobile devices`

## Directory Structure

### Linux/macOS

```
~
├── git-commit-ai/
│ └── git-commit.sh
├── .config/
│ └── git-commit-ai/
│   ├── config.json  # Configuration (API keys, models, providers)
│   └── providers/   # Provider-specific configurations
└── usr/
  └── local/
    └── bin/
      └── cmai -> ~/git-commit-ai/git-commit.sh
```

### Windows

```
%USERPROFILE%
├── git-commit-ai/
│ └── cmai.sh
└── .config/
  └── git-commit-ai/
    ├── config.json
    └── providers/
```

## Security

- API key is stored locally with restricted permissions (600)
- Configuration directory is protected (700)
- No data is stored or logged except the API key
- All communication is done via HTTPS

## Troubleshooting

1. **No API key found**
   - Run `cmai your_openrouter_api_key` to configure

2. **Permission denied**
   - Check file permissions: `ls -la ~/.config/git-commit-ai`
   - Should show: `drwx------` for directory and `-rw-------` for config file

3. **Debug mode**
   - Run with `--debug` flag to see detailed logs
   - Check API responses and git operations

4. **Windows-specific issues**
   - Make sure Git Bash is installed
   - Check if curl is available in Git Bash
   - Verify PATH environment variable includes the installation directory

## Uninstallation

### Linux/macOS

```bash
bash
sudo rm /usr/local/bin/cmai
rm -rf ~/git-commit-ai
rm -rf ~/.config/git-commit-ai
```

### Windows

```bash
rm -rf "$USERPROFILE/git-commit-ai"
rm -rf "$USERPROFILE/.config/git-commit-ai"
```
Then remove the directory from your PATH environment variable

## Testing Framework

This project includes an automated testing framework to evaluate commit message generation quality across different AI models and scenarios.

### Running Tests

#### Single Model Testing
Test a specific provider and model with multiple scenarios:

```bash
python3 tests/auto_tester.py [--provider PROVIDER] [--model MODEL] [rounds]
```

- `--provider`: Provider to use (ollama, openrouter) - default: ollama
- `--model`: Model name - default: qwen3:4b  
- `rounds`: Number of test rounds per scenario - default: 3

Examples:
```bash
# Test default ollama:qwen3:4b with 5 rounds
python3 tests/auto_tester.py 5

# Test specific Ollama model
python3 tests/auto_tester.py --provider ollama --model qwen2.5:3b 3

# Test OpenRouter model  
python3 tests/auto_tester.py --provider openrouter --model qwen/qwen-2.5-coder-32b-instruct:free 2
```

#### Multi-Model Comparison
Compare multiple models side by side:

```bash
python3 tests/auto_tester.py --multi model1,model2,model3 [rounds]
```

Examples:
```bash
# Compare Ollama models
python3 tests/auto_tester.py --multi qwen3:4b,qwen2.5:3b,qwen3:1.7b 2

# Compare different providers
python3 tests/auto_tester.py --multi qwen3:4b,qwen/qwen-2.5-coder-32b-instruct:free 3
```

#### Help
```bash
python3 tests/auto_tester.py --help
```

### Test Scenarios

The framework includes 9 test scenarios covering different commit types:
- **simple_fix**: Basic bug fixes
- **new_feature**: New functionality implementation
- **documentation_update**: README and docs changes
- **refactor_large**: Major code restructuring
- **style_formatting**: Code formatting and style changes
- **performance_optimization**: Performance improvements
- **test_addition**: Adding new tests
- **chore_dependencies**: Dependency updates
- **adaptive_prompting_feature**: Complex feature implementation (external templates)

### Test Reports

Tests generate detailed reports including:
- Overall accuracy statistics
- Per-scenario consistency analysis
- Common issues identification
- Model comparison metrics
- Recommendations for improvement

Reports are saved to `tests/test_report_YYYYMMDD_HHMMSS.txt` and also displayed in the console.

### Prerequisites for Testing

1. **For Ollama models**: Ensure Ollama is running and models are pulled
   ```bash
   ollama serve
   ollama pull qwen3:4b
   ollama pull qwen2.5:3b
   ollama pull qwen3:1.7b
   ```

2. **For OpenRouter models**: Ensure API key is configured
   ```bash
   cmai --api-key your_openrouter_api_key
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes (using `cmai` 😉)
4. Test your changes using the automated testing framework
5. Push to the branch
6. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenRouter](https://openrouter.ai/) for providing the AI API
- [Conventional Commits](https://www.conventionalcommits.org/) for the commit message format

## My other products

- [DigiCord AI](https://digicord.site) - The Most Useful AI Chatbot on Discord
- [IndieBacklink.com](https://indiebacklink.com) - Indie Makers Unite: Feature, Support, Succeed
- [TopRanking.ai](https://topranking.ai) - AI Directory, listing AI products
- [ZII.ONE](https://zii.one) - Personalized Link Shortener
- [VidCap.xyz](https://vidcap.xyz) - Extract Youtube caption, download videos, capture screenshot, summarize,…
- [ReadTube.me](https://readtube.me) - Write blog articles based on Youtube videos
- [BoostTogether.com](https://boosttogether.com) - The Power of WE in Advertising
- [AIVN.Site](https://aivn.site) - Face Swap, Remove BG, Photo Editor,…
- [DxUp.dev](https://dxup.dev) - Developer-focused platform for app deployment & centralized cloud resource management.
