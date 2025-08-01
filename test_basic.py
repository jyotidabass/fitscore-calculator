#!/usr/bin/env python3
"""
Basic test script for the FitScore Calculator FastAPI application
Tests basic functionality without requiring OpenAI API key
"""

import requests
import subprocess
import time
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def start_server():
    """Start the FastAPI server in the background"""
    print("🚀 Starting FastAPI server...")
    try:
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "fitscore_calculator:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully")
                return process
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def stop_server(process):
    """Stop the FastAPI server"""
    if process:
        print("�� Stopping server...")
        process.terminate()
        process.wait()

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
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
        response = requests.get(f"{BASE_URL}/api-docs")
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

def test_root_endpoint():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_docs_endpoint():
    """Test docs endpoint"""
    print("\n🔍 Testing docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Docs endpoint working")
            return True
        else:
            print(f"❌ Docs endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Docs endpoint error: {e}")
        return False

def main():
    """Run basic tests"""
    print("�� Starting Basic FitScore Calculator API Tests")
    print("=" * 50)
    
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
        
        if test_root_endpoint():
            tests_passed += 1
        
        if test_docs_endpoint():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"🎉 Basic tests completed! {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("✅ All basic tests passed!")
            sys.exit(0)
        else:
            print("❌ Some basic tests failed!")
            sys.exit(1)
            
    finally:
        # Always stop the server
        stop_server(server_process)

if __name__ == "__main__":
    main()
