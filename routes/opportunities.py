# routes/opportunities.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Opportunity
import json
from datetime import datetime

bp = Blueprint("opportunities", __name__, url_prefix="/api/opportunities")


# ---------------------------------------
# CREATE OPPORTUNITY (Corporate / Admin)
# ---------------------------------------
@bp.route("/", methods=["POST"])
@login_required
def create_opportunity():
    if current_user.role not in ("corporate", "admin"):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or request.form or {}

    opp = Opportunity(
        owner_id=current_user.id,
        title=data.get("title"),
        type=data.get("type"),
        description=data.get("description"),
        eligibility=data.get("eligibility"),
        sectors=json.dumps(data.get("sectors", [])),
        target_stages=json.dumps(data.get("target_stages", [])),
        countries=json.dumps(data.get("countries", [])),
        deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
        benefits=data.get("benefits"),
        status=data.get("status", "draft"),
    )

    db.session.add(opp)
    db.session.commit()

    return jsonify(opp.to_dict()), 201


# ---------------------------------------
# UPDATE OPPORTUNITY (Owner / Admin)
# ---------------------------------------
@bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_opportunity(id):
    opp = Opportunity.query.get_or_404(id)

    if opp.owner_id != current_user.id and current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    data = request.json or request.form or {}

    # Update simple fields
    for key in ["title", "type", "description", "eligibility", "benefits", "status"]:
        if key in data:
            setattr(opp, key, data[key])

    # Update JSON fields
    if "sectors" in data:
        opp.sectors = json.dumps(data["sectors"])
    if "target_stages" in data:
        opp.target_stages = json.dumps(data["target_stages"])
    if "countries" in data:
        opp.countries = json.dumps(data["countries"])

    # Update deadline
    if data.get("deadline"):
        opp.deadline = datetime.fromisoformat(data["deadline"])

    db.session.commit()

    return jsonify(opp.to_dict())


# ---------------------------------------
# GET OPPORTUNITY DETAILS (Public)
# ---------------------------------------
@bp.route("/<int:id>", methods=["GET"])
def get_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    return jsonify(opp.to_dict())


# ---------------------------------------
# LIST + FILTER OPPORTUNITIES (Public)
# ---------------------------------------
@bp.route("/", methods=["GET"])
def list_opportunities():
    q = Opportunity.query.filter_by(status="published")

    # Filters
    sector = request.args.get("sector")
    stage = request.args.get("stage")
    country = request.args.get("country")
    owner = request.args.get("owner")

    if sector:
        q = q.filter(Opportunity.sectors.like(f"%{sector}%"))
    if stage:
        q = q.filter(Opportunity.target_stages.like(f"%{stage}%"))
    if country:
        q = q.filter(Opportunity.countries.like(f"%{country}%"))
    if owner:
        try:
            o_id = int(owner)
            q = q.filter_by(owner_id=o_id)
        except:
            pass

    # Pagination
    page = int(request.args.get("page", 1))
    per = int(request.args.get("per", 12))
    
    total_items = q.count()
    total_pages = (total_items + per - 1) // per
    
    items = q.order_by(Opportunity.created_at.desc()).offset((page - 1) * per).limit(per).all()

    items_data = []
    for i in items:
        d = i.to_dict()
        if i.owner:
            d['owner_name'] = i.owner.name
            d['owner_company'] = i.owner.company
        items_data.append(d)

    return jsonify({
        "success": True,
        "data": {
            "items": items_data,
            "pagination": {
                "page": page,
                "per_page": per,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }
    })
