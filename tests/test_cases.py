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