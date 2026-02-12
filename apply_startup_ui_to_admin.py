#!/usr/bin/env python3
"""
Apply startup dashboard UI/UX to admin dashboard
Preserves ALL fields and functionality
"""

import re
from datetime import datetime

print("🎨 Applying Startup Dashboard UI to Admin Dashboard")
print("=" * 70)

# Read the admin dashboard
with open("templates/admin_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ Read admin dashboard ({len(content)} characters, {content.count(chr(10))} lines)")

# Step 1: Replace the header and sidebar with top navigation
# Find the body tag and everything up to admin-content
old_nav_pattern = r'<body>.*?<div class="admin-content">'

new_top_nav = '''<body>
    <!-- Top Nav -->
    <nav class="top-nav">
        <a href="/" class="nav-brand" style="text-decoration: none;">
            <i class="fas fa-hexagon-nodes"></i>
            ALCHEMY ADMIN
        </a>

        <div class="nav-dropdowns">
            <!-- Dashboard Dropdown -->
            <div class="dropdown" id="dashboardDropdown">
                <button class="dropdown-toggle active" onclick="toggleDropdown('dashboardDropdown')">
                    <i class="fas fa-grid-2"></i> Dashboard <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('dashboard')"><i class="fas fa-chart-line"></i> Overview</button>
                    <button class="dropdown-item" onclick="showSection('analytics')"><i class="fas fa-chart-bar"></i> Analytics</button>
                </div>
            </div>

            <!-- Users Dropdown -->
            <div class="dropdown" id="usersDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('usersDropdown')">
                    <i class="fas fa-users"></i> Users <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('users')"><i class="fas fa-users"></i> All Users</button>
                    <button class="dropdown-item" onclick="showSection('startups')"><i class="fas fa-rocket"></i> Startups</button>
                    <button class="dropdown-item" onclick="showSection('corporate')"><i class="fas fa-building"></i> Corporate</button>
                    <button class="dropdown-item" onclick="showSection('connectors')"><i class="fas fa-handshake"></i> Connectors</button>
                </div>
            </div>

            <!-- Programs Dropdown -->
            <div class="dropdown" id="programsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('programsDropdown')">
                    <i class="fas fa-trophy"></i> Programs <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('programs')"><i class="fas fa-trophy"></i> All Programs</button>
                    <button class="dropdown-item" onclick="showSection('referrals')"><i class="fas fa-exchange-alt"></i> Referrals</button>
                </div>
            </div>

            <!-- Activity Dropdown -->
            <div class="dropdown" id="activityDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('activityDropdown')">
                    <i class="fas fa-bell"></i> Activity <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('meetings')"><i class="fas fa-video"></i> Meetings</button>
                    <button class="dropdown-item" onclick="showSection('leads')"><i class="fas fa-hand-holding-heart"></i> Leads</button>
                    <button class="dropdown-item" onclick="showSection('inbox')"><i class="fas fa-envelope"></i> Inbox</button>
                </div>
            </div>

            <!-- Tools Dropdown -->
            <div class="dropdown" id="toolsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('toolsDropdown')">
                    <i class="fas fa-tools"></i> Tools <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="seedMockData()"><i class="fas fa-database"></i> Seed Mock Data</button>
                    <button class="dropdown-item" id="globalSearchBtn"><i class="fas fa-search"></i> Global Search</button>
                </div>
            </div>
        </div>

        <!-- Profile Dropdown -->
        <div class="dropdown profile-dropdown" id="profileDropdown">
            <div class="profile-toggle dropdown-toggle" onclick="toggleDropdown('profileDropdown')">
                <div class="avatar">A</div>
                <span class="profile-name">Admin</span>
                <i class="fas fa-chevron-down" style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-left: 5px;"></i>
            </div>
            <div class="dropdown-menu" style="left: auto; right: 0; min-width: 200px;">
                <a href="/" class="dropdown-item" style="text-decoration: none;"><i class="fas fa-house"></i> Back to Platform</a>
                <div style="border-top: 1px solid #f1f5f9; margin: 0.5rem 0;"></div>
                <a href="/logout" class="dropdown-item" style="color: #ef4444; text-decoration: none;"><i class="fas fa-right-from-bracket"></i> Sign Out</a>
            </div>
        </div>
    </nav>

    <main class="main-content">
        <div class="admin-content">'''

# Replace the navigation
content = re.sub(old_nav_pattern, new_top_nav, content, flags=re.DOTALL)
print("✅ Replaced header and sidebar with top navigation")

# Save the file
with open("templates/admin_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved updated dashboard")
print(f"📊 Final size: {len(content)} characters")
print("\n🎉 Phase 1 Complete: Navigation Structure Updated!")
print("\nNext: Run apply_startup_css_to_admin.py to update styles")
