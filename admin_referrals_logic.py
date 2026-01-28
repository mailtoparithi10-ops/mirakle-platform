
# Add this to the imports in routes/admin.py if not already present, 
# although they seem to be there based on previous `view_file`.
# We need to make sure we import User, Startup, Opportunity, Referral from models.

# Add this new route to routes/admin.py
@bp.route("/referrals", methods=["GET"])
@login_required
def get_referrals():
    if require_admin():
        return require_admin()

    referrals = Referral.query.order_by(Referral.created_at.desc()).all()
    results = []
    
    for ref in referrals:
        connector = User.query.get(ref.connector_id)
        startup = Startup.query.get(ref.startup_id)
        program = Opportunity.query.get(ref.opportunity_id)
        
        # Safe access in case validation failed or records were deleted
        connector_name = connector.name if connector else "Unknown"
        startup_name = startup.company_name if startup else "Unknown" 
        program_title = program.title if program else "Unknown"
        
        results.append({
            "id": ref.id,
            "connector_name": connector_name,
            "startup_name": startup_name,
            "program_title": program_title,
            "status": ref.status,
            "created_at": ref.created_at.isoformat()
        })

    return jsonify({"success": True, "referrals": results})
