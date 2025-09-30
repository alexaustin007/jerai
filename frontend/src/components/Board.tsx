// Kanban board component with columns for each issue state

import { useState, useEffect } from 'react';
import { getIssues, createIssue, type Issue } from '../api/issues';
import IssueCard from './IssueCard';

export default function Board() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newIssueTitle, setNewIssueTitle] = useState('');

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
    { state: 'Active', color: '#f39c12', icon: 'ACTIVE' },
    { state: 'Resolved', color: '#27ae60', icon: 'DONE' },
    { state: 'Closed', color: '#34495e', icon: 'CLOSED' }
  ];

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
        <h1>Jerai - AI Bug Tracker</h1>
        <button
          className="btn-create"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          + Create Issue
        </button>
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