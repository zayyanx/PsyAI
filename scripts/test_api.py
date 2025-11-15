#!/usr/bin/env python3
"""
PsyAI Platform - API Testing Script

Comprehensive test script to validate all API endpoints.
Run this script after starting the API server to verify functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Test result container."""
    endpoint: str
    method: str
    passed: bool
    status_code: Optional[int]
    message: str
    duration_ms: float


class Colors:
    """Terminal colors for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    """API testing class."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: list[TestResult] = []
        self.token: Optional[str] = None
        self.session_id: Optional[int] = None
        
    def print_header(self, text: str):
        """Print test section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    def print_result(self, result: TestResult):
        """Print test result."""
        status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if result.passed else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
        print(f"{status} | {result.method:6s} {result.endpoint:40s} | {result.status_code or 'N/A':3} | {result.duration_ms:6.0f}ms | {result.message}")
    
    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        json_data: Optional[Dict] = None,
        form_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        description: str = "",
    ) -> TestResult:
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                if form_data:
                    response = requests.post(url, data=form_data, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=json_data, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=json_data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration_ms = (time.time() - start_time) * 1000
            
            passed = response.status_code == expected_status
            message = description or ("Success" if passed else f"Expected {expected_status}, got {response.status_code}")
            
            result = TestResult(
                endpoint=endpoint,
                method=method,
                passed=passed,
                status_code=response.status_code,
                message=message,
                duration_ms=duration_ms
            )
            
            self.results.append(result)
            self.print_result(result)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = TestResult(
                endpoint=endpoint,
                method=method,
                passed=False,
                status_code=None,
                message=f"Error: {str(e)}",
                duration_ms=duration_ms
            )
            self.results.append(result)
            self.print_result(result)
            return result
    
    def run_health_tests(self):
        """Test health endpoints."""
        self.print_header("Testing Health Endpoints")
        
        self.test_endpoint("GET", "/api/v1/health", description="Basic health check")
        self.test_endpoint("GET", "/api/v1/health/detailed", description="Detailed health check")
        self.test_endpoint("GET", "/api/v1/ping", description="Ping endpoint")
    
    def run_auth_tests(self):
        """Test authentication endpoints."""
        self.print_header("Testing Authentication Endpoints")
        
        # Register user
        result = self.test_endpoint(
            "POST",
            "/api/v1/auth/register",
            expected_status=201,
            json_data={
                "email": f"test_{int(time.time())}@example.com",
                "username": f"testuser_{int(time.time())}",
                "password": "TestPassword123!",
                "full_name": "Test User"
            },
            description="Register new user"
        )
        
        # Login with form data
        email = f"test_{int(time.time())}@example.com"
        password = "TestPassword123!"
        
        # First register the user
        requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": email,
                "username": f"user_{int(time.time())}",
                "password": password,
                "full_name": "Test User"
            }
        )
        
        # Then login
        result = self.test_endpoint(
            "POST",
            "/api/v1/auth/login",
            form_data={"username": email, "password": password},
            description="Login with form data"
        )
        
        # Extract token
        if result.passed:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data={"username": email, "password": password}
                )
                self.token = response.json()["access_token"]
                print(f"{Colors.GREEN}✓ Token obtained successfully{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}✗ Failed to obtain token: {e}{Colors.ENDC}")
        
        # Login with JSON
        self.test_endpoint(
            "POST",
            "/api/v1/auth/login/json",
            json_data={"email": email, "password": password},
            description="Login with JSON"
        )
        
        # Test login with wrong password
        self.test_endpoint(
            "POST",
            "/api/v1/auth/login",
            expected_status=401,
            form_data={"username": email, "password": "wrongpassword"},
            description="Login with wrong password (should fail)"
        )
    
    def run_user_tests(self):
        """Test user endpoints."""
        self.print_header("Testing User Endpoints")
        
        if not self.token:
            print(f"{Colors.YELLOW}⚠ Skipping user tests (no authentication token){Colors.ENDC}")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get current user
        self.test_endpoint(
            "GET",
            "/api/v1/users/me",
            headers=headers,
            description="Get current user info"
        )
        
        # Update current user
        self.test_endpoint(
            "PUT",
            "/api/v1/users/me",
            headers=headers,
            json_data={"full_name": "Updated Test User"},
            description="Update current user"
        )
        
        # Test unauthorized access
        self.test_endpoint(
            "GET",
            "/api/v1/users/me",
            expected_status=401,
            description="Get user without auth (should fail)"
        )
    
    def run_chat_tests(self):
        """Test chat endpoints."""
        self.print_header("Testing Chat Endpoints")
        
        if not self.token:
            print(f"{Colors.YELLOW}⚠ Skipping chat tests (no authentication token){Colors.ENDC}")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create chat session
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat/sessions",
                headers=headers,
                json={"mode": "ai", "title": "Test Session"}
            )
            if response.status_code == 201:
                self.session_id = response.json()["id"]
                print(f"{Colors.GREEN}✓ Chat session created (ID: {self.session_id}){Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to create chat session: {e}{Colors.ENDC}")
        
        self.test_endpoint(
            "POST",
            "/api/v1/chat/sessions",
            expected_status=201,
            headers=headers,
            json_data={"mode": "ai", "title": "Test Session"},
            description="Create chat session"
        )
        
        # List chat sessions
        self.test_endpoint(
            "GET",
            "/api/v1/chat/sessions",
            headers=headers,
            description="List chat sessions"
        )
        
        if self.session_id:
            # Get specific session
            self.test_endpoint(
                "GET",
                f"/api/v1/chat/sessions/{self.session_id}",
                headers=headers,
                description="Get specific session"
            )
            
            # Send message
            self.test_endpoint(
                "POST",
                f"/api/v1/chat/sessions/{self.session_id}/messages",
                expected_status=201,
                headers=headers,
                json_data={"content": "Hello, AI!"},
                description="Send message"
            )
            
            # Get messages
            self.test_endpoint(
                "GET",
                f"/api/v1/chat/sessions/{self.session_id}/messages",
                headers=headers,
                description="Get session messages"
            )
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("Test Summary")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_duration = sum(r.duration_ms for r in self.results) / total if total > 0 else 0
        
        print(f"Total Tests:     {total}")
        print(f"{Colors.GREEN}Passed:          {passed}{Colors.ENDC}")
        print(f"{Colors.RED}Failed:          {failed}{Colors.ENDC}")
        print(f"Pass Rate:       {pass_rate:.1f}%")
        print(f"Avg Duration:    {avg_duration:.0f}ms")
        
        if failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.ENDC}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.method} {result.endpoint}: {result.message}")
        
        return failed == 0
    
    def run_all_tests(self):
        """Run all test suites."""
        print(f"\n{Colors.BOLD}PsyAI Platform - API Testing{Colors.ENDC}")
        print(f"Testing API at: {self.base_url}\n")
        
        # Check if API is reachable
        try:
            response = requests.get(f"{self.base_url}/api/v1/ping", timeout=5)
            if response.status_code != 200:
                print(f"{Colors.RED}✗ API is not responding correctly{Colors.ENDC}")
                sys.exit(1)
        except Exception as e:
            print(f"{Colors.RED}✗ Cannot connect to API: {e}{Colors.ENDC}")
            print(f"\nMake sure the API server is running:")
            print(f"  uvicorn psyai.platform.api_framework:app --reload")
            sys.exit(1)
        
        # Run test suites
        self.run_health_tests()
        self.run_auth_tests()
        self.run_user_tests()
        self.run_chat_tests()
        
        # Print summary
        success = self.print_summary()
        
        sys.exit(0 if success else 1)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test PsyAI Platform API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(base_url=args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
