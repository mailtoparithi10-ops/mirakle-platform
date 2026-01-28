from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Notification
from extensions import db

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify({
        "success": True,
        "notifications": [n.to_dict() for n in notifs]
    })

@bp.route('/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.get_or_404(id)
    if notif.user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    
    notif.is_read = True
    db.session.commit()
    return jsonify({"success": True})
