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
        
        # Load system message from external file (no fallback)
        system_message = self.load_prompt_template("openrouter_system.txt")
        if not system_message:
            raise FileNotFoundError("Required prompt template 'openrouter_system.txt' not found")
        
        # Load user message template from external file (no fallback)
        user_template = self.load_prompt_template("openrouter_user.txt")
        if not user_template:
            raise FileNotFoundError("Required prompt template 'openrouter_user.txt' not found")
        
        # Build diff section based on whether to use diff content
        if use_diff:
            diff_section = f"""## Diff:
<diff>
{diff}
</diff>"""
        else:
            diff_section = f"""## File statistics:
<file_stats>
{detailed_changes}
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only."""
        
        # Format the user content using the template
        user_content = user_template.format(
            changes=changes,
            diff_section=diff_section
        )
        
        return {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ]
        }
    
    def get_model_tier(self) -> str:
        """Determine model tier based on model name for adaptive prompting."""
        model_lower = self.model.lower()
        
        # Large models (30B+) - minimal prompting needed
        if any(size in model_lower for size in ['32b', '30b', '70b', '72b']):
            return 'large'
        
        # Small models (≤2B) - heavy prompting needed 
        if any(size in model_lower for size in ['1.7b', '1b', '2b']):
            return 'small'
        
        # Medium models (3-10B) - balanced approach
        if any(size in model_lower for size in ['3b', '4b', '7b', '8b']):
            return 'medium'
        
        # Default to medium for unknown models
        return 'medium'
    
    def detect_change_context(self, changes: str, diff: str) -> str:
        """Provide smart context hints for medium/small models based on actual changes."""
        hints = []
        
        # Format detection - spacing, indentation changes
        if self._is_formatting_change(diff):
            hints.append("🎨 Spacing/formatting detected → use 'style' NOT 'fix'")
        
        # Dependency update detection
        if self._is_dependency_change(changes):
            hints.append("🧹 Dependencies detected → use 'chore' NOT 'fix'")
        
        # Performance optimization detection
        if self._is_performance_change(diff):
            hints.append("⚡ Performance optimization → use 'perf' NOT 'refactor'")
        
        # Large refactor detection
        if self._is_large_refactor(changes):
            hints.append("🏗️ Multiple files changed → likely 'refactor' NOT 'fix'")
        
        return "\n".join(hints) if hints else ""
    
    def _is_formatting_change(self, diff: str) -> bool:
        """Detect if changes are formatting-related."""
        import re
        
        # Look for spacing pattern changes
        spacing_patterns = [
            r'[<>=!]\s*→\s*[<>=!]\s+',  # a<b → a < b, a=b → a = b
            r'^\+.*\s+$',               # Lines with added trailing spaces
            r'^\-\s*\+\s*',             # Indentation changes
        ]
        
        # Check for common formatting indicators
        formatting_indicators = [
            ' < ', ' > ', ' = ', ' + ', ' - ',  # Operator spacing
            'spacing', 'indentation', 'format',
        ]
        
        # Pattern-based detection
        for pattern in spacing_patterns:
            if re.search(pattern, diff, re.MULTILINE):
                return True
        
        # Content-based detection
        for indicator in formatting_indicators:
            if indicator in diff.lower():
                return True
        
        return False
    
    def _is_dependency_change(self, changes: str) -> bool:
        """Detect if changes involve dependency files."""
        dep_files = [
            'requirements.txt', 'package.json', 'package-lock.json',
            'yarn.lock', 'Pipfile', 'Pipfile.lock', 'setup.py',
            'pyproject.toml', 'Cargo.toml', 'Cargo.lock',
            '.yml', '.yaml', 'docker', 'Dockerfile'
        ]
        
        changes_lower = changes.lower()
        return any(dep_file in changes_lower for dep_file in dep_files)
    
    def _is_performance_change(self, diff: str) -> bool:
        """Detect if changes are performance-related."""
        diff_lower = diff.lower()
        
        # Specific pattern: loop elimination for database queries
        loop_to_query_patterns = [
            'for post in' in diff_lower and 'append' in diff_lower,
            'for item in' in diff_lower and 'list(' in diff_lower,
            ('posts = []' in diff_lower and 'return list(' in diff_lower),
            ('select_related' in diff_lower or 'prefetch_related' in diff_lower)
        ]
        
        if any(loop_to_query_patterns):
            return True
            
        # General performance keywords
        perf_keywords = [
            'optimize', 'optimization', 'cache', 'caching', 'performance',
            'speed', 'faster', 'efficient', 'inefficient', 'query performance'
        ]
        
        return any(keyword in diff_lower for keyword in perf_keywords)
    
    def _is_large_refactor(self, changes: str) -> bool:
        """Detect if changes involve large refactoring."""
        # Count number of files changed
        file_count = len([line for line in changes.split('\n') if line.strip()])
        
        # Large refactor indicators
        refactor_keywords = [
            'restructure', 'refactor', 'reorganize', 'split',
            'architecture', 'modular', 'separate'
        ]
        
        changes_lower = changes.lower()
        has_refactor_keywords = any(keyword in changes_lower for keyword in refactor_keywords)
        
        # Consider it a large refactor if multiple files OR refactor keywords
        return file_count >= 3 or has_refactor_keywords
    
    def load_prompt_template(self, filename: str) -> str:
        """Load prompt template from external file."""
        try:
            # Try to load from prompts directory next to the script
            script_dir = Path(__file__).parent
            prompt_file = script_dir / "prompts" / filename
            
            if prompt_file.exists():
                return prompt_file.read_text().strip()
            
            # Fallback: try from user config directory  
            config_prompts_dir = self.config.config_dir / "prompts"
            prompt_file = config_prompts_dir / filename
            
            if prompt_file.exists():
                return prompt_file.read_text().strip()
            
            # Try from installed location (for installed versions)
            installed_prompts_dir = Path.home() / "git-commit-ai" / "prompts"
            prompt_file = installed_prompts_dir / filename
            
            if prompt_file.exists():
                return prompt_file.read_text().strip()
            
            # If no external file found, return empty string
            return ""
            
        except Exception as e:
            self.debug_log(f"Warning: Could not load prompt template {filename}: {e}")
            return ""
    
    def build_ollama_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> Dict:
        """Build request for Ollama provider with adaptive prompting strategy."""
        
        model_tier = self.get_model_tier()
        
        # Load instructions from external files (no fallbacks - use files only)
        instructions = self.load_prompt_template(f"{model_tier}_model.txt")
        if not instructions:
            raise FileNotFoundError(f"Required prompt template '{model_tier}_model.txt' not found")
        
        # 🔥 Smart enhancement ONLY for medium/small models
        if model_tier in ['medium', 'small']:
            # Add intelligent context hints based on actual changes
            smart_hints = self.detect_change_context(changes, diff)
            if smart_hints:
                instructions += f"\n\n🎯 SMART CONTEXT HINTS:\n{smart_hints}"
            
            # Add final check for medium and small models
            final_check_template = self.load_prompt_template("final_check.txt")
            if final_check_template:
                instructions += f"\n\n{final_check_template}"
        
        # Load base prompt template
        base_template = self.load_prompt_template("ollama_base.txt")
        if not base_template:
            raise FileNotFoundError("Required prompt template 'ollama_base.txt' not found")
        
        # Build diff section based on whether to use diff content
        if use_diff:
            diff_section = f"""## Diff:
<diff>
{diff}
</diff>"""
        else:
            diff_section = f"""## File statistics:
<file_stats>
{detailed_changes}
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only."""
        
        # Format the prompt using the template
        prompt = base_template.format(
            changes=changes,
            diff_section=diff_section,
            instructions=instructions,
            final_check=""  # final_check is now handled within instructions
        )
        
        return {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.8
            }
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
