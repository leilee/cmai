#!/usr/bin/env python3
"""
Automated batch testing system for git commit message generation.
Tests multiple scenarios and generates detailed analysis reports.
"""

import sys
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_cases import TEST_CASES
import importlib.util
spec = importlib.util.spec_from_file_location("git_commit", Path(__file__).parent.parent / "git-commit.py")
git_commit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_commit)

class TestResult:
    def __init__(self, test_case, generated_message, expected_type, expected_scope=None):
        self.test_case = test_case
        self.generated_message = generated_message
        self.expected_type = expected_type
        self.expected_scope = expected_scope
        self.analysis = self._analyze()
    
    def _analyze(self):
        """Analyze the generated commit message."""
        lines = self.generated_message.strip().split('\n')
        if not lines:
            return {
                'has_format': False,
                'type_correct': False,
                'scope_extracted': None,
                'scope_correct': False,
                'subject_length': 0,
                'has_body': False,
                'issues': ['Empty message']
            }
        
        first_line = lines[0].strip()
        
        # Parse conventional commit format: type(scope): subject
        pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(pattern, first_line)
        
        issues = []
        
        if match:
            actual_type, actual_scope, subject = match.groups()
            has_format = True
            
            # Check type correctness
            valid_types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]
            type_correct = actual_type in valid_types and actual_type == self.expected_type
            
            if actual_type not in valid_types:
                issues.append(f"Invalid type: {actual_type}")
            elif actual_type != self.expected_type:
                issues.append(f"Wrong type: got {actual_type}, expected {self.expected_type}")
            
            # Check scope
            scope_correct = True
            if self.expected_scope and actual_scope != self.expected_scope:
                scope_correct = False
                issues.append(f"Wrong scope: got {actual_scope}, expected {self.expected_scope}")
            
            # Check subject length
            subject_length = len(subject)
            if subject_length > 60:
                issues.append(f"Subject too long: {subject_length} chars")
            
            # Check if subject ends with period
            if subject.endswith('.'):
                issues.append("Subject should not end with period")
            
        else:
            has_format = False
            actual_type = None
            actual_scope = None
            subject = first_line
            subject_length = len(subject)
            type_correct = False
            scope_correct = False
            issues.append("Missing conventional commit format")
        
        # Check body
        has_body = len(lines) > 1 and any(line.strip() for line in lines[1:])
        
        return {
            'has_format': has_format,
            'actual_type': actual_type,
            'actual_scope': actual_scope,
            'type_correct': type_correct,
            'scope_correct': scope_correct,
            'subject': subject,
            'subject_length': subject_length,
            'has_body': has_body,
            'issues': issues
        }

