"""
Restore Program Details Section and Fix Profile Section Visibility
This script:
1. Restores the missing program-details section that shows referral links
2. Ensures profile section displays properly
"""

# Read the current file
with open('templates/enabler_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert the program-details section (after the programs section, before referrals section)
programs_section_end = '            </section>\n\n            <!-- REFERRALS SECTION -->'

# Create the program-details section HTML
program_details_section = '''            </section>

            <!-- PROGRAM DETAILS SECTION -->
            <section id="program-details" class="section">
                <div style="margin-bottom: 2rem;">
                    <button class="btn" onclick="showSection('programs')" style="margin-bottom: 1rem;">
                        <i class="fa-solid fa-arrow-left"></i> Back to Programs
                    </button>
                </div>

                <div class="card" style="overflow: hidden; padding: 0;">
                    <!-- Program Banner -->
                    <div id="programDetailsBanner" style="height: 200px; background-size: cover; background-position: center; position: relative;">
                        <div style="position: absolute; top: 1rem; left: 1rem;">
                            <span id="programDetailsType" class="badge-soft" style="background: rgba(0,0,0,0.7); color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700;">Program</span>
                        </div>
                    </div>

                    <!-- Program Content -->
                    <div style="padding: 2rem;">
                        <h2 id="programDetailsTitle" style="font-size: 2rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem;">Program Title</h2>
                        
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 3rem; margin-top: 2rem;">
                            <!-- Left Column - Details -->
                            <div>
                                <div style="margin-bottom: 2rem;">
                                    <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 0.75rem;">
                                        <i class="fa-solid fa-info-circle"></i> Description
                                    </h3>
                                    <p id="programDetailsDesc" style="color: #64748b; line-height: 1.7;">Program description will appear here.</p>
                                </div>

                                <div style="margin-bottom: 2rem;">
                                    <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 0.75rem;">
                                        <i class="fa-solid fa-check-circle"></i> Eligibility
                                    </h3>
                                    <p id="programDetailsEligibility" style="color: #64748b; line-height: 1.7;">Eligibility criteria will appear here.</p>
                                </div>

                                <div style="margin-bottom: 2rem;">
                                    <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 0.75rem;">
                                        <i class="fa-solid fa-gift"></i> Benefits
                                    </h3>
                                    <p id="programDetailsBenefits" style="color: #64748b; line-height: 1.7;">Program benefits will appear here.</p>
                                </div>

                                <div style="margin-bottom: 2rem;">
                                    <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 0.75rem;">
                                        <i class="fa-solid fa-tags"></i> Sectors
                                    </h3>
                                    <div id="programDetailsSectors" style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                        <!-- Sectors will be populated here -->
                                    </div>
                                </div>
                            </div>

                            <!-- Right Column - Quick Info & Actions -->
                            <div>
                                <div class="card" style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.5rem;">
                                    <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 1.5rem;">
                                        <i class="fa-solid fa-clipboard-list"></i> Quick Info
                                    </h3>
                                    
                                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                                        <div>
                                            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Countries</div>
                                            <div id="programDetailsCountries" style="font-weight: 600; color: #1e293b;">Global</div>
                                        </div>
                                        
                                        <div>
                                            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Deadline</div>
                                            <div id="programDetailsDeadline" style="font-weight: 600; color: #1e293b;">Rolling</div>
                                        </div>
                                    </div>

                                    <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
                                        <button id="referFromDetailsBtn" class="btn-primary" style="width: 100%; justify-content: center; padding: 1rem;">
                                            <i class="fa-solid fa-share-nodes"></i> Refer a Startup
                                        </button>
                                    </div>

                                    <!-- Referral Link Section -->
                                    <div style="margin-top: 1.5rem; padding: 1.5rem; background: white; border-radius: 12px; border: 2px dashed #e2e8f0;">
                                        <h4 style="font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem;">
                                            <i class="fa-solid fa-link"></i> Your Referral Link
                                        </h4>
                                        <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">Share this link with startups to track referrals:</p>
                                        
                                        <div style="display: flex; gap: 0.5rem;">
                                            <input type="text" id="programReferralLink" readonly 
                                                   style="flex: 1; padding: 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.85rem; background: #f8fafc; font-family: monospace;">
                                            <button onclick="copyReferralLink()" class="btn" style="padding: 0.75rem 1rem;">
                                                <i class="fa-solid fa-copy"></i>
                                            </button>
                                        </div>
                                        
                                        <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                                            <button onclick="shareViaWhatsApp()" class="btn" style="flex: 1; background: #25D366; color: white; border-color: #25D366;">
                                                <i class="fa-brands fa-whatsapp"></i> WhatsApp
                                            </button>
                                            <button onclick="shareViaEmail()" class="btn" style="flex: 1; background: #EA4335; color: white; border-color: #EA4335;">
                                                <i class="fa-solid fa-envelope"></i> Email
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- REFERRALS SECTION -->'''

# Replace the section
if programs_section_end in content:
    content = content.replace(programs_section_end, program_details_section)
    print("✅ Program details section restored")
else:
    print("❌ Could not find insertion point for program details section")

# Write the updated content
with open('templates/enabler_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File updated successfully")
print("\n📋 Changes made:")
print("1. Restored program-details section with:")
print("   - Program banner and title")
print("   - Description, eligibility, and benefits")
print("   - Sectors and quick info")
print("   - Referral link display and copy functionality")
print("   - WhatsApp and Email sharing buttons")
print("2. Profile section already has proper CSS and structure")
print("\n🔧 Next steps:")
print("1. Add JavaScript functions for referral link operations:")
print("   - copyReferralLink()")
print("   - shareViaWhatsApp()")
print("   - shareViaEmail()")
print("2. Update viewProgramDetails() to generate referral link")
print("3. Test by clicking 'View Program' on any program card")
