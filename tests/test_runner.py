#!/usr/bin/env python3
"""
Test runner for git commit message generation.
Tests different optimizations against various change scenarios.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import git-commit.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_cases import TEST_CASES, get_test_case

# Import the GitCommitAI class directly
import importlib.util
spec = importlib.util.spec_from_file_location("git_commit", Path(__file__).parent.parent / "git-commit.py")
git_commit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_commit)

class MockGitCommitAI(git_commit.GitCommitAI):
    """Mock version of GitCommitAI for testing without actual git operations."""
    
    def __init__(self, provider="ollama", model="qwen3:4b"):
        # Initialize without calling parent __init__ to avoid config loading
        self.debug = True
        self.provider = provider
        self.model = model
        self.base_url = "http://localhost:11434/api"
    
    def test_prompt_generation(self, test_case):
        """Test prompt generation for a given test case."""
        print(f"\n=== Testing: {test_case.name} ===")
        print(f"Description: {test_case.description}")
        print(f"Expected type: {test_case.expected_type}")
        if test_case.expected_scope:
            print(f"Expected scope: {test_case.expected_scope}")
        
        # Determine if we should use diff content
        use_diff = bool(test_case.diff.strip())
        detailed_changes = "" if use_diff else "Files changed: " + test_case.changes
        
        # Generate the request
        if self.provider == "ollama":
            request_data = self.build_ollama_request(
                test_case.changes, 
                test_case.diff, 
                use_diff, 
                detailed_changes
            )
        else:
            request_data = self.build_openrouter_request(
                test_case.changes, 
                test_case.diff, 
                use_diff, 
                detailed_changes
            )
        
        # Print the generated prompt
        if self.provider == "ollama":
            print("\n--- Generated Ollama Prompt ---")
            print(request_data["prompt"])
        else:
            print("\n--- Generated OpenRouter Messages ---")
            for msg in request_data["messages"]:
                print(f"{msg['role'].upper()}:")
                print(msg["content"])
                print()
        
        print("-" * 50)
        return request_data

def run_test_case(test_case_name, provider="ollama"):
    """Run a specific test case."""
    test_case = get_test_case(test_case_name)
    if not test_case:
        print(f"Test case '{test_case_name}' not found.")
        return
    
    tester = MockGitCommitAI(provider=provider)
    tester.test_prompt_generation(test_case)

def run_all_tests(provider="ollama"):
    """Run all test cases."""
    print(f"Running all tests with provider: {provider}")
    
    tester = MockGitCommitAI(provider=provider)
    
    for test_case in TEST_CASES:
        tester.test_prompt_generation(test_case)
        input("Press Enter to continue to next test case...")

def compare_prompts(test_case_name, original_script, modified_script):
    """Compare prompts between original and modified versions."""
    # This would be used to compare before/after optimization
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_runner.py <test_case_name>     # Run specific test")
        print("  python test_runner.py all                  # Run all tests")
        print("  python test_runner.py list                 # List test cases")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        from test_cases import list_test_cases
        list_test_cases()
    elif command == "all":
        run_all_tests()
    else:
        run_test_case(command)