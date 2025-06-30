import requests

try:
    response = requests.get('http://localhost:5000/admin/services')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Page loads successfully")
        
        # Check for key modal elements
        html = response.text
        elements = {
            'deleteModal': 'id="deleteModal"' in html,
            'confirmDelete': 'confirmDelete(' in html,
            'delete-btn': 'delete-btn' in html,
            'serviceName': 'id="serviceName"' in html
        }
        
        for element, found in elements.items():
            status = "✓" if found else "✗"
            print(f"{status} {element}: {found}")
            
    else:
        print(f"✗ HTTP {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
