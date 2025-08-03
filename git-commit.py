#!/usr/bin/env python3
"""
AI-powered Git Commit Message Generator

This script generates conventional commit messages using various AI providers
including OpenRouter, Ollama, LMStudio, and custom providers.
"""

import argparse
import json
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Tuple, Optional


class Config:
    """Handles JSON-based configuration management for the git commit tool."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "git-commit-ai"
        self.providers_dir = self.config_dir / "providers"
        self.main_config_file = self.config_dir / "config.json"
        
        # Default provider configurations
        self.default_configs = {
            "openrouter": {
                "api_key": "",
                "model": "google/gemini-flash-1.5-8b",
                "base_url": "https://openrouter.ai/api/v1"
            },
            "ollama": {
                "api_key": "",
                "model": "qwen3:1.7b",
                "base_url": "http://localhost:11434/api"
            },
            "lmstudio": {
                "api_key": "",
                "model": "default",
                "base_url": "http://localhost:1234/v1"
            },
            "custom": {
                "api_key": "",
                "model": "",
                "base_url": ""
            }
        }
        
        # Create config directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.providers_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.chmod(0o700)
        self.providers_dir.chmod(0o700)
        
        # Migrate old configuration if needed
        self._migrate_old_config()
    
    def _migrate_old_config(self) -> None:
        """Migrate from old single-file configuration to new JSON structure."""
        old_files = {
            "config": self.config_dir / "config",
            "model": self.config_dir / "model", 
            "base_url": self.config_dir / "base_url",
            "provider": self.config_dir / "provider"
        }
        
        # Check if old config exists
        old_config_exists = any(f.exists() for f in old_files.values())
        
        if old_config_exists and not self.main_config_file.exists():
            # Read old configuration
            old_provider = self._read_old_file(old_files["provider"], "openrouter")
            old_api_key = self._read_old_file(old_files["config"], "")
            old_model = self._read_old_file(old_files["model"], "")
            old_base_url = self._read_old_file(old_files["base_url"], "")
            
            # Create provider config with old values
            if old_provider in self.default_configs:
                provider_config = self.default_configs[old_provider].copy()
                if old_api_key:
                    provider_config["api_key"] = old_api_key.split()[0]  # Remove extra args
                if old_model:
                    provider_config["model"] = old_model
                if old_base_url:
                    provider_config["base_url"] = old_base_url
                
                # Save migrated config
                self.save_provider_config(old_provider, provider_config)
                self.set_current_provider(old_provider)
            
            # Remove old files
            for old_file in old_files.values():
                if old_file.exists():
                    old_file.unlink()
    
    def _read_old_file(self, file_path: Path, default: str = "") -> str:
        """Read old configuration file format."""
        if file_path.exists():
            return file_path.read_text().strip()
        return default
    
    def _load_json_file(self, file_path: Path, default: Dict) -> Dict:
        """Load JSON configuration file."""
        if file_path.exists():
            try:
                with file_path.open('r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return default.copy()
    
    def _save_json_file(self, file_path: Path, data: Dict) -> None:
        """Save JSON configuration file."""
        with file_path.open('w') as f:
            json.dump(data, f, indent=2)
        file_path.chmod(0o600)
    
    def get_main_config(self) -> Dict:
        """Get main configuration."""
        default_main_config = {
            "current_provider": "openrouter",
            "version": "2.0"
        }
        return self._load_json_file(self.main_config_file, default_main_config)
    
    def save_main_config(self, config: Dict) -> None:
        """Save main configuration."""
        self._save_json_file(self.main_config_file, config)
    
    def get_provider_config_file(self, provider: str) -> Path:
        """Get path to provider configuration file."""
        return self.providers_dir / f"{provider}.json"
    
    def get_provider_config(self, provider: str) -> Dict:
        """Get provider configuration."""
        if provider not in self.default_configs:
            raise ValueError(f"Unknown provider: {provider}")
        
        config_file = self.get_provider_config_file(provider)
        return self._load_json_file(config_file, self.default_configs[provider])
    
    def save_provider_config(self, provider: str, config: Dict) -> None:
        """Save provider configuration."""
        if provider not in self.default_configs:
            raise ValueError(f"Unknown provider: {provider}")
        
        config_file = self.get_provider_config_file(provider)
        self._save_json_file(config_file, config)
    
    def get_current_provider(self) -> str:
        """Get current provider."""
        main_config = self.get_main_config()
        return main_config.get("current_provider", "openrouter")
    
    def set_current_provider(self, provider: str) -> None:
        """Set current provider."""
        if provider not in self.default_configs:
            raise ValueError(f"Unknown provider: {provider}")
        
        main_config = self.get_main_config()
        main_config["current_provider"] = provider
        self.save_main_config(main_config)
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """Get API key for provider."""
        if provider is None:
            provider = self.get_current_provider()
        config = self.get_provider_config(provider)
        return config.get("api_key", "")
    
    def save_api_key(self, api_key: str, provider: Optional[str] = None) -> None:
        """Save API key for provider."""
        if provider is None:
            provider = self.get_current_provider()
        
        # Clean API key (remove quotes and extra arguments)
        api_key = api_key.split()[0] if api_key else ""
        
        config = self.get_provider_config(provider)
        config["api_key"] = api_key
        self.save_provider_config(provider, config)
    
    def get_model(self, provider: Optional[str] = None) -> str:
        """Get model for provider."""
        if provider is None:
            provider = self.get_current_provider()
        config = self.get_provider_config(provider)
        return config.get("model", "")
    
    def save_model(self, model: str, provider: Optional[str] = None) -> None:
        """Save model for provider."""
        if provider is None:
            provider = self.get_current_provider()
        config = self.get_provider_config(provider)
        config["model"] = model
        self.save_provider_config(provider, config)
    
    def get_base_url(self, provider: Optional[str] = None) -> str:
        """Get base URL for provider."""
        if provider is None:
            provider = self.get_current_provider()
        config = self.get_provider_config(provider)
        return config.get("base_url", "")
    
    def save_base_url(self, base_url: str, provider: Optional[str] = None) -> None:
        """Save base URL for provider."""
        if provider is None:
            provider = self.get_current_provider()
        config = self.get_provider_config(provider)
        config["base_url"] = base_url
        self.save_provider_config(provider, config)
    
    def get_provider(self) -> str:
        """Get current provider (for backward compatibility)."""
        return self.get_current_provider()
    
    def save_provider(self, provider: str) -> None:
        """Save provider (for backward compatibility)."""
        self.set_current_provider(provider)


class GitCommitAI:
    """Main class for AI-powered git commit message generation."""
    
    PROVIDERS = {
        "openrouter": "openrouter",
        "ollama": "ollama", 
        "lmstudio": "lmstudio",
        "custom": "custom"
    }
    
    PROVIDER_URLS = {
        "openrouter": "https://openrouter.ai/api/v1",
        "ollama": "http://localhost:11434/api",
        "lmstudio": "http://localhost:1234/v1"
    }
    
    DEFAULT_MODELS = {
        "ollama": "qwen3:1.7b",
        "openrouter": "google/gemini-flash-1.5-8b",
        "lmstudio": "default"
    }
    
    def __init__(self):
        self.config = Config()
        self.debug = False
        self.push = False
        self.stage_changes = True
        self.dry_run = False
        
        # Load configuration
        self.provider = self.config.get_current_provider()
        provider_config = self.config.get_provider_config(self.provider)
        self.base_url = provider_config.get("base_url", "")
        self.model = provider_config.get("model", "")
        
        # Set default model if not configured
        if not self.model and self.provider in self.DEFAULT_MODELS:
            self.model = self.DEFAULT_MODELS[self.provider]
    
    def debug_log(self, message: str, content: str = "") -> None:
        """Log debug messages if debug mode is enabled."""
        if self.debug:
            print(f"DEBUG: {message}")
            if content:
                print("DEBUG: Content >>>")
                print(content)
                print("DEBUG: <<<")
    
    def setup_provider(self, provider: str, base_url: str, model: str) -> None:
        """Setup provider configuration."""
        self.provider = provider
        self.base_url = base_url
        self.model = model
        
        # Get current provider config and update it
        provider_config = self.config.get_provider_config(provider)
        provider_config["base_url"] = base_url
        provider_config["model"] = model
        
        # Save provider config and set as current
        self.config.save_provider_config(provider, provider_config)
        self.config.set_current_provider(provider)
    
    def check_ollama_requirements(self) -> None:
        """Check if Ollama is running and model exists."""
        if self.provider != "ollama":
            return
            
        # Check if Ollama is running
        try:
            subprocess.run(["pgrep", "ollama"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Error: Ollama server not running. Please start Ollama first:")
            print("ollama serve")
            sys.exit(1)
        
        # Check if model exists
        try:
            result = subprocess.run(["ollama", "ls"], capture_output=True, text=True, check=True)
            models = [line.split()[0] for line in result.stdout.strip().split('\n')[1:]]
            if self.model not in models:
                print(f"Error: Model '{self.model}' not found in Ollama. Please pull it first:")
                print(f"ollama pull {self.model}")
                sys.exit(1)
        except subprocess.CalledProcessError:
            print("Error: Failed to check Ollama models")
            sys.exit(1)
    
    def get_git_changes(self) -> Tuple[str, str, bool, str]:
        """Get git changes and diff content."""
        # Stage changes if requested
        if self.stage_changes:
            subprocess.run(["git", "add", "."], check=True)
        
        # Get file changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True, text=True, check=True
        )
        changes = result.stdout.replace('\t', ' ').strip()
        
        if not changes:
            print("No staged changes found. Please stage your changes using 'git add' first.")
            sys.exit(1)
        
        # Get diff content
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, check=True
        )
        diff_content = result.stdout
        
        # Smart diff handling based on size
        diff_char_count = len(diff_content)
        small_diff_limit = 15000
        medium_diff_limit = 50000
        use_diff_content = True
        detailed_changes = ""
        
        self.debug_log(f"Diff content size: {diff_char_count} characters")
        
        if diff_char_count <= small_diff_limit:
            self.debug_log("Using full diff content (small diff)")
        elif diff_char_count <= medium_diff_limit:
            self.debug_log("Truncating diff content (medium diff)")
            truncate_to = 12000
            diff_content = diff_content[:truncate_to]
            diff_content += f"\n\n[... diff truncated due to size - showing first {truncate_to} characters only]"
        else:
            self.debug_log(f"Diff too large ({diff_char_count} chars), using file list only")
            use_diff_content = False
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True, text=True, check=True
            )
            detailed_changes = result.stdout
        
        return changes, diff_content, use_diff_content, detailed_changes
    
    def build_openrouter_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> Dict:
        """Build request for OpenRouter/Custom providers."""
        system_message = "You are a git commit message generator. Create conventional commit messages."
        
        if use_diff:
            user_content = f"""Generate a commit message for these changes:

