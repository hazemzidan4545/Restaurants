#!/usr/bin/env python3
"""
Simple template validation test for admin module templates
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.append(str(app_dir))

try:
    from flask import Flask, render_template_string
    from jinja2 import Environment, FileSystemLoader, TemplateError
    
    # Set up Jinja2 environment to load templates
    template_dir = app_dir / 'app' / 'modules' / 'admin' / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    print("Testing admin template compilation...")
    
    # Test base template
    try:
        base_template = env.get_template('base.html')
        print("✓ base.html compiled successfully")
    except TemplateError as e:
        print(f"✗ base.html compilation error: {e}")
        
    # Test menu management template  
    try:
        menu_template = env.get_template('menu_management.html')
        print("✓ menu_management.html compiled successfully")
    except TemplateError as e:
        print(f"✗ menu_management.html compilation error: {e}")
        
    # Test services management template
    try:
        services_template = env.get_template('services_management.html')
        print("✓ services_management.html compiled successfully")
    except TemplateError as e:
        print(f"✗ services_management.html compilation error: {e}")
        
    print("\nTemplate validation complete!")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure Flask is installed: pip install flask")
except Exception as e:
    print(f"Unexpected error: {e}")
