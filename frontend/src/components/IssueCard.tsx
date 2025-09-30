// Issue card component with action buttons

import { useState } from 'react';
import { transition, aiFix, type Issue } from '../api/issues';

interface Props {
  issue: Issue;
  onUpdate: () => void;
}

export default function IssueCard({ issue, onUpdate }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleActivate() {
    try {
      setError(null);
      await transition(issue.id, 'Active');
      onUpdate();
    } catch (err) {
      setError('Failed to activate issue');
      console.error(err);
    }
  }

  async function handleAIFix() {
    try {
      setLoading(true);
      setError(null);
      await aiFix(issue.id);
      onUpdate();
    } catch (err) {
      setError('AI fix failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // Get type badge color
  const typeColor = {
    BUG: '#e74c3c',
    STORY: '#3498db',
    TASK: '#95a5a6'
  }[issue.type] || '#95a5a6';

  return (
    <div className="issue-card">
      <div className="issue-header">
        <span className="issue-id">#{issue.id}</span>
        <span className="issue-type" style={{ backgroundColor: typeColor }}>
          {issue.type}
        </span>
      </div>

      <p className="issue-title">{issue.title}</p>

      <div className="issue-meta">
        <small>Created by {issue.created_by}</small>
      </div>

      <div className="issue-actions">
        {issue.state === 'New' && (
          <button onClick={handleActivate} className="btn-primary">
            Activate
          </button>
        )}

        {issue.state === 'Active' && (
          <button
            onClick={handleAIFix}
            disabled={loading}
            className="btn-ai"
          >
            {loading ? 'Fixing...' : 'AI Fix'}
          </button>
        )}

        <a href={`#/issues/${issue.id}/events`} className="btn-link">
          Events
        </a>
      </div>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
}