# routes/startups.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Startup
import json

bp = Blueprint('startups', __name__, url_prefix='/api/startups')

@bp.route('/', methods=['POST'])
@login_required
def create_startup():
    # Only founders (or admin) can create startups
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403

    data = request.json or request.form or {}
    # required: name
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400

    s = Startup(
        founder_id=current_user.id,
        name=name,
        website=data.get('website'),
        country=data.get('country'),
        region=data.get('region'),
        sectors=json.dumps(data.get('sectors', [])),
        stage=data.get('stage'),
        team_size=data.get('team_size'),
        funding=data.get('funding'),
        problem=data.get('problem'),
        solution=data.get('solution'),
        traction=data.get('traction'),
        pitch_deck_url=data.get('pitch_deck_url'),
        demo_url=data.get('demo_url'),
        tags=json.dumps(data.get('tags', []))
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_startup(id):
    s = Startup.query.get_or_404(id)
    # only founder owner or admin
    if current_user.id != s.founder_id and current_user.role != 'admin':
        return jsonify({'error': 'forbidden'}), 403

    data = request.json or request.form or {}
    for key in ['name','website','country','region','stage','team_size','funding','problem','solution','traction','pitch_deck_url','demo_url']:
        if key in data:
            setattr(s, key, data[key])
    if 'sectors' in data:
        s.sectors = json.dumps(data['sectors'])
    if 'tags' in data:
        s.tags = json.dumps(data['tags'])
    db.session.commit()
    return jsonify(s.to_dict())

@bp.route('/<int:id>', methods=['GET'])
def get_startup(id):
    s = Startup.query.get_or_404(id)
    return jsonify(s.to_dict())

@bp.route('/', methods=['GET'])
def list_startups():
    q = Startup.query
    country = request.args.get('country')
    sector = request.args.get('sector')
    stage = request.args.get('stage')
    founder = request.args.get('founder')
    if country:
        q = q.filter_by(country=country)
    if stage:
        q = q.filter_by(stage=stage)
    if founder:
        try:
            f_id = int(founder)
            q = q.filter_by(founder_id=f_id)
        except:
            pass
    if sector:
        q = q.filter(Startup.sectors.like(f'%{sector}%'))
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 50))
    items = q.offset(start).limit(limit).all()
    return jsonify([i.to_dict() for i in items])

@bp.route('/mine', methods=['GET'])
@login_required
def list_my_startups():
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403
    
    startups = Startup.query.filter_by(founder_id=current_user.id).all()
    return jsonify({
        "success": True,
        "startups": [s.to_dict() for s in startups]
    })
