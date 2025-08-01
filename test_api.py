#!/usr/bin/env python3
"""
Test script for the FitScore Calculator FastAPI application
"""

import requests
import json
import time
import subprocess
import os
import signal
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def start_server():
    """Start the FastAPI server in the background"""
    print("🚀 Starting FastAPI server...")
    try:
        # Check if main.py exists
        if not os.path.exists("main.py"):
            print("❌ main.py not found!")
            return None
        
        # Start the server in the background with more verbose output
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Server process started with PID: {process.pid}")
        
        # Wait longer for server to start
        print("⏳ Waiting for server to start...")
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server started successfully and responding!")
                    return process
                else:
                    print(f"⚠️ Server responding but status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⏳ Still waiting... ({i+1}/10) - {e}")
                continue
        
        # If we get here, server didn't start properly
        print("❌ Server failed to start within timeout")
        
        # Check if process is still running
        if process.poll() is None:
            print("⚠️ Process is still running but not responding")
            return process
        else:
            print("❌ Process has terminated")
            # Get any error output
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Server stderr: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def stop_server(process):
    """Stop the FastAPI server"""
    if process:
        print("🛑 Stopping server...")
        try:
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server stopped successfully")
        except subprocess.TimeoutExpired:
            print("⚠️ Server didn't stop gracefully, forcing...")
            process.kill()
            process.wait()

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    print("\n🔍 Testing API docs...")
    try:
        response = requests.get(f"{BASE_URL}/api-docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs endpoint working")
            print(f"Available endpoints: {list(response.json()['endpoints'].keys())}")
            return True
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

def test_fitscore_calculation():
    """Test FitScore calculation with sample data"""
    print("\n🔍 Testing FitScore calculation...")
    
    # Sample data
    sample_data = {
        "resume_text": """John Doe
Software Engineer

EDUCATION:
Massachusetts Institute of Technology
Bachelor of Science in Computer Science
GPA: 3.8

EXPERIENCE:
Senior Software Engineer
Google Inc.
2020-2023 (3 years)
- Led team of 10 engineers
- Built scalable microservices
- Used Python, React, AWS, Docker

Software Engineer
Microsoft Corporation
2018-2020 (2 years)
- Developed web applications
- Used JavaScript, Node.js, SQL

SKILLS:
Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, SQL, MongoDB

BONUS:
- Open source contributor
- Published technical articles
- Speaking at conferences""",
        
        "job_description": """Senior Software Engineer
Tech Startup

We are looking for a Senior Software Engineer to join our growing team.

Requirements:
- 5+ years of software engineering experience
- Strong knowledge of Python, JavaScript, React
- Experience with AWS, Docker, Kubernetes
- Experience with microservices architecture
- Leadership experience preferred

Nice to have:
- Machine learning experience
- Open source contributions
- Startup experience""",
        
        "collateral": "Startup environment with fast-paced culture and emphasis on technical skills.",
        "use_gpt4": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-fitscore",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ FitScore calculation successful!")
            print(f"Total Score: {result['total_score']}")
            print(f"Submittable: {result['submittable']}")
            return True
        else:
            print(f"❌ FitScore calculation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FitScore calculation error: {e}")
        return False

def test_form_endpoint():
    """Test form-based endpoint"""
    print("\n🔍 Testing form endpoint...")
    
    form_data = {
        "resume_text": "Software Engineer at Google with Python, React, AWS experience. MIT graduate.",
        "job_description": "Looking for Python developer with React and AWS experience.",
        "use_gpt4": "true"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-fitscore-form",
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Form endpoint working!")
                print(f"Total Score: {result['total_score']}")
                print(f"Submittable: {result['submittable']}")
                return True
            else:
                print(f"❌ Form endpoint failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Form endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Form endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting FitScore Calculator API Tests")
    print("=" * 50)
    
    # Check if we're in the right directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Start the server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server. Exiting.")
        sys.exit(1)
    
    try:
        # Run tests
        tests_passed = 0
        total_tests = 4
        
        if test_health():
            tests_passed += 1
        
        if test_api_docs():
            tests_passed += 1
        
        if test_fitscore_calculation():
            tests_passed += 1
        
        if test_form_endpoint():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"🎉 Tests completed! {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
            
    finally:
        # Always stop the server
        stop_server(server_process)

if __name__ == "__main__":
    main() 
