#!/usr/bin/env python3
"""
Test cases for git commit message generation with different change types.
These simulate various git diff scenarios to test prompt optimization.
"""

class TestCase:
    def __init__(self, name, description, changes, diff, expected_type, expected_scope=None):
        self.name = name
        self.description = description
        self.changes = changes
        self.diff = diff
        self.expected_type = expected_type
        self.expected_scope = expected_scope

# Test cases for different commit types
TEST_CASES = [
    TestCase(
        name="simple_fix",
        description="Simple bug fix in existing function",
        changes="M\tsrc/utils.py",
        diff="""--- a/src/utils.py
+++ b/src/utils.py
@@ -10,7 +10,7 @@ def validate_email(email):
     if not email:
         return False
-    return "@" in email
+    return "@" in email and "." in email
     
 def format_date(date):""",
        expected_type="fix",
        expected_scope="utils"
    ),
    
    TestCase(
        name="new_feature",
        description="Adding new authentication feature",
        changes="A\tsrc/auth/oauth.py\nM\tsrc/auth/__init__.py",
        diff="""--- /dev/null
+++ b/src/auth/oauth.py
@@ -0,0 +1,25 @@
+import requests
+
+class OAuthManager:
+    def __init__(self, client_id, client_secret):
+        self.client_id = client_id
+        self.client_secret = client_secret
+    
+    def get_access_token(self, code):
+        data = {
+            'client_id': self.client_id,
+            'client_secret': self.client_secret,
+            'code': code,
+            'grant_type': 'authorization_code'
+        }
+        response = requests.post('/oauth/token', data=data)
+        return response.json()['access_token']
+
--- a/src/auth/__init__.py
+++ b/src/auth/__init__.py
@@ -1,2 +1,3 @@
 from .login import LoginManager
+from .oauth import OAuthManager""",
        expected_type="feat",
        expected_scope="auth"
    ),
    
    TestCase(
        name="documentation_update",
        description="Update README with installation instructions",
        changes="M\tREADME.md",
        diff="""--- a/README.md
+++ b/README.md
@@ -15,6 +15,15 @@ AI-powered Git Commit Message Generator
 
 ## Installation
 
+### Using pip
+```bash
+pip install git-commit-ai
+```
+
+### From source
+```bash
+git clone https://github.com/user/repo.git
+cd repo
+pip install -e .
+```
+
 ## Usage""",
        expected_type="docs",
        expected_scope="readme"
    ),
    
    TestCase(
        name="refactor_large",
        description="Large refactoring of API structure",
        changes="M\tsrc/api/handlers.py\nM\tsrc/api/models.py\nM\tsrc/api/validators.py\nD\tsrc/api/legacy.py",
        diff="",  # Large diff, will use file stats
        expected_type="refactor",
        expected_scope="api"
    ),
    
    TestCase(
        name="style_formatting",
        description="Code formatting and style fixes",
        changes="M\tsrc/main.py\nM\tsrc/config.py",
        diff="""--- a/src/main.py
+++ b/src/main.py
@@ -5,8 +5,8 @@ import sys
 
 def main():
-    if len(sys.argv)<2:
-        print("Error: missing argument")
+    if len(sys.argv) < 2:
+        print("Error: missing argument")
         return
     
-    config=load_config()
+    config = load_config()""",
        expected_type="style",
        expected_scope=None
    ),
    
    TestCase(
        name="performance_optimization",
        description="Optimize database query performance",
        changes="M\tsrc/database/queries.py",
        diff="""--- a/src/database/queries.py
+++ b/src/database/queries.py
@@ -12,10 +12,8 @@ class UserQueries:
     def get_user_posts(self, user_id):
-        posts = []
-        for post in Post.objects.filter(user_id=user_id):
-            posts.append(post)
-        return posts
+        return list(Post.objects.filter(user_id=user_id).select_related('user'))""",
        expected_type="perf",
        expected_scope="database"
    ),
    
    TestCase(
        name="test_addition",
        description="Add unit tests for authentication module",
        changes="A\ttests/test_auth.py\nM\ttests/__init__.py",
        diff="""--- /dev/null
+++ b/tests/test_auth.py
@@ -0,0 +1,20 @@
+import unittest
+from src.auth import LoginManager
+
+class TestAuth(unittest.TestCase):
+    def setUp(self):
+        self.login_manager = LoginManager()
+    
+    def test_valid_login(self):
+        result = self.login_manager.authenticate("user", "pass")
+        self.assertTrue(result)
+    
+    def test_invalid_login(self):
+        result = self.login_manager.authenticate("", "")
+        self.assertFalse(result)""",
        expected_type="test",
        expected_scope="auth"
    ),
    
    TestCase(
        name="chore_dependencies",
        description="Update dependencies and build config",
        changes="M\trequirements.txt\nM\tsetup.py\nM\t.github/workflows/ci.yml",
        diff="""--- a/requirements.txt
+++ b/requirements.txt
@@ -1,5 +1,5 @@
-requests==2.28.0
+requests==2.31.0
-flask==2.0.1
+flask==2.3.3""",
        expected_type="chore",
        expected_scope=None
    ),
    
    TestCase(
        name="adaptive_prompting_feature",
        description="Major feature implementation: adaptive prompting strategies with external templates",
        changes="""M	README.md
M	git-commit.py
M	install.sh
A	prompts/final_check.txt
A	prompts/large_model.txt
A	prompts/medium_model.txt
A	prompts/ollama_base.txt
A	prompts/openrouter_system.txt
A	prompts/openrouter_user.txt
A	prompts/small_model.txt""",
        diff="""diff --git a/README.md b/README.md
index 9489430..aa1bf33 100644
--- a/README.md
+++ b/README.md
@@ -20,6 +20,7 @@ Your commit messages will look like this:
   - OpenRouter (default) using `google/gemini-flash-1.5-8b` - SUPER CHEAP!
     - Around $0.00001/commit -> $1 per 100K commit messages!
   - Custom API support - Bring your own provider!
+- 🧠 Adaptive prompting strategies based on model size (small/medium/large)
 - 📝 Follows [Conventional Commits](https://www.conventionalcommits.org/) format
 - 🔒 Secure local API key storage
 - 🚀 Automatic git commit and push
@@ -262,13 +263,6 @@ cmai --use-custom http://my-api.com
 cmai --use-custom http://my-api.com --model my-custom-model
 ```
 
-# Use a different model
-cmai --use-ollama --model qwen-coder:7b
-
-# Use Ollama with debug and push
-cmai --use-ollama --debug --push
-```
-
 ### Common Options
 ```bash
 # Commit and push
@@ -302,12 +296,8 @@ Example generated commit messages:
 │ └── git-commit.sh
 ├── .config/
 │ └── git-commit-ai/
-│   ├── config       # API key
-│   ├── model        # Selected AI model
-│   ├── provider     # Selected provider (openrouter/ollama/custom)
-│   └── base_url     # API base URL
-│   ├── model
-│   └── base_url
+│   ├── config.json  # Configuration (API keys, models, providers)
+│   └── providers/   # Provider-specific configurations
 └── usr/
   └── local/
     └── bin/
@@ -322,9 +312,8 @@ Example generated commit messages:
 │ └── cmai.sh
 └── .config/
   └── git-commit-ai/
-    ├── config
-    ├── model
-    └── base_url
+    ├── config.json
+    └── providers/
 ```
 
 ## Security
diff --git a/git-commit.py b/git-commit.py
index 52f9309..0f8810f 100755
--- a/git-commit.py
+++ b/git-commit.py
@@ -362,62 +362,36 @@ class GitCommitAI:
     
     def build_openrouter_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> Dict:
         \"\"\"Build request for OpenRouter/Custom providers.\"\"\"
-        system_message = \"You are a git commit message generator. Create conventional commit messages.\"
         
+        # Load system message from external file (no fallback)
+        system_message = self.load_prompt_template(\"openrouter_system.txt\")
+        if not system_message:
+            raise FileNotFoundError(\"Required prompt template 'openrouter_system.txt' not found\")
+        
+        # Load user message template from external file (no fallback)
+        user_template = self.load_prompt_template(\"openrouter_user.txt\")
+        if not user_template:
+            raise FileNotFoundError(\"Required prompt template 'openrouter_user.txt' not found\")
+        
+        # Build diff section based on whether to use diff content
         if use_diff:
-            user_content = f\"\"\"Generate a commit message for these changes:
-
-## File changes:
-<file_changes>
-{changes}
-</file_changes>
-
-## Diff:
+            diff_section = f\"\"\"## Diff:
 <diff>
 {diff}
-</diff>
-
-## Format:
-<type>(<scope>): <subject>
-
-<body>
-
-Important:
-- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
-- Subject: max 70 characters, imperative mood, no period
-- Body: list changes to explain what and why, not how
-- Scope: max 3 words
-- For minor changes: use 'fix' instead of 'feat'
-- Do not wrap your response in triple backticks
-- Response should be the commit message only, no explanations.\"\"\"
+</diff>\"\"\"
         else:
-            user_content = f\"\"\"Generate a commit message for these changes:
-
-## File changes:
-<file_changes>
-{changes}
-</file_changes>
-
-## File statistics:
+            diff_section = f\"\"\"## File statistics:
 <file_stats>
 {detailed_changes}
 </file_stats>
 
-Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.
-
-## Format:
-<type>(<scope>): <subject>
-
-<body>
-
-Important:
-- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
-- Subject: max 70 characters, imperative mood, no period
-- Body: list changes to explain what and why, not how
-- Scope: max 3 words
-- For minor changes: use 'fix' instead of 'feat'
-- Do not wrap your response in triple backticks
-- Response should be the commit message only, no explanations.\"\"\"
+Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.\"\"\"
+        
+        # Format the user content using the template
+        user_content = user_template.format(
+            changes=changes,
+            diff_section=diff_section
+        )
         
         return {
             \"model\": self.model,
@@ -428,54 +402,109 @@ Important:
             ]
         }
     
+    def get_model_tier(self) -> str:
+        \"\"\"Determine model tier based on model name for adaptive prompting.\"\"\"
+        model_lower = self.model.lower()
+        
+        # Large models (30B+) - minimal prompting needed
+        if any(size in model_lower for size in ['32b', '30b', '70b', '72b']):
+            return 'large'
+        
+        # Small models (≤2B) - heavy prompting needed 
+        if any(size in model_lower for size in ['1.7b', '1b', '2b']):
+            return 'small'
+        
+        # Medium models (3-10B) - balanced approach
+        if any(size in model_lower for size in ['3b', '4b', '7b', '8b']):
+            return 'medium'
+        
+        # Default to medium for unknown models
+        return 'medium'
+    
+    def load_prompt_template(self, filename: str) -> str:
+        \"\"\"Load prompt template from external file.\"\"\"
+        try:
+            # Try to load from prompts directory next to the script
+            script_dir = Path(__file__).parent
+            prompt_file = script_dir / \"prompts\" / filename
+            
+            if prompt_file.exists():
+                return prompt_file.read_text().strip()
+            
+            # Fallback: try from user config directory  
+            config_prompts_dir = self.config.config_dir / \"prompts\"
+            prompt_file = config_prompts_dir / filename
+            
+            if prompt_file.exists():
+                return prompt_file.read_text().strip()
+            
+            # Try from installed location (for installed versions)
+            installed_prompts_dir = Path.home() / \"git-commit-ai\" / \"prompts\"
+            prompt_file = installed_prompts_dir / filename
+            
+            if prompt_file.exists():
+                return prompt_file.read_text().strip()
+            
+            # If no external file found, return empty string
+            return \"\"
+            
+        except Exception as e:
+            self.debug_log(f\"Warning: Could not load prompt template {filename}: {e}\")
+            return \"\"
+    
     def build_ollama_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> Dict:
-        \"\"\"Build request for Ollama provider.\"\"\"
-        common_instructions = \"\"\"Follow the conventional commits format: <type>(<scope>): <subject>
-
-<body>
-
-Where type is one of: feat, fix, docs, style, refactor, perf, test, chore.
-- Scope: max 3 words.
-- Keep the subject under 70 chars.
-- Body: list changes to explain what and why
-- Use 'fix' for minor changes
-- Do not wrap your response in triple backticks
-- Response should be the commit message only, no explanations.\"\"\"
+        \"\"\"Build request for Ollama provider with adaptive prompting strategy.\"\"\"
+        
+        model_tier = self.get_model_tier()
         
+        # Load instructions from external files (no fallbacks - use files only)
+        instructions = self.load_prompt_template(f\"{model_tier}_model.txt\")
+        if not instructions:
+            raise FileNotFoundError(f\"Required prompt template '{model_tier}_model.txt' not found\")
+        
+        # Add final check for medium and small models
+        final_check = \"\"
+        if model_tier in ['medium', 'small']:
+            final_check_template = self.load_prompt_template(\"final_check.txt\")
+            if final_check_template:
+                final_check = f\"\\n\\n{final_check_template}\"
+        
+        # Load base prompt template
+        base_template = self.load_prompt_template(\"ollama_base.txt\")
+        if not base_template:
+            raise FileNotFoundError(\"Required prompt template 'ollama_base.txt' not found\")
+        
+        # Build diff section based on whether to use diff content
         if use_diff:
-            prompt = f\"\"\"Generate a conventional commit message for these changes: 
-<file_changes>
-{changes}
-</file_changes>
-
-## Diff:
+            diff_section = f\"\"\"## Diff:
 <diff>
 {diff}
-</diff>
-
-## Instructions:
-{common_instructions}\"\"\"
+</diff>\"\"\"
         else:
-            prompt = f\"\"\"Generate a conventional commit message for these changes: 
-<file_changes>
-{changes}
-</file_changes>
-
-## File statistics:
+            diff_section = f\"\"\"## File statistics:
 <file_stats>
 {detailed_changes}
 </file_stats>
 
-Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.
-
-## Instructions:
-{common_instructions}\"\"\"
+Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.\"\"\"
+        
+        # Format the prompt using the template
+        prompt = base_template.format(
+            changes=changes,
+            diff_section=diff_section,
+            instructions=instructions,
+            final_check=final_check
+        )
         
         return {
             \"model\": self.model,
             \"prompt\": prompt,
+            \"stream\": False,
             \"think\": False,
-            \"stream\": False
+            \"options\": {
+                \"temperature\": 0.2,
+                \"top_p\": 0.8
+            }
         }
     
     def make_api_request(self, changes: str, diff: str, use_diff: bool, detailed_changes: str) -> str:
diff --git a/install.sh b/install.sh
index e14c344..9661cd0 100755
--- a/install.sh
+++ b/install.sh
@@ -87,6 +87,12 @@ if [ ! -f \"$SOURCE_SCRIPT\" ]; then
     exit 1
 fi
 
+# Check for prompts directory if installing Python version
+SOURCE_PROMPTS_DIR=\"$(dirname \"$0\")/prompts\"
+if [ \"$VERSION\" = \"py\" ] && [ ! -d \"$SOURCE_PROMPTS_DIR\" ]; then
+    echo \"Warning: prompts directory not found. Python version may use fallback prompts.\"
+fi
+
 echo \"Installing $SCRIPT_TYPE version of git-commit-ai...\"
 
 # Create directory for the script
@@ -98,6 +104,12 @@ debug_log \"Copying $SCRIPT_TYPE git-commit script\"
 cp \"$SOURCE_SCRIPT\" \"$SCRIPT_DIR/$SCRIPT_NAME\"
 chmod +x \"$SCRIPT_DIR/$SCRIPT_NAME\"
 
+# Copy prompts directory if it exists and we're installing Python version
+if [ \"$VERSION\" = \"py\" ] && [ -d \"$SOURCE_PROMPTS_DIR\" ]; then
+    debug_log \"Copying prompts directory\"
+    cp -r \"$SOURCE_PROMPTS_DIR\" \"$SCRIPT_DIR/\"
+fi
+
 # Handle executable installation
 if [ \"$OS\" = \"windows\" ]; then
     # On Windows, we rely on PATH""",
        expected_type="feat",
       expected_scope="prompts"
    )
]

def get_test_case(name):
    """Get a specific test case by name."""
    for case in TEST_CASES:
        if case.name == name:
            return case
    return None

def list_test_cases():
    """List all available test cases."""
    print("Available test cases:")
    for case in TEST_CASES:
        print(f"  {case.name}: {case.description}")

if __name__ == "__main__":
    list_test_cases()