class AutoTester:
    def __init__(self, provider="ollama", model="qwen3:4b", test_rounds=3):
        self.provider = provider
        self.model = model
        self.test_rounds = test_rounds
        self.results = []
        
        # Set provider-specific configurations
        if provider == "ollama":
            self.base_url = "http://localhost:11434/api"
            self.api_key = None
        elif provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            # Try to get API key from config
            try:
                from pathlib import Path
                import json
                config_file = Path.home() / ".config" / "git-commit-ai" / "providers" / "openrouter.json"
                if config_file.exists():
                    with open(config_file) as f:
                        config = json.load(f)
                        self.api_key = config.get("api_key", "")
                else:
                    self.api_key = ""
            except:
                self.api_key = ""
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def run_all_tests(self):
        """Run all test cases multiple times and collect results."""
        print(f"🚀 Starting automated testing with {self.provider}:{self.model}")
        print(f"📊 Testing {len(TEST_CASES)} scenarios × {self.test_rounds} rounds = {len(TEST_CASES) * self.test_rounds} total tests")
        print("=" * 60)
        
        total_tests = 0
        failed_tests = 0
        
        for round_num in range(1, self.test_rounds + 1):
            print(f"\n🔄 Round {round_num}/{self.test_rounds}")
            
            for i, test_case in enumerate(TEST_CASES, 1):
                print(f"  [{i:2d}/{len(TEST_CASES)}] {test_case.name}...", end=" ")
                
                try:
                    # Generate commit message
                    generated = self._generate_commit_message(test_case)
                    
                    # Analyze result
                    result = TestResult(
                        test_case, 
                        generated, 
                        test_case.expected_type, 
                        test_case.expected_scope
                    )
                    
                    result.round = round_num
                    self.results.append(result)
                    
                    # Show quick status
                    if result.analysis['type_correct'] and result.analysis['has_format']:
                        print("✅")
                    else:
                        print("❌")
                        failed_tests += 1
                    
                    total_tests += 1
                    
                    # Small delay to avoid overwhelming the API
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"💥 Error: {e}")
                    failed_tests += 1
                    total_tests += 1
        
        print(f"\n📈 Testing completed: {total_tests - failed_tests}/{total_tests} passed")
        return self.results
    
    def _generate_commit_message(self, test_case):
        """Generate commit message for a test case."""
        # Determine if we should use diff content
        use_diff = bool(test_case.diff.strip())
        detailed_changes = "" if use_diff else "Files changed: " + test_case.changes
        
        # Build request based on provider
        if self.provider == "ollama":
            request_data = self._build_ollama_request(test_case.changes, test_case.diff, use_diff, detailed_changes)
            url = f"{self.base_url}/generate"
            headers = {"Content-Type": "application/json"}
        elif self.provider == "openrouter":
            request_data = self._build_openrouter_request(test_case.changes, test_case.diff, use_diff, detailed_changes)
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/mrgoonie/cmai",
                "X-Title": "cmai - AI Commit Message Generator"
            }
        else:
            raise Exception(f"Unsupported provider: {self.provider}")
        
        # Make API request
        data = json.dumps(request_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_text = response.read().decode('utf-8')
        
        # Extract message based on provider
        response_data = json.loads(response_text)
        
        if self.provider == "ollama":
            commit_message = response_data.get("response", "")
            if not commit_message:
                raise Exception("Empty response from Ollama")
        elif self.provider == "openrouter":
            try:
                commit_message = response_data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                raise Exception(f"Failed to parse OpenRouter response: {response_data}")
        
        return commit_message.replace('\\n', '\n').replace('\\r', '').strip()
    
    def _build_ollama_request(self, changes, diff, use_diff, detailed_changes):
        """Build Ollama request using the new external template system."""
        # Create a temporary GitCommitAI instance to access the template system
        temp_app = git_commit.GitCommitAI()
        temp_app.model = self.model
        temp_app.provider = "ollama"
        
        try:
            # Use the real template system from git-commit.py
            return temp_app.build_ollama_request(changes, diff, use_diff, detailed_changes)
        except Exception as e:
            # Fallback to a simple request if template loading fails
            print(f"Warning: Template loading failed, using fallback: {e}")
            return {
                "model": self.model,
                "prompt": f"Generate a conventional commit message for: {changes}",
                "stream": False,
                "think": False,
                "options": {"temperature": 0.2, "top_p": 0.8}
            }
    
    def _build_openrouter_request(self, changes, diff, use_diff, detailed_changes):
        """Build OpenRouter request using the new external template system."""
        # Create a temporary GitCommitAI instance to access the template system
        temp_app = git_commit.GitCommitAI()
        temp_app.model = self.model
        temp_app.provider = "openrouter"
        
        try:
            # Use the real template system from git-commit.py
            return temp_app.build_openrouter_request(changes, diff, use_diff, detailed_changes)
        except Exception as e:
            # Fallback to a simple request if template loading fails
            print(f"Warning: Template loading failed, using fallback: {e}")
            return {
                "model": self.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": "You are a git commit message generator."},
                    {"role": "user", "content": f"Generate a conventional commit message for: {changes}"}
                ]
            }
    
    def generate_report(self):
        """Generate detailed analysis report."""
        if not self.results:
            print("No test results to analyze.")
            return
        
        # Calculate statistics
        total_tests = len(self.results)
        format_correct = sum(1 for r in self.results if r.analysis['has_format'])
        type_correct = sum(1 for r in self.results if r.analysis['type_correct'])
        both_correct = sum(1 for r in self.results if r.analysis['has_format'] and r.analysis['type_correct'])
        
        # Group by test case for consistency analysis
        by_test_case = {}
        for result in self.results:
            case_name = result.test_case.name
            if case_name not in by_test_case:
                by_test_case[case_name] = []
            by_test_case[case_name].append(result)
        
        # Generate report
        report = f"""
🤖 Automated Commit Message Generation Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: {self.provider}:{self.model}
Test Rounds: {self.test_rounds}

📊 OVERALL STATISTICS
==================
Total Tests: {total_tests}
Format Correct: {format_correct}/{total_tests} ({format_correct/total_tests*100:.1f}%)
Type Correct: {type_correct}/{total_tests} ({type_correct/total_tests*100:.1f}%)
Both Correct: {both_correct}/{total_tests} ({both_correct/total_tests*100:.1f}%)

🔍 DETAILED ANALYSIS BY SCENARIO
=============================="""

        for case_name, case_results in by_test_case.items():
            case = case_results[0].test_case
            correct_count = sum(1 for r in case_results if r.analysis['type_correct'] and r.analysis['has_format'])
            consistency = correct_count / len(case_results) * 100
            
            report += f"""
{case_name.upper().replace('_', ' ')}
Expected: {case.expected_type}({case.expected_scope or 'any'})
Consistency: {correct_count}/{len(case_results)} ({consistency:.1f}%)
"""
            
            for i, result in enumerate(case_results, 1):
                analysis = result.analysis
                status = "✅" if analysis['type_correct'] and analysis['has_format'] else "❌"
                
                if analysis['has_format']:
                    actual = f"{analysis['actual_type']}({analysis['actual_scope'] or '?'}): {analysis['subject'][:30]}..."
                else:
                    actual = f"No format: {analysis['subject'][:40]}..."
                
                report += f"  Round {i}: {status} {actual}\n"
                
                if analysis['issues']:
                    report += f"           Issues: {', '.join(analysis['issues'])}\n"

        report += f"""

🎯 COMMON ISSUES
=============="""
        
        # Analyze common issues
        all_issues = []
        for result in self.results:
            all_issues.extend(result.analysis['issues'])
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_tests * 100
            report += f"\n• {issue}: {count} times ({percentage:.1f}%)"

        report += f"""

💡 RECOMMENDATIONS
================"""
        
        if format_correct / total_tests < 0.8:
            report += "\n• 🚨 Format compliance is low - consider stronger format enforcement"
        
        if type_correct / total_tests < 0.7:
            report += "\n• 🎯 Type detection accuracy needs improvement - review examples and rules"
        
        # Find least consistent scenarios
        inconsistent_cases = []
        for case_name, case_results in by_test_case.items():
            correct_count = sum(1 for r in case_results if r.analysis['type_correct'] and r.analysis['has_format'])
            consistency = correct_count / len(case_results)
            if consistency < 0.8:
                inconsistent_cases.append((case_name, consistency))
        
        if inconsistent_cases:
            report += "\n• 🔄 Focus on improving consistency for:"
            for case_name, consistency in sorted(inconsistent_cases, key=lambda x: x[1]):
                report += f"\n  - {case_name}: {consistency*100:.1f}% consistent"

        return report

