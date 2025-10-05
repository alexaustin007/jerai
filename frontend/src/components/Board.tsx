// Kanban board component with columns for each issue state

import { useState, useEffect } from 'react';
import { getIssues, createIssue, type Issue } from '../api/issues';
import IssueCard from './IssueCard';
import EventTrail from './EventTrail';

export default function Board() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newIssueTitle, setNewIssueTitle] = useState('');
  const [selectedIssueId, setSelectedIssueId] = useState<number | null>(null);

  useEffect(() => {
    loadIssues();
  }, []);

  async function loadIssues() {
    try {
      setLoading(true);
      const data = await getIssues();
      setIssues(data);
    } catch (error) {
      console.error('Failed to load issues:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateIssue(e: React.FormEvent) {
    e.preventDefault();
    if (!newIssueTitle.trim()) return;

    try {
      await createIssue(newIssueTitle, 'BUG');
      setNewIssueTitle('');
      setShowCreateForm(false);
      loadIssues();
    } catch (error) {
      console.error('Failed to create issue:', error);
    }
  }

  const columns = [
    { state: 'New', color: '#95a5a6', icon: 'NEW' },
    { state: 'Active', color: '#1966e3', icon: 'ACTIVE' },
    { state: 'Resolved', color: '#f39c12', icon: 'DONE' },
    { state: 'Closed', color: '#48bd00', icon: 'CLOSED' }
  ];

  // Show event trail if an issue is selected
  if (selectedIssueId !== null) {
    return (
      <EventTrail
        issueId={selectedIssueId}
        onBack={() => setSelectedIssueId(null)}
      />
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading issues...</p>
      </div>
    );
  }

  return (
    <div className="board-container">
      <div className="board-header">
        <h1>Jerai - AI that solves your backlog, not just bugs</h1>
        <div className="header-links">
          <a 
            href="https://jerai-creb.vercel.app/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="ecommerce-link"
          >
            🛒 Buggy E-commerce Website
          </a>
          <button
            className="btn-create"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            + Create Issue
          </button>
        </div>
      </div>

      {showCreateForm && (
        <form className="create-form" onSubmit={handleCreateIssue}>
          <input
            type="text"
            placeholder="Enter bug description..."
            value={newIssueTitle}
            onChange={(e) => setNewIssueTitle(e.target.value)}
            autoFocus
          />
          <div className="form-actions">
            <button type="submit" className="btn-primary">Create</button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="board">
        {columns.map(column => {
          const columnIssues = issues.filter(issue => issue.state === column.state);

          return (
            <div key={column.state} className="column">
              <div className="column-header" style={{ borderTopColor: column.color }}>
                <span className="column-icon">{column.icon}</span>
                <h2>{column.state}</h2>
                <span className="column-count">{columnIssues.length}</span>
              </div>

              <div className="column-content">
                {columnIssues.length === 0 ? (
                  <div className="empty-state">No issues</div>
                ) : (
                  columnIssues.map(issue => (
                    <IssueCard
                      key={issue.id}
                      issue={issue}
                      onUpdate={loadIssues}
                      onShowEvents={() => setSelectedIssueId(issue.id)}
                    />
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}