## File changes:
<file_changes>
{changes}
</file_changes>

## Diff:
<diff>
{diff}
</diff>

## Format:
<type>(<scope>): <subject>

<body>

Important:
- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
- Subject: max 70 characters, imperative mood, no period
- Body: list changes to explain what and why, not how
- Scope: max 3 words
- For minor changes: use 'fix' instead of 'feat'
- Do not wrap your response in triple backticks
- Response should be the commit message only, no explanations."""
        else:
            user_content = f"""Generate a commit message for these changes:

## File changes:
<file_changes>
{changes}
</file_changes>

## File statistics:
<file_stats>
{detailed_changes}
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.

## Format:
<type>(<scope>): <subject>

<body>

Important:
- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
- Subject: max 70 characters, imperative mood, no period
- Body: list changes to explain what and why, not how
- Scope: max 3 words
- For minor changes: use 'fix' instead of 'feat'
- Do not wrap your response in triple backticks
- Response should be the commit message only, no explanations."""
        
        return {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ]
        }
    
    def build_ollama_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> Dict:
        """Build request for Ollama provider."""
        common_instructions = """Follow the conventional commits format: <type>(<scope>): <subject>

<body>

Where type is one of: feat, fix, docs, style, refactor, perf, test, chore.
- Scope: max 3 words.
- Keep the subject under 70 chars.
- Body: list changes to explain what and why
- Use 'fix' for minor changes
- Do not wrap your response in triple backticks
- Response should be the commit message only, no explanations."""
        
        if use_diff:
            prompt = f"""Generate a conventional commit message for these changes: 
