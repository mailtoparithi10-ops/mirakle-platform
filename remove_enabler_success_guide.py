"""
Remove Enabler Success Guide Section
This section contains non-functional buttons and mock resources that don't exist.
"""

def remove_success_guide():
    with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove the entire guide section
    # The section starts at line 4613 with <section id="guide" class="section">
    # and ends before the closing </div> for main content
    
    guide_section_start = content.find('<section id="guide" class="section">')
    if guide_section_start == -1:
        print("❌ Guide section not found")
        return
    
    # Find the end of this section (before </div>\n    </main>)
    guide_section_end = content.find('</section>', guide_section_start)
    if guide_section_end == -1:
        print("❌ Could not find end of guide section")
        return
    
    # Include the closing </section> tag
    guide_section_end += len('</section>')
    
    # Remove the section
    new_content = content[:guide_section_start] + content[guide_section_end:]
    
    # Also need to remove the guide case from showSection function
    # Find the guide case in the showSection function
    guide_case = """} else if (sectionId === 'guide') {
                sectionTitle.textContent = 'Connector Success Guide';
                sectionSubtitle.textContent = 'Learn strategies to maximize your impact and unlock premium reward tiers.';
            }"""
    
    new_content = new_content.replace(guide_case, '}')
    
    # Write back
    with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Removed Enabler Success Guide section")
    print("   - Removed entire guide section HTML")
    print("   - Removed guide case from showSection() function")
    print("   - Section contained non-functional buttons:")
    print("     • Start Interactive Tutorial (startGuideTutorial not implemented)")
    print("     • Download buttons (downloadAsset not implemented)")
    print("     • Mock reward tier system")
    print("     • Mock connector resources")

if __name__ == '__main__':
    remove_success_guide()
