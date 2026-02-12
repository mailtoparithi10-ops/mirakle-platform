#!/usr/bin/env python3
"""
Apply startup dashboard UI/UX to enabler dashboard
Preserves all fields and functionality
"""

import re
from datetime import datetime

print("🎨 Applying Startup Dashboard UI to Enabler Dashboard")
print("=" * 70)

# Read the enabler dashboard
with open("templates/enabler_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ Read enabler dashboard ({len(content)} characters, {content.count(chr(10))} lines)")

# Step 1: Update title
content = content.replace(
    "<title>Connector Dashboard - Alchemy</title>",
    "<title>Enabler Dashboard - Alchemy</title>"
)
print("✅ Updated page title")

# Step 2: Add CSS variables at the beginning of style section
css_variables = """        :root {
            --primary: #ffdf00;
            --primary-dark: #e6c800;
            --bg-dark: #000000;
            --bg-page: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-dim: #64748b;
            --border: #e2e8f0;
            --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        """

# Find the style tag and insert variables
content = content.replace(
    "    <style>\n        .timeline-meta {",
    f"    <style>\n{css_variables}        .timeline-meta {{"
)
print("✅ Added CSS variables")

# Step 3: Update body styles
old_body = """        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            min-height: 100vh;
            display: flex;
        }"""

new_body = """        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-page);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
        }"""

content = content.replace(old_body, new_body)
print("✅ Updated body styles")

# Step 4: Update main-content styles
old_main = """        .main-content {
            margin-left: 240px;
            flex: 1;
            background: white;
            min-height: 100vh;
            border-radius: 20px 0 0 20px;
            overflow: hidden;
        }"""

new_main = """        .main-content {
            margin-top: 74px;
            flex: 1;
            padding: 2.5rem 3.5rem;
            width: 100%;
            max-width: 1440px;
            margin-left: auto;
            margin-right: auto;
        }"""

content = content.replace(old_main, new_main)
print("✅ Updated main-content layout")

# Step 5: Add top navigation CSS (insert before .sidebar)
top_nav_css = """
        /* Top Navigation */
        .top-nav {
            width: 100%;
            background: #000;
            padding: 0.75rem 2.5rem;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #fff;
            font-size: 1.4rem;
            font-weight: 900;
            letter-spacing: -0.5px;
        }

        .nav-brand i {
            color: var(--primary);
        }

        .nav-dropdowns {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .dropdown {
            position: relative;
        }

        .dropdown-toggle {
            background: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.7rem 1.1rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition);
        }

        .dropdown-toggle:hover,
        .dropdown-toggle.active {
            color: var(--primary);
            background: rgba(255, 223, 0, 0.1);
            border-color: var(--primary);
        }

        .dropdown-menu {
            position: absolute;
            top: 115%;
            left: 0;
            background: white;
            border-radius: 18px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border);
            min-width: 240px;
            padding: 0.75rem;
            opacity: 0;
            visibility: hidden;
            transform: translateY(10px);
            transition: var(--transition);
            z-index: 1001;
        }

        .dropdown.active .dropdown-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .dropdown-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.8rem 1rem;
            color: var(--text-main);
            text-decoration: none;
            transition: var(--transition);
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            background: none;
            border: none;
            width: 100%;
            text-align: left;
        }

        .dropdown-item:hover {
            background: #f8fafc;
            color: #000;
        }

        .dropdown-item.active {
            background: rgba(255, 223, 0, 0.15);
            color: #000;
        }

        .dropdown-item.active i {
            color: var(--primary-dark);
        }

        .dropdown-item i {
            width: 18px;
            color: var(--text-dim);
        }

        .dropdown-item:hover i {
            color: var(--primary-dark);
        }

        .profile-dropdown {
            position: relative;
        }

        .profile-toggle {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            padding: 5px 15px 5px 6px;
            cursor: pointer;
            transition: var(--transition);
        }

        .profile-toggle:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            color: #000;
            font-size: 0.9rem;
            overflow: hidden;
        }

        .profile-name {
            color: white;
            font-size: 0.85rem;
            font-weight: 700;
        }

        /* Hide sidebar */
        .sidebar {
            display: none;
        }

"""

content = content.replace("        .sidebar {", top_nav_css + "        .sidebar-old {")
print("✅ Added top navigation CSS and hid sidebar")

# Step 6: Update dashboard header styles
old_dashboard_header = """        .dashboard-header {
            padding: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            background: white;
        }

        .dashboard-title {
            font-size: 2rem;
            font-weight: 700;
            color: #000000;
            margin-bottom: 0.5rem;
        }

        .dashboard-subtitle {
            color: #666666;
            font-size: 1rem;
        }"""

new_dashboard_header = """        .dashboard-header {
            margin-bottom: 2.5rem;
        }

        .dashboard-title {
            font-size: 2.2rem;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -0.5px;
            margin-bottom: 0.4rem;
        }

        .dashboard-subtitle {
            color: var(--text-dim);
            font-size: 1.05rem;
            font-weight: 500;
        }"""

content = content.replace(old_dashboard_header, new_dashboard_header)
print("✅ Updated dashboard header styles")

# Step 7: Update card styles
content = re.sub(
    r'border-radius: 1rem;',
    'border-radius: 22px;',
    content
)
print("✅ Updated card border-radius")

# Step 8: Update button styles
old_btn_primary = """        .btn-primary {
            background: #fcb82e;
            border-color: #fbbf24;
            color: #000000;
        }

        .btn-primary:hover {
            background: #e5a629;
        }"""

new_btn_styles = """        .btn {
            padding: 10px 18px;
            border-radius: 12px;
            border: none;
            font-weight: 800;
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
        }

        .btn-black {
            background: var(--text-main);
            color: var(--primary);
        }

        .btn-black:hover {
            transform: translateY(-2px);
            opacity: 0.9;
        }

        .btn-primary {
            background: #fcb82e;
            border-color: #fbbf24;
            color: #000000;
        }

        .btn-primary:hover {
            background: #e5a629;
            transform: translateY(-2px);
        }"""

if old_btn_primary in content:
    content = content.replace(old_btn_primary, new_btn_styles)
    print("✅ Updated button styles")

# Save the modified content
output_file = "templates/enabler_dashboard.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved updated dashboard to {output_file}")
print(f"📊 Final size: {len(content)} characters, {content.count(chr(10))} lines")
print("\n🎉 Phase 1 Complete: CSS and Layout Updated!")
print("\nNext: Run apply_startup_nav_to_enabler.py to update the navigation HTML")
