"""
Issues API routes (placeholder for main Jerai functionality)
"""

from flask import Blueprint

issues_bp = Blueprint('issues', __name__)

@issues_bp.route('/', methods=['GET'])
def get_issues():
    """Get all issues (placeholder)"""
    return {"issues": [], "message": "Issues API not implemented yet"}
