import { useState, useEffect } from 'react';
import { getEvents, getIssue, type Event, type Issue } from '../api/issues';

interface Props {
  issueId: number;
  onBack: () => void;
}

export default function EventTrail({ issueId, onBack }: Props) {
  const [events, setEvents] = useState<Event[]>([]);
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [issueId]);

  async function loadData() {
    try {
      setLoading(true);
      const [eventsData, issueData] = await Promise.all([
        getEvents(issueId),
        getIssue(issueId)
      ]);
      setEvents(eventsData);
      setIssue(issueData);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  }

  function formatTimestamp(ts: string) {
    const date = new Date(ts);
    return date.toLocaleString();
  }

  function renderEventDetails(event: Event) {
    switch (event.type) {
      case 'IssueCreated':
        return (
          <div className="event-details">
            <p><strong>Title:</strong> {event.payload?.title}</p>
            <p><strong>Type:</strong> {event.payload?.type}</p>
          </div>
        );

      case 'StateChanged':
        return (
          <div className="event-details">
            <p>
              <strong>State changed:</strong> {event.payload?.from} → {event.payload?.to}
            </p>
            {event.payload?.reason && (
              <p><strong>Reason:</strong> {event.payload.reason}</p>
            )}
          </div>
        );

      case 'AnalysisComplete':
        return (
          <div className="event-details">
            <p><strong>AI Analysis (Cerebras):</strong></p>
            <pre className="analysis-text">{event.payload?.analysis}</pre>
            <p><strong>Likely Cause:</strong> {event.payload?.likely_cause}</p>
            <p><strong>Affected Files:</strong> {event.payload?.affected_files?.join(', ')}</p>
            {event.payload?.mock && (
              <span className="badge badge-warning">Mock Data</span>
            )}
          </div>
        );

      case 'PatchProposed':
        return (
          <div className="event-details">
            <p><strong>Code Patch (Llama via MCP):</strong></p>
            <pre className="patch-code">{event.payload?.patch}</pre>
            <p><strong>Files Modified:</strong> {event.payload?.files_modified?.join(', ')}</p>
            <p>
              <strong>Tests:</strong>{' '}
              <span className="badge badge-success">
                {event.payload?.test_results?.passed?.length || 0} passed
              </span>{' '}
              <span className="badge badge-danger">
                {event.payload?.test_results?.failed?.length || 0} failed
              </span>
            </p>
            {event.payload?.mock && (
              <span className="badge badge-warning">Mock Data</span>
            )}
          </div>
        );

      case 'PatchValidated':
        return (
          <div className="event-details">
            <p><strong>Validation Status:</strong> {event.payload?.status}</p>
            <p><strong>Recommendation:</strong> {event.payload?.recommendation}</p>
            <p>
              <strong>Tests Passed:</strong>{' '}
              {event.payload?.tests_passed?.join(', ') || 'None'}
            </p>
          </div>
        );

      case 'AIFixRequested':
        return (
          <div className="event-details">
            <p>AI fix workflow started for: <strong>{event.payload?.title}</strong></p>
          </div>
        );

      default:
        return (
          <div className="event-details">
            <pre>{JSON.stringify(event.payload, null, 2)}</pre>
          </div>
        );
    }
  }

  const eventIcons: Record<string, string> = {
    'IssueCreated': '📝',
    'StateChanged': '🔄',
    'AIFixRequested': '🤖',
    'AnalysisComplete': '🧠',
    'PatchProposed': '📋',
    'PatchValidated': '✅',
    'AIFixFailed': '❌'
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading events...</p>
      </div>
    );
  }

  return (
    <div className="event-trail-container">
      <div className="event-trail-header">
        <button onClick={onBack} className="btn-back">← Back to Board</button>
        <div>
          <h1>Event Trail</h1>
          {issue && (
            <p className="issue-title-small">
              Issue #{issue.id}: {issue.title}
            </p>
          )}
        </div>
      </div>

      <div className="events-timeline">
        {events.map((event, index) => (
          <div key={event.id} className={`event-item event-${event.type.toLowerCase()}`}>
            <div className="event-marker">
              <span className="event-icon">{eventIcons[event.type] || '•'}</span>
              {index < events.length - 1 && <div className="event-line"></div>}
            </div>
            <div className="event-content">
              <div className="event-header-row">
                <h3 className="event-type">{event.type}</h3>
                <span className="event-time">{formatTimestamp(event.ts)}</span>
              </div>
              <p className="event-actor">by {event.actor}</p>
              {renderEventDetails(event)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
