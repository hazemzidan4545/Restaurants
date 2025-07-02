import requests
import json

def test_order_api():
    """Test order creation via API"""
    
    try:
        # First, let's check if the server is running
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Test data for order creation
    order_data = {
        "customer_id": 1,
        "table_id": 1,
        "order_type": "dine_in",
        "items": [
            {
                "item_id": 1,
                "quantity": 2,
                "note": "Test order item"
            }
        ]
    }
    
    try:
        print("🧪 Testing order creation via API...")
        response = requests.post(
            'http://localhost:5000/api/orders',
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Order created successfully!")
            return True
        else:
            print(f"❌ Order creation failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_order_api()
    if success:
        print("\n🎉 API order creation test PASSED!")
    else:
        print("\n💥 API order creation test FAILED!")