def run_multi_model_comparison(model_specs, rounds=2):
    """Run comparison tests across multiple models.
    
    Args:
        model_specs: List of model specifications, either:
                    - "model_name" (defaults to ollama)  
                    - "provider:model_name"
    """
    all_results = {}
    
    print(f"🚀 Multi-Model Comparison Test")
    print(f"📊 Models: {', '.join(model_specs)}")
    print(f"🔄 Rounds per model: {rounds}")
    print("=" * 60)
    
    for model_spec in model_specs:
        # Parse provider and model
        if ":" in model_spec and not model_spec.startswith("qwen"):
            # Handle provider:model format (but not qwen:version)
            provider, model = model_spec.split(":", 1)
        else:
            # Default to ollama for simple model names
            provider, model = "ollama", model_spec
        
        print(f"\n🤖 Testing model: {provider}:{model}")
        print("-" * 40)
        
        tester = AutoTester(provider=provider, model=model, test_rounds=rounds)
        try:
            results = tester.run_all_tests()
            all_results[f"{provider}:{model}"] = {
                'tester': tester,
                'results': results
            }
        except Exception as e:
            print(f"💥 Model {provider}:{model} failed: {e}")
            all_results[f"{provider}:{model}"] = None
    
    # Generate comparison report
    comparison_report = generate_comparison_report(all_results, rounds)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path(__file__).parent / f"multi_model_comparison_{timestamp}.txt"
    report_file.write_text(comparison_report)
    
    print(comparison_report)
    print(f"\n📋 Comparison report saved to: {report_file}")

