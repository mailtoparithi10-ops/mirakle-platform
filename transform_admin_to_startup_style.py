#!/usr/bin/env python3
"""
Transform Admin Dashboard to Startup Dashboard Style
Complete transformation using startup dashboard as exact reference
"""

print("🎨 Transforming Admin Dashboard to Startup Style")
print("=" * 70)

# Read admin dashboard
with open("templates/admin_dashboard.html", "r", encoding="utf-8") as f:
    admin_content = f.read()

print(f"✅ Read admin dashboard ({len(admin_content)} characters)")

# Top navigation HTML (exactly like startup dashboard)
top_nav = """<body>
    <!-- Top Navigation -->
    <nav class="top-nav">
        <div class="nav-brand">
            <i class="fas fa-shield-alt"></i>
            ADMIN
        </div>
        
        <div class="nav-dropdowns">
            <!-- Dashboard Dropdown -->
            <div class="dropdown" id="dashboardDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('dashboardDropdown')">
                    <i class="fas fa-chart-line"></i>
                    Dashboard
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('dashboard')">
                        <i class="fas fa-home"></i>
                        Overview
                    </button>
                    <button class="dropdown-item" onclick="showSection('analytics')">
                        <i class="fas fa-chart-bar"></i>
                        Analytics
                    </button>
                </div>
            </div>

            <!-- Users Dropdown -->
            <div class="dropdown" id="usersDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('usersDropdown')">
                    <i class="fas fa-users"></i>
                    Users
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('users')">
                        <i class="fas fa-users"></i>
                        All Users
                    </button>
                    <button class="dropdown-item" onclick="showSection('startups')">
                        <i class="fas fa-rocket"></i>
                        Startups
                    </button>
                    <button class="dropdown-item" onclick="showSection('corporate')">
                        <i class="fas fa-building"></i>
                        Corporate
                    </button>
                    <button class="dropdown-item" onclick="showSection('connectors')">
                        <i class="fas fa-handshake"></i>
                        Connectors
                    </button>
                </div>
            </div>

            <!-- Programs Dropdown -->
            <div class="dropdown" id="programsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('programsDropdown')">
                    <i class="fas fa-trophy"></i>
                    Programs
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('programs')">
                        <i class="fas fa-trophy"></i>
                        All Programs
                    </button>
                    <button class="dropdown-item" onclick="showSection('referrals')">
                        <i class="fas fa-exchange-alt"></i>
                        Referrals
                    </button>
                </div>
            </div>

            <!-- Activity Dropdown -->
            <div class="dropdown" id="activityDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('activityDropdown')">
                    <i class="fas fa-bolt"></i>
                    Activity
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="showSection('meetings')">
                        <i class="fas fa-video"></i>
                        Meetings
                    </button>
                    <button class="dropdown-item" onclick="showSection('leads')">
                        <i class="fas fa-hand-holding-heart"></i>
                        Leads
                    </button>
                    <button class="dropdown-item" onclick="showSection('inbox')">
                        <i class="fas fa-envelope"></i>
                        Inbox
                    </button>
                </div>
            </div>

            <!-- Tools Dropdown -->
            <div class="dropdown" id="toolsDropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('toolsDropdown')">
                    <i class="fas fa-tools"></i>
                    Tools
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; margin-left: 4px;"></i>
                </button>
                <div class="dropdown-menu">
                    <button class="dropdown-item" onclick="seedMockData()">
                        <i class="fas fa-database"></i>
                        Seed Mock Data
                    </button>
                    <button class="dropdown-item" onclick="document.getElementById('globalSearchInput')?.focus()">
                        <i class="fas fa-search"></i>
                        Global Search
                    </button>
                </div>
            </div>

            <!-- Profile Dropdown -->
            <div class="dropdown profile-dropdown" id="profileDropdown">
                <button class="profile-toggle" onclick="toggleDropdown('profileDropdown')">
                    <div class="avatar">A</div>
                    <span class="profile-name">Admin</span>
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; color: #94a3b8;"></i>
                </button>
                <div class="dropdown-menu" style="right: 0; left: auto;">
                    <button class="dropdown-item" onclick="goToPlatform()">
                        <i class="fas fa-arrow-left"></i>
                        Back to Platform
                    </button>
                    <button class="dropdown-item" onclick="window.location.href='/logout'">
                        <i class="fas fa-sign-out-alt"></i>
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
"""

# Replace <body> tag with new structure
admin_content = admin_content.replace("<body>", top_nav)

# Find and remove old header and sidebar (everything between <body> and first section)
# Find the first <section or <div class="welcome-banner"
import re

# Remove everything from after <body> to the first actual content section
# Pattern: from <body> to <div class="welcome-banner">
pattern = r'(<body>.*?)(<!-- DASHBOARD SECTION -->|<div class="welcome-banner">)'
match = re.search(pattern, admin_content, re.DOTALL)

if match:
    # Keep everything before <body> and after the welcome banner
    before_body = admin_content[:admin_content.find('<body>')]
    after_banner = admin_content[admin_content.find('<!-- DASHBOARD SECTION -->'):]
    
    admin_content = before_body + top_nav + after_banner
    print("✅ Replaced old structure with new navigation")
else:
    print("⚠️  Could not find pattern, using simple replacement")

# Close main and body tags properly at the end
# Find </body> and add </main> before it
admin_content = admin_content.replace('</body>', '</main>\n</body>')

# Save
with open("templates/admin_dashboard.html", "w", encoding="utf-8") as f:
    f.write(admin_content)

print(f"✅ Saved admin dashboard ({len(admin_content)} characters)")

print("\n" + "=" * 70)
print("🎉 Transformation Complete!")
print("\n✨ Next: Update CSS to match startup dashboard style")
