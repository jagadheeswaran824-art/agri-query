#!/usr/bin/env python3
"""
Test script for KrishiSahay Flask Backend
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    try:
        test_query = "How to control aphids in mustard?"
        payload = {
            "query": test_query,
            "mode": "online"
        }
        
        print(f"\n🧪 Testing Query: {test_query}")
        response = requests.post(
            'http://localhost:5000/api/query',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query Test Passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Response Time: {data.get('responseTime', 0):.2f}ms")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            print(f"   Offline Answer: {data.get('offlineAnswer', '')[:100]}...")
            if data.get('onlineAnswer'):
                print(f"   Online Answer: {data.get('onlineAnswer', '')[:100]}...")
            return True
        else:
            print(f"❌ Query Test Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Query Test Error: {e}")
        return False

def test_analytics_endpoint():
    """Test the analytics endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/analytics')
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Analytics Test Passed")
            print(f"   Total Queries: {data.get('total_queries', 0)}")
            print(f"   Active Users: {data.get('active_users', 0)}")
            print(f"   Avg Response Time: {data.get('avg_response_time', 0):.2f}ms")
            return True
        else:
            print(f"❌ Analytics Test Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics Test Error: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/status')
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Status Test Passed")
            print(f"   Active Connections: {data.get('activeConnections', 0)}")
            print(f"   Active Sessions: {data.get('activeSessions', 0)}")
            print(f"   Total Queries: {data.get('totalQueries', 0)}")
            return True
        else:
            print(f"❌ Status Test Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status Test Error: {e}")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🧪 KrishiSahay Backend Test Suite                  ║
║                                                       ║
║   Testing Flask server endpoints...                  ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Query Endpoint", test_query_endpoint),
        ("Analytics Endpoint", test_analytics_endpoint),
        ("Status Endpoint", test_status_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        if test_func():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        print("\n🌐 You can now:")
        print("   • Open http://localhost:5000 in your browser")
        print("   • Use the frontend interface")
        print("   • Test WebSocket connections")
    else:
        print("⚠️  Some tests failed. Check the server logs.")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()