<file_changes>
{changes}
</file_changes>

## Diff:
<diff>
{diff}
</diff>

## Instructions:
{common_instructions}"""
        else:
            prompt = f"""Generate a conventional commit message for these changes: 
<file_changes>
{changes}
</file_changes>

## File statistics:
<file_stats>
{detailed_changes}
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.

## Instructions:
{common_instructions}"""
        
        return {
            "model": self.model,
            "prompt": prompt,
            "think": False,
            "stream": False
        }
    
    def make_api_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> str:
        """Make API request to the configured provider."""
        self.debug_log(f"Using provider: {self.provider}")
        self.debug_log(f"Request model: {self.model}")
        
        headers = {"Content-Type": "application/json"}
        
        if self.provider == "ollama":
            endpoint = "generate"
            url = f"{self.base_url}/{endpoint}"
            request_data = self.build_ollama_request(changes, diff, use_diff, detailed_changes)
        elif self.provider == "lmstudio":
            endpoint = "chat/completions"
            url = f"{self.base_url}/{endpoint}"
            request_data = self.build_openrouter_request(changes, diff, use_diff, detailed_changes)
        elif self.provider == "openrouter":
            endpoint = "chat/completions"
            url = f"{self.base_url}/{endpoint}"
            headers.update({
                "HTTP-Referer": "https://github.com/mrgoonie/cmai",
                "Authorization": f"Bearer {self.config.get_api_key()}",
                "X-Title": "cmai - AI Commit Message Generator"
            })
            request_data = self.build_openrouter_request(changes, diff, use_diff, detailed_changes)
        elif self.provider == "custom":
            endpoint = "chat/completions"
            url = f"{self.base_url}/{endpoint}"
            api_key = self.config.get_api_key()
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            request_data = self.build_openrouter_request(changes, diff, use_diff, detailed_changes)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        self.debug_log(f"Making request to: {url}")
        self.debug_log(f"Request data: {json.dumps(request_data, indent=2)}")
        
        try:
            # Prepare request
            data = json.dumps(request_data).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers)
            
            # Make request
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            print(f"Error making API request: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error making API request: {e}")
            sys.exit(1)
    
    def extract_commit_message(self, response: str) -> str:
        """Extract commit message from API response."""
        try:
            response_data = json.loads(response)
        except json.JSONDecodeError:
            print(f"Error: Failed to parse API response as JSON: {response}")
            sys.exit(1)
        
        commit_message = ""
        
        if self.provider == "ollama":
            commit_message = response_data.get("response", "")
            if not commit_message:
                print(f"Error: Failed to get response from Ollama. Response: {response}")
                sys.exit(1)
        elif self.provider in ["lmstudio", "openrouter", "custom"]:
            try:
                commit_message = response_data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                print(f"Error: Failed to parse response. Response: {response}")
                sys.exit(1)
        
        if not commit_message:
            print(f"Failed to generate commit message. API response: {response}")
            sys.exit(1)
        
        # Clean the message
        commit_message = commit_message.replace('\\n', '\n').replace('\\r', '').strip()
        
        return commit_message
    
    def execute_commit(self, commit_message: str) -> None:
        """Execute git commit or show preview in dry-run mode."""
        if self.dry_run:
            print("Dry run mode - Generated commit message:")
            print("=" * 39)
            print(commit_message)
            print("=" * 39)
            print("Use 'cmai' without --dry-run to execute the commit.")
            return
        
        self.debug_log("Executing git commit")
        try:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
        except subprocess.CalledProcessError:
            print("Failed to commit changes")
            sys.exit(1)
        
        if self.push:
            self.debug_log("Pushing to origin")
            try:
                subprocess.run(["git", "push", "origin"], check=True)
                print("Successfully pushed changes to origin")
            except subprocess.CalledProcessError:
                print("Failed to push changes")
                sys.exit(1)
        
        print("Successfully committed changes with message:")
        print(commit_message)
    
    def run(self, args) -> None:
        """Main execution method."""
        self.debug_log("Script started")
        
        # Check API key for providers that need it
        if self.provider == "openrouter" and not self.config.get_api_key():
            print("No API key found. Please provide the OpenRouter API key using --api-key flag")
            sys.exit(1)
        
        # Check provider-specific requirements
        self.check_ollama_requirements()
        
        # Get git changes
        changes, diff_content, use_diff_content, detailed_changes = self.get_git_changes()
        
        # Make API request
        response = self.make_api_request(changes, diff_content, use_diff_content, detailed_changes)
        
        # Extract and execute commit
        commit_message = self.extract_commit_message(response)
        self.execute_commit(commit_message)
        
        self.debug_log("Script completed successfully")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Git Commit Message Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --api-key your_api_key          # First time setup with API key
  %(prog)s --use-ollama                    # Switch to Ollama provider
  %(prog)s --use-openrouter                # Switch back to OpenRouter
  %(prog)s --use-lmstudio                  # Switch to LMStudio provider
  %(prog)s --use-custom http://my-api.com  # Use custom provider
        """
    )
    
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--push", "-p", action="store_true", help="Push changes after commit")
    parser.add_argument("--no-stage", action="store_true", help="Do not stage changes automatically")
    parser.add_argument("--dry-run", action="store_true", help="Preview commit message without executing git commit")
    parser.add_argument("--model", help="Use specific model")
    parser.add_argument("--base-url", help="Set base URL for API")
    parser.add_argument("--api-key", help="Set API key")
    parser.add_argument("--use-ollama", action="store_true", help="Use Ollama as provider")
    parser.add_argument("--use-openrouter", action="store_true", help="Use OpenRouter as provider") 
    parser.add_argument("--use-lmstudio", action="store_true", help="Use LMStudio as provider")
    parser.add_argument("--use-custom", help="Use custom provider with base URL")
    
    args = parser.parse_args()
    
    app = GitCommitAI()
    
    # Set flags from arguments
    app.debug = args.debug
    app.push = args.push
    app.stage_changes = not args.no_stage
    app.dry_run = args.dry_run
    
    # Handle provider setup
    if args.use_ollama:
        app.setup_provider("ollama", app.PROVIDER_URLS["ollama"], app.DEFAULT_MODELS["ollama"])
    elif args.use_openrouter:
        app.setup_provider("openrouter", app.PROVIDER_URLS["openrouter"], app.DEFAULT_MODELS["openrouter"])
    elif args.use_lmstudio:
        app.setup_provider("lmstudio", app.PROVIDER_URLS["lmstudio"], app.DEFAULT_MODELS["lmstudio"])
    elif args.use_custom:
        app.setup_provider("custom", args.use_custom, "")
    
    # Handle configuration updates
    if args.model:
        app.model = args.model.strip('"')
        app.config.save_model(app.model, app.provider)
    
    if args.base_url:
        app.base_url = args.base_url
        app.config.save_base_url(app.base_url, app.provider)
    
    if args.api_key:
        app.config.save_api_key(args.api_key, app.provider)
    
    app.run(args)


if __name__ == "__main__":
    main()
