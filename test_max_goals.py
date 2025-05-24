#!/usr/bin/env python3
"""
Test script to verify max goal functionality for spending limits
"""
import requests
import json
import time

# Test data
TEST_USERNAME = f"testuser_max_goals_{int(time.time())}"
BASE_URL = "http://localhost:8000"

def test_max_goals():
    print("Testing max goal functionality...")
    
    # Create test user
    print(f"1. Creating test user: {TEST_USERNAME}")
    try:
        response = requests.post(f"{BASE_URL}/api/signup", json={"username": TEST_USERNAME})
        if response.status_code == 200:
            user_data = response.json()
            token = user_data["token"]
            print(f"   User created: {user_data['username']}")
            print(f"   Token: {token[:10]}...")
        else:
            print(f"   User might already exist: {response.status_code}")
            return
    except Exception as e:
        print(f"   Error creating user: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get metrics config to verify types
    print("2. Getting metrics config...")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/config", headers=headers)
        if response.status_code == 200:
            config = response.json()
            print("   Metrics config:")
            for metric in config:
                print(f"     {metric['name']} ({metric['key']}): type={metric['type']}, goal={metric['goal']}")
        else:
            print(f"   Error getting config: {response.status_code}")
            return
    except Exception as e:
        print(f"   Error getting config: {e}")
        return
    
    # Find the spend metric (max type)
    spend_metric = None
    for metric in config:
        if metric['type'] == 'max':
            spend_metric = metric
            break
    
    if not spend_metric:
        print("   No max type metric found!")
        return
    
    print(f"3. Testing with spend metric: {spend_metric['name']} (limit: {spend_metric['goal']})")
    
    # Add some spending entries - some below limit, some above
    test_entries = [
        (5000, "Should be under limit"),  # Under limit
        (8000, "Should be under limit"),  # Under limit  
        (15000, "Should be over limit"),  # Over limit
        (3000, "Should be under limit"),  # Under limit
    ]
    
    print("4. Adding test spending entries...")
    for value, description in test_entries:
        try:
            response = requests.post(f"{BASE_URL}/api/metrics", 
                                   headers=headers,
                                   json={"metric_key": spend_metric['key'], "value": value})
            if response.status_code == 200:
                print(f"   Added {value} INR - {description}")
            else:
                print(f"   Error adding entry: {response.status_code}")
        except Exception as e:
            print(f"   Error adding entry: {e}")
    
    # Get aggregated metrics to see goal completion
    print("5. Getting aggregated metrics...")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", headers=headers)
        if response.status_code == 200:
            metrics = response.json()
            daily_data = metrics.get("daily", {})
            goal_reached = daily_data.get("goalReached", {})
            
            print("   Goal completion results:")
            for metric_key, days_completed in goal_reached.items():
                metric_info = next((m for m in config if m['key'] == metric_key), None)
                if metric_info:
                    goal_type = "Limit" if metric_info['type'] == 'max' else "Goal"
                    print(f"     {metric_info['name']}: {days_completed}/1 days {goal_type.lower()} met")
                    
                    if metric_info['type'] == 'max':
                        # For max goals, show the actual values vs limit
                        avg_value = daily_data.get("average_values", {}).get(metric_key, 0)
                        limit = metric_info['goal']
                        status = "UNDER" if avg_value <= limit else "OVER"
                        print(f"       Daily total: {avg_value} INR (Limit: {limit} INR) - {status} LIMIT")
            
        else:
            print(f"   Error getting metrics: {response.status_code}")
    except Exception as e:
        print(f"   Error getting metrics: {e}")
    
    print("6. Test completed!")

if __name__ == "__main__":
    test_max_goals() 