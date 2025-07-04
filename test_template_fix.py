#!/usr/bin/env python3
"""
Quick test to verify the template fix worked
"""
import requests

def test_edit_campaign_page():
    """Test the edit campaign page that was causing the error"""
    print("🧪 Testing Edit Campaign Page Fix")
    print("-" * 35)
    
    try:
        # Test the edit campaign page with campaign ID 1
        url = "http://127.0.0.1:5000/admin/campaigns/edit/1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Edit Campaign page is working!")
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.content)} bytes")
            
            # Check if the response contains expected content
            if b"Edit Campaign" in response.content:
                print("✅ Page contains expected title")
            else:
                print("⚠️ Page may not be loading correctly")
                
        elif response.status_code == 404:
            print("⚠️ Campaign not found (ID 1 may not exist)")
            print("   This is expected if no campaigns exist yet")
        else:
            print(f"❌ Error: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Flask server may not be running")
    except Exception as e:
        print(f"❌ Error testing page: {e}")

def test_other_campaign_pages():
    """Test other campaign-related pages"""
    print("\n🧪 Testing Other Campaign Pages")
    print("-" * 32)
    
    pages = [
        ("/admin/campaigns-management", "Campaigns Management"),
        ("/admin/campaigns/add", "Add Campaign"),
    ]
    
    for endpoint, name in pages:
        try:
            url = f"http://127.0.0.1:5000{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection failed")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def main():
    print("🔧 TEMPLATE ERROR FIX VERIFICATION")
    print("=" * 40)
    
    test_edit_campaign_page()
    test_other_campaign_pages()
    
    print("\n" + "=" * 40)
    print("📝 FIXES APPLIED:")
    print("✅ Added 'now=datetime.now' to edit_campaign route")
    print("✅ Fixed template to use 'now' variable instead of 'now()' function")
    print("✅ Updated both date calculations in the template")
    
    print("\n🎯 RESULT:")
    print("The UndefinedError for 'now' should now be resolved!")

if __name__ == "__main__":
    main()
