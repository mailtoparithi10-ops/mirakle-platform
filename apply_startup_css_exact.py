#!/usr/bin/env python3
"""
Apply Startup Dashboard CSS to Admin Dashboard
Use exact CSS from startup dashboard
"""

print("🎨 Applying Startup Dashboard CSS")
print("=" * 70)

# Read current admin CSS
with open("static/css/admin_dashboard.css", "r", encoding="utf-8") as f:
    admin_css = f.read()

print(f"✅ Read admin CSS ({len(admin_css)} characters)")

# Startup dashboard CSS for navigation (exact copy)
startup_nav_css = """:root {
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

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg-page);
    color: var(--text-main);
    min-height: 100vh;
}

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

/* Main Content */
.main-content {
    margin-top: 74px;
    flex: 1;
    padding: 2.5rem 3.5rem;
    width: 100%;
    max-width: 1440px;
    margin-left: auto;
    margin-right: auto;
}

"""

# Prepend startup CSS to admin CSS
new_css = startup_nav_css + "\n\n/* ===== ADMIN DASHBOARD SPECIFIC STYLES ===== */\n\n" + admin_css

# Save
with open("static/css/admin_dashboard.css", "w", encoding="utf-8") as f:
    f.write(new_css)

print(f"✅ Saved updated CSS ({len(new_css)} characters)")

print("\n" + "=" * 70)
print("🎉 CSS Applied!")
print("\n✨ Admin dashboard now has startup dashboard styling")