def generate_comparison_report(all_results, rounds):
    """Generate cross-model comparison report."""
    valid_results = {k: v for k, v in all_results.items() if v is not None}
    
    if not valid_results:
        return "❌ No valid results to compare"
    
    report = f"""
🤖 Multi-Model Commit Message Generation Comparison
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Rounds per Model: {rounds}

📊 CROSS-MODEL PERFORMANCE SUMMARY
================================="""
    
    # Calculate stats for each model
    model_stats = {}
    for model, data in valid_results.items():
        results = data['results']
        total_tests = len(results)
        format_correct = sum(1 for r in results if r.analysis['has_format'])
        type_correct = sum(1 for r in results if r.analysis['type_correct'])
        both_correct = sum(1 for r in results if r.analysis['has_format'] and r.analysis['type_correct'])
        
        model_stats[model] = {
            'total': total_tests,
            'format_rate': format_correct / total_tests * 100,
            'type_rate': type_correct / total_tests * 100,
            'overall_rate': both_correct / total_tests * 100
        }
    
    # Performance comparison table
    report += f"\n\nModel               | Format | Type  | Overall"
    report += f"\n--------------------|--------|-------|--------"
    
    for model, stats in model_stats.items():
        report += f"\n{model:<19} | {stats['format_rate']:5.1f}% | {stats['type_rate']:4.1f}% | {stats['overall_rate']:6.1f}%"
    
    # Find best performing model
    best_model = max(model_stats.keys(), key=lambda m: model_stats[m]['overall_rate'])
    report += f"\n\n🏆 Best Overall: {best_model} ({model_stats[best_model]['overall_rate']:.1f}%)"
    
    # Detailed scenario analysis
    report += f"\n\n🔍 SCENARIO-BY-SCENARIO BREAKDOWN"
    report += f"\n================================="
    
    # Group results by test case
    scenarios = {}
    for model, data in valid_results.items():
        for result in data['results']:
            scenario = result.test_case.name
            if scenario not in scenarios:
                scenarios[scenario] = {}
            if model not in scenarios[scenario]:
                scenarios[scenario][model] = []
            scenarios[scenario][model].append(result)
    
    for scenario, model_results in scenarios.items():
        case = next(iter(model_results.values()))[0].test_case
        report += f"\n\n{scenario.upper().replace('_', ' ')}"
        report += f"\nExpected: {case.expected_type}({case.expected_scope or 'any'})"
        
        for model, results in model_results.items():
            correct_count = sum(1 for r in results if r.analysis['type_correct'] and r.analysis['has_format'])
            consistency = correct_count / len(results) * 100
            
            # Show sample result
            sample = results[0]
            if sample.analysis['has_format']:
                sample_text = f"{sample.analysis['actual_type']}({sample.analysis['actual_scope'] or '?'})"
                status = "✅" if sample.analysis['type_correct'] else "❌"
            else:
                sample_text = "No format"
                status = "❌"
            
            report += f"\n  {model:<15}: {consistency:5.1f}% {status} {sample_text}"
    
    # Common issues analysis
    report += f"\n\n🎯 CROSS-MODEL ISSUE PATTERNS"
    report += f"\n============================"
    
    all_issues = {}
    for model, data in valid_results.items():
        model_issues = []
        for result in data['results']:
            model_issues.extend(result.analysis['issues'])
        
        issue_counts = {}
        for issue in model_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        all_issues[model] = issue_counts
    
    # Find common issues across models
    common_issues = set()
    for model_issues in all_issues.values():
        common_issues.update(model_issues.keys())
    
    for issue in sorted(common_issues):
        issue_line = f"\n• {issue}:"
        for model in valid_results.keys():
            count = all_issues[model].get(issue, 0)
            if count > 0:
                issue_line += f" {model}({count})"
        if len([m for m in valid_results.keys() if all_issues[m].get(issue, 0) > 0]) > 1:
            report += issue_line
    
    # Recommendations
    report += f"\n\n💡 CROSS-MODEL INSIGHTS"
    report += f"\n======================"
    
    # Check if optimization is model-specific
    type_rates = [stats['type_rate'] for stats in model_stats.values()]
    if max(type_rates) - min(type_rates) > 20:
        report += f"\n• 🚨 Large performance gap ({max(type_rates):.1f}% - {min(type_rates):.1f}%) suggests model-specific overfitting"
    
    # Check format consistency
    format_rates = [stats['format_rate'] for stats in model_stats.values()]
    if min(format_rates) > 90:
        report += f"\n• ✅ Format rules generalize well across models"
    
    # Model size vs performance analysis
    if len(model_stats) >= 2:
        report += f"\n• 📈 Consider model size vs accuracy tradeoff for deployment"
    
    return report

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python auto_tester.py [rounds]                           # Test single model (default: ollama:qwen3:4b)")
        print("  python auto_tester.py --provider PROVIDER --model MODEL [rounds]  # Test specific provider/model")
        print("  python auto_tester.py --multi model1,model2 [rounds]     # Test multiple models")
        print("")
        print("Options:")
        print("  --provider PROVIDER    Provider: ollama, openrouter (default: ollama)")
        print("  --model MODEL         Model name (default: qwen3:4b)")
        print("  rounds                Number of test rounds per scenario (default: 3)")
        print("")
        print("Examples:")
        print("  python auto_tester.py --provider ollama --model qwen3:4b 5")
        print("  python auto_tester.py --provider openrouter --model qwen/qwen-2.5-coder-32b-instruct:free 2")
        print("  python auto_tester.py --multi qwen3:4b,qwen2.5:3b,qwen3:1.7b")
        print("  python auto_tester.py --multi qwen3:4b,openrouter:qwen/qwen-2.5-coder-32b-instruct:free")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--multi":
        if len(sys.argv) < 3:
            print("Error: --multi requires model list")
            print("Example: python auto_tester.py --multi qwen3:4b,qwen2.5:3b,qwen3:1.7b")
            return
        
        model_specs = sys.argv[2].split(',')
        rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        run_multi_model_comparison(model_specs, rounds)
        return
    
    # Parse arguments for single model testing
    provider = "ollama"
    model = "qwen3:4b"
    rounds = 3
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
            provider = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        else:
            # Assume it's the rounds parameter
            try:
                rounds = int(sys.argv[i])
            except ValueError:
                print(f"Error: Invalid rounds parameter: {sys.argv[i]}")
                return
            i += 1
    
    tester = AutoTester(provider=provider, model=model, test_rounds=rounds)
    
    try:
        # Run tests
        results = tester.run_all_tests()
        
        # Generate and save report
        report = tester.generate_report()
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(__file__).parent / f"test_report_{timestamp}.txt"
        report_file.write_text(report)
        
        # Print summary
        print(report)
        print(f"\n📋 Full report saved to: {report_file}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Testing failed: {e}")

if __name__ == "__main__":
    main()