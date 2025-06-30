#!/usr/bin/env python3
"""Test script to verify the Filters & Search section alignment in Menu Management."""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_filter_section_alignment():
    """Test that the Filters & Search section is properly center-aligned."""
    
    template_path = 'app/modules/admin/templates/menu_management.html'
    
    print("🔍 Testing Filters & Search Section Alignment")
    print("=" * 60)
    
    # Read the template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for center alignment elements
    checks = [
        ('justify-content-center', 'Center justification for flex container'),
        ('text-center', 'Center text alignment for title'),
        ('position-relative', 'Relative positioning for container'),
        ('position-absolute', 'Absolute positioning for actions'),
        ('right: 0', 'Right positioning for filter actions'),
        ('Filters & Search', 'Filter section title exists'),
    ]
    
    results = []
    for check, description in checks:
        found = check in content
        status = "✅ PASS" if found else "❌ FAIL"
        results.append(found)
        print(f"{status} - {description}")
        if found and check == 'Filters & Search':
            # Find and display the context
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if check in line:
                    print(f"      Found at line {i+1}: {line.strip()}")
                    break
    
    # Check for the complete filter section structure
    filter_section_patterns = [
        'class="d-flex justify-content-center align-items-center position-relative"',
        'class="card-title text-center"',
        'class="filter-actions position-absolute"',
        'style="right: 0;"'
    ]
    
    print("\n📋 Filter Section Structure Analysis:")
    print("-" * 40)
    
    structure_checks = []
    for pattern in filter_section_patterns:
        found = pattern in content
        status = "✅ FOUND" if found else "❌ MISSING"
        structure_checks.append(found)
        print(f"{status} - {pattern}")
    
    # Overall assessment
    print(f"\n🎯 Overall Assessment:")
    print("-" * 30)
    
    if all(results) and all(structure_checks):
        print("✅ EXCELLENT: Filters & Search section is properly center-aligned!")
        print("   - Title is centered using text-center class")
        print("   - Container uses justify-content-center for center alignment")
        print("   - Filter actions are positioned absolutely to the right")
        print("   - Structure follows modern Bootstrap flexbox patterns")
    elif most_passed := sum(results + structure_checks) >= len(results + structure_checks) * 0.8:
        print("⚠️  GOOD: Most alignment elements are in place")
        print("   - Minor improvements may be needed")
    else:
        print("❌ NEEDS WORK: Filter section alignment needs attention")
    
    # Extract and display the actual filter header section
    print(f"\n📄 Current Filter Header Structure:")
    print("-" * 40)
    
    lines = content.split('\n')
    in_filter_section = False
    section_lines = []
    
    for i, line in enumerate(lines):
        if '<!-- Enhanced Filters & Search Section -->' in line:
            in_filter_section = True
            section_lines.append(f"{i+1:3}: {line}")
        elif in_filter_section:
            section_lines.append(f"{i+1:3}: {line}")
            if '</div>' in line and 'card-header' in lines[max(0, i-10):i+1][-1] if i >= 10 else line:
                # Stop after the card-header div closes
                break
        
        if len(section_lines) > 15:  # Safety limit
            break
    
    for line in section_lines[:12]:  # Show first 12 lines
        print(line)
    
    if len(section_lines) > 12:
        print("    ... (truncated)")

if __name__ == "__main__":
    test_filter_section_alignment()
