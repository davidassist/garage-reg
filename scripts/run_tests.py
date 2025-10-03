#!/usr/bin/env python3
"""
GarageReg Test Runner Script
Comprehensive local testing with coverage reporting
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional
import json
import time
import webbrowser


class TestRunner:
    """Comprehensive test runner for GarageReg."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.frontend_dir = project_root / "web-admin-new"
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"🔧 Running: {' '.join(cmd)}")
        if cwd:
            print(f"   📁 Working directory: {cwd}")
            
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode != 0 and check:
            print(f"❌ Command failed with exit code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            sys.exit(1)
        
        return result
    
    def setup_backend_env(self):
        """Set up backend test environment."""
        print("🐍 Setting up backend test environment...")
        
        # Create test environment file
        test_env_file = self.backend_dir / ".env.test"
        test_env_content = """
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379
TESTING=true
SECRET_KEY=test-secret-key-for-local-testing-only
LOG_LEVEL=INFO
"""
        
        test_env_file.write_text(test_env_content.strip())
        print(f"✅ Created {test_env_file}")
        
        # Install test dependencies
        self.run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], cwd=self.backend_dir)
        
        self.run_command([
            sys.executable, "-m", "pip", "install", 
            "pytest-cov", "pytest-asyncio", "pytest-mock", "pytest-xdist",
            "black", "isort", "flake8", "mypy"
        ], cwd=self.backend_dir)
    
    def run_backend_linting(self) -> bool:
        """Run backend code linting and formatting checks."""
        print("🔍 Running backend linting...")
        
        success = True
        
        # Check formatting with black
        print("  📝 Checking code formatting with black...")
        result = self.run_command([
            "black", "--check", "--diff", "app/", "tests/"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode != 0:
            print("❌ Code formatting issues found. Run 'black app/ tests/' to fix.")
            success = False
        else:
            print("✅ Code formatting is correct")
        
        # Check imports with isort
        print("  📦 Checking import sorting with isort...")
        result = self.run_command([
            "isort", "--check-only", "--diff", "app/", "tests/"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode != 0:
            print("❌ Import sorting issues found. Run 'isort app/ tests/' to fix.")
            success = False
        else:
            print("✅ Import sorting is correct")
        
        # Check with flake8
        print("  🐛 Running flake8 linting...")
        result = self.run_command([
            "flake8", "app/", "tests/", 
            "--max-line-length=88", "--extend-ignore=E203,W503"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode != 0:
            print("❌ Linting issues found:")
            print(result.stdout)
            success = False
        else:
            print("✅ No linting issues found")
        
        return success
    
    def run_backend_unit_tests(self) -> bool:
        """Run backend unit tests."""
        print("🧪 Running backend unit tests...")
        
        result = self.run_command([
            "pytest", "tests/unit/",
            "-v",
            "--cov=app",
            "--cov-report=html:htmlcov/unit",
            "--cov-report=xml:coverage-unit.xml",
            "--cov-report=term-missing",
            "--junit-xml=test-results/unit-results.xml",
            "--maxfail=5",
            "--tb=short"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
            return True
        else:
            print("❌ Unit tests failed")
            print(result.stdout)
            return False
    
    def run_backend_integration_tests(self) -> bool:
        """Run backend integration tests."""
        print("🔗 Running backend integration tests...")
        
        result = self.run_command([
            "pytest", "tests/integration/",
            "-v",
            "--cov=app",
            "--cov-append",
            "--cov-report=html:htmlcov/integration",
            "--cov-report=xml:coverage-integration.xml",
            "--cov-report=term-missing",
            "--junit-xml=test-results/integration-results.xml",
            "--maxfail=5",
            "--tb=short"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode == 0:
            print("✅ Integration tests passed")
            return True
        else:
            print("❌ Integration tests failed")
            print(result.stdout)
            return False
    
    def run_backend_api_tests(self) -> bool:
        """Run backend API tests."""
        print("🌐 Running backend API tests...")
        
        result = self.run_command([
            "pytest", "tests/api/",
            "-v",
            "--cov=app",
            "--cov-append",
            "--cov-report=html:htmlcov/api",
            "--cov-report=xml:coverage-api.xml",
            "--cov-report=term-missing",
            "--junit-xml=test-results/api-results.xml",
            "--maxfail=5",
            "--tb=short"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode == 0:
            print("✅ API tests passed")
            return True
        else:
            print("❌ API tests failed")
            print(result.stdout)
            return False
    
    def generate_backend_coverage_report(self):
        """Generate comprehensive coverage report."""
        print("📊 Generating coverage report...")
        
        # Generate final HTML report
        self.run_command([
            "coverage", "html", "--directory=htmlcov/combined",
            "--title=GarageReg Backend Coverage Report"
        ], cwd=self.backend_dir)
        
        # Generate XML report
        self.run_command([
            "coverage", "xml", "-o", "coverage-combined.xml"
        ], cwd=self.backend_dir)
        
        # Generate terminal report
        result = self.run_command([
            "coverage", "report", "--show-missing"
        ], cwd=self.backend_dir, check=False)
        
        print("📈 Coverage Report:")
        print(result.stdout)
        
        # Check critical modules coverage
        coverage_file = self.backend_dir / "coverage-combined.xml"
        if coverage_file.exists():
            self._check_critical_modules_coverage(coverage_file)
    
    def _check_critical_modules_coverage(self, coverage_file: Path):
        """Check coverage for critical modules."""
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            critical_modules = [
                "app/core/auth.py",
                "app/core/security.py", 
                "app/services/data_export_import_service.py",
                "app/api/auth.py",
                "app/models/user.py",
                "app/models/organization.py"
            ]
            
            print("\n🎯 Critical Modules Coverage:")
            for package in root.findall(".//package"):
                for cls in package.findall("classes/class"):
                    filename = cls.get("filename", "")
                    if any(critical in filename for critical in critical_modules):
                        line_rate = float(cls.get("line-rate", 0)) * 100
                        status = "✅" if line_rate >= 90 else "❌"
                        print(f"  {status} {filename}: {line_rate:.1f}%")
        
        except Exception as e:
            print(f"⚠️ Could not parse coverage report: {e}")
    
    def setup_frontend_env(self):
        """Set up frontend test environment."""
        print("🟢 Setting up frontend test environment...")
        
        # Install dependencies
        self.run_command(["npm", "ci"], cwd=self.frontend_dir)
        
        # Install Playwright browsers
        self.run_command(["npx", "playwright", "install", "--with-deps"], cwd=self.frontend_dir)
    
    def run_frontend_e2e_tests(self) -> bool:
        """Run frontend E2E tests with Playwright."""
        print("🎭 Running frontend E2E tests...")
        
        # Start backend server in background if not running
        backend_proc = self._start_backend_server()
        
        try:
            # Wait for backend to be ready
            time.sleep(5)
            
            # Run Playwright tests
            result = self.run_command([
                "npx", "playwright", "test",
                "--reporter=html,junit,json",
                "--output-dir=test-results"
            ], cwd=self.frontend_dir, check=False)
            
            if result.returncode == 0:
                print("✅ E2E tests passed")
                return True
            else:
                print("❌ E2E tests failed")
                print(result.stdout)
                return False
        
        finally:
            if backend_proc:
                backend_proc.terminate()
                backend_proc.wait()
    
    def _start_backend_server(self) -> Optional[subprocess.Popen]:
        """Start backend server for E2E tests."""
        try:
            # Check if server is already running
            result = subprocess.run([
                "curl", "-s", "http://localhost:8000/health"
            ], capture_output=True, timeout=2)
            
            if result.returncode == 0:
                print("ℹ️ Backend server already running")
                return None
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("🚀 Starting backend server...")
        proc = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0", "--port", "8000"
        ], cwd=self.backend_dir)
        
        return proc
    
    def run_smoke_tests(self) -> bool:
        """Run smoke tests for critical functionality."""
        print("💨 Running smoke tests...")
        
        result = self.run_command([
            "pytest", "-m", "smoke",
            "--tb=short",
            "--maxfail=1",
            "--junit-xml=test-results/smoke-results.xml"
        ], cwd=self.backend_dir, check=False)
        
        if result.returncode == 0:
            print("✅ Smoke tests passed")
            return True
        else:
            print("❌ Smoke tests failed")
            return False
    
    def open_coverage_report(self):
        """Open coverage report in browser."""
        coverage_html = self.backend_dir / "htmlcov" / "combined" / "index.html"
        if coverage_html.exists():
            print(f"🌐 Opening coverage report: {coverage_html}")
            webbrowser.open(f"file://{coverage_html.absolute()}")
        else:
            print("❌ Coverage report not found")
    
    def open_e2e_report(self):
        """Open E2E test report in browser."""
        e2e_html = self.frontend_dir / "playwright-report" / "index.html"
        if e2e_html.exists():
            print(f"🌐 Opening E2E test report: {e2e_html}")
            webbrowser.open(f"file://{e2e_html.absolute()}")
        else:
            print("❌ E2E test report not found")
    
    def generate_test_summary(self, results: dict):
        """Generate comprehensive test summary."""
        print("\n" + "="*60)
        print("📋 TEST SUITE SUMMARY")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        print(f"Total test suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📊 Detailed Results:")
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        # Overall status
        all_passed = all(results.values())
        overall_status = "🟢 ALL TESTS PASSED" if all_passed else "🔴 SOME TESTS FAILED"
        print(f"\n🎯 Overall Status: {overall_status}")
        
        return all_passed


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="GarageReg Test Runner")
    parser.add_argument("--backend-only", action="store_true", help="Run only backend tests")
    parser.add_argument("--frontend-only", action="store_true", help="Run only frontend tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--smoke-only", action="store_true", help="Run only smoke tests")
    parser.add_argument("--no-lint", action="store_true", help="Skip linting")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--open-reports", action="store_true", help="Open test reports in browser")
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    # Look for backend and frontend directories
    while project_root.parent != project_root:
        if (project_root / "backend").exists() and (project_root / "web-admin-new").exists():
            break
        project_root = project_root.parent
    
    runner = TestRunner(project_root)
    results = {}
    
    print("🧪 Starting GarageReg Test Suite")
    print(f"📁 Project root: {project_root}")
    
    try:
        # Backend tests
        if not args.frontend_only:
            print("\n🐍 BACKEND TESTING")
            print("-" * 30)
            
            runner.setup_backend_env()
            
            if not args.no_lint:
                results["Backend Linting"] = runner.run_backend_linting()
            
            if args.unit_only or not (args.integration_only or args.smoke_only):
                results["Backend Unit Tests"] = runner.run_backend_unit_tests()
            
            if args.integration_only or not (args.unit_only or args.smoke_only):
                results["Backend Integration Tests"] = runner.run_backend_integration_tests()
                results["Backend API Tests"] = runner.run_backend_api_tests()
            
            if args.smoke_only or not (args.unit_only or args.integration_only):
                results["Smoke Tests"] = runner.run_smoke_tests()
            
            if not args.no_coverage:
                runner.generate_backend_coverage_report()
        
        # Frontend tests
        if not args.backend_only and not (args.unit_only or args.integration_only or args.smoke_only):
            print("\n🎭 FRONTEND TESTING")
            print("-" * 30)
            
            runner.setup_frontend_env()
            results["Frontend E2E Tests"] = runner.run_frontend_e2e_tests()
        
        # Generate summary
        all_passed = runner.generate_test_summary(results)
        
        # Open reports if requested
        if args.open_reports:
            runner.open_coverage_report()
            runner.open_e2e_report()
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test run failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()