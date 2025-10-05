from flask import Blueprint, request, jsonify
from models.base import db
from models.issue import Issue
from models.event import Event
from datetime import datetime

issues_bp = Blueprint('issues', __name__)


@issues_bp.route('/', methods=['GET'])
def get_issues():
    """Get all issues"""
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    return jsonify([issue.to_dict() for issue in issues])


@issues_bp.route('/<int:issue_id>', methods=['GET'])
def get_issue(issue_id):
    """Get single issue"""
    issue = Issue.query.get_or_404(issue_id)
    return jsonify(issue.to_dict())


@issues_bp.route('/', methods=['POST'])
def create_issue():
    """Create new issue"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    issue = Issue(
        title=data['title'],
        type=data.get('type', 'BUG'),
        created_by=data.get('created_by', 'user')
    )

    db.session.add(issue)
    db.session.flush()

    event = Event(
        issue_id=issue.id,
        type='IssueCreated',
        actor=data.get('created_by', 'user'),
        payload_json={'title': data['title'], 'type': data.get('type', 'BUG')}
    )
    db.session.add(event)
    db.session.commit()

    return jsonify(issue.to_dict()), 201


@issues_bp.route('/<int:issue_id>', methods=['DELETE'])
def delete_issue(issue_id):
    """Delete an issue"""
    issue = Issue.query.get_or_404(issue_id)
    
    # Delete associated events first
    Event.query.filter_by(issue_id=issue_id).delete()
    
    # Delete the issue
    db.session.delete(issue)
    db.session.commit()
    
    return jsonify({'message': 'Issue deleted successfully'}), 200


@issues_bp.route('/<int:issue_id>/events', methods=['GET'])
def get_issue_events(issue_id):
    """Get all events for an issue"""
    issue = Issue.query.get_or_404(issue_id)
    events = Event.query.filter_by(issue_id=issue_id).order_by(Event.ts.asc()).all()
    return jsonify([event.to_dict() for event in events])


@issues_bp.route('/<int:issue_id>/transition', methods=['POST'])
def transition_issue(issue_id):
    """Transition issue to new state"""
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json()

    if not data or not data.get('to'):
        return jsonify({'error': 'Target state is required'}), 400

    old_state = issue.state
    new_state = data['to']

    valid_transitions = {
        'New': ['Active'],
        'Active': ['Resolved'],
        'Resolved': ['Closed'],
        'Closed': ['Active'],
        'Removed': []
    }

    if new_state not in valid_transitions.get(old_state, []):
        return jsonify({'error': f'Invalid transition from {old_state} to {new_state}'}), 400

    issue.state = new_state
    issue.updated_at = datetime.utcnow()

    event = Event(
        issue_id=issue_id,
        type='StateChanged',
        actor=data.get('actor', 'user'),
        payload_json={'from': old_state, 'to': new_state}
    )
    db.session.add(event)
    db.session.commit()

    return jsonify(issue.to_dict())


@issues_bp.route('/<int:issue_id>/ai-fix', methods=['POST'])
def trigger_ai_fix(issue_id):
    """Trigger AI fix for issue - runs complete workflow with all 3 sponsors"""
    from services.ai_service import start_ai_fix

    issue = Issue.query.get_or_404(issue_id)

    if issue.state != 'Active':
        return jsonify({'error': 'Issue must be in Active state for AI fix'}), 400

    # Log AI fix requested
    event = Event(
        issue_id=issue_id,
        type='AIFixRequested',
        actor='user',
        payload_json={'title': issue.title}
    )
    db.session.add(event)
    db.session.commit()

    # Run AI fix workflow (Cerebras + Llama + MCP)
    result = start_ai_fix(issue_id, issue.title)

    # If successful, transition to Resolved
    if result.get('success'):
        issue.state = 'Resolved'
        issue.updated_at = datetime.utcnow()

        state_event = Event(
            issue_id=issue_id,
            type='StateChanged',
            actor='ai-system',
            payload_json={'from': 'Active', 'to': 'Resolved', 'reason': 'AI fix completed'}
        )
        db.session.add(state_event)
        db.session.commit()

    return jsonify({
        'success': result.get('success'),
        'message': result.get('message'),
        'issue': issue.to_dict()
    })
