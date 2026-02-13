#!/usr/bin/env python3
"""
Complete Admin Dashboard Transformation
Transform admin dashboard to match startup/enabler design in one go
"""

print("🎨 Complete Admin Dashboard Transformation")
print("=" * 70)

# Read the original file
with open("templates/admin_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"✅ Read original file ({len(html)} characters)")

# Step 1: Add top navigation after <body> tag
top_nav = """
    <!-- Modern Top Navigation -->
    <nav class="top-nav">
        <div class="nav-brand">
            <i class="fas fa-shield-alt"></i>
            ADMIN
        </div>
        
        <div cla