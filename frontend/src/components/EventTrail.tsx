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

  function parseContent(rawContent: string): string {
    if (!rawContent) return '';

    try {
      const jsonString = rawContent.replace(/'/g, '"').replace(/False/g, 'false').replace(/True/g, 'true');
      const parsed = JSON.parse(jsonString);
      if (parsed.content && Array.isArray(parsed.content)) {
        return parsed.content
          .map((item: any) => item.text || '')
          .join('\n\n')
          .trim();
      }
      return rawContent;
    } catch {
      const contentMatch = rawContent.match(/'text':\s*'([^']+(?:''[^']+)*)'/);
      if (contentMatch) {
        return contentMatch[1]
          .replace(/''/g, "'")
          .replace(/\\n/g, '\n')
          .trim();
      }

      const textPattern = /"text":\s*"([^"\\]*(?:\\.[^"\\]*)*)"/g;
      const matches = [...rawContent.matchAll(textPattern)];
      if (matches.length > 0) {
        return matches
          .map(m => m[1].replace(/\\n/g, '\n').replace(/\\"/g, '"'))
          .join('\n\n')
          .trim();
      }

      return rawContent;
    }
  }

  function formatAnalysis(rawAnalysis: string) {
    const cleanedText = parseContent(rawAnalysis);
    const lines = cleanedText.split('\n').map(line => line.trim()).filter(line => line);

    const sections: { title: string; content: string[] }[] = [];
    let currentSection: { title: string; content: string[] } | null = null;

    lines.forEach(line => {
      const sectionMatch = line.match(/^(ROOT CAUSE|LIKELY CAUSE|AFFECTED FILES|SUGGESTED APPROACH|FIX APPROACH|FIX|SOLUTION|ANALYSIS|RECOMMENDATION):\s*(.*)$/i);

      if (sectionMatch) {
        if (currentSection && currentSection.content.length > 0) {
          sections.push(currentSection);
        }
        currentSection = {
          title: sectionMatch[1].toUpperCase(),
          content: sectionMatch[2] ? [sectionMatch[2]] : []
        };
      } else if (currentSection) {
        currentSection.content.push(line);
      } else {
        if (!sections.length || sections[sections.length - 1].title !== 'OVERVIEW') {
          currentSection = { title: 'OVERVIEW', content: [line] };
        } else {
          sections[sections.length - 1].content.push(line);
        }
      }
    });

    if (currentSection && currentSection.content.length > 0) {
      sections.push(currentSection);
    }

    if (sections.length === 0) {
      return (
        <div className="formatted-analysis">
          <div className="analysis-section">
            <div className="section-content">
              <p>{cleanedText}</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="formatted-analysis">
        {sections.map((section, idx) => (
          <div key={idx} className="analysis-section">
            <h4 className="section-title">{section.title}</h4>
            <div className="section-content">
              {section.content.map((text, i) => (
                <p key={i}>{text}</p>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  function formatPatch(rawPatch: string) {
    const cleanedPatch = parseContent(rawPatch);
    const lines = cleanedPatch.split('\n');

    return (
      <div className="formatted-patch">
        {lines.map((line, idx) => {
          let className = 'patch-line';
          if (line.startsWith('---') || line.startsWith('+++')) {
            className += ' patch-header';
          } else if (line.startsWith('+') && !line.startsWith('+++')) {
            className += ' patch-addition';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            className += ' patch-deletion';
          } else if (line.startsWith('@@')) {
            className += ' patch-meta';
          }

          return (
            <div key={idx} className={className}>
              <code>{line || '\u00A0'}</code>
            </div>
          );
        })}
      </div>
    );
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
            <div className="detail-header">
              <h3>AI Analysis (Cerebras)</h3>
              {event.payload?.mock && (
                <span className="badge badge-warning">Mock Data</span>
              )}
            </div>
            {formatAnalysis(event.payload?.analysis || '')}
            {event.payload?.affected_files && event.payload.affected_files.length > 0 && (
              <div className="affected-files-section">
                <h4>Affected Files:</h4>
                <ul className="file-list">
                  {event.payload.affected_files.map((file: string, idx: number) => (
                    <li key={idx}><code>{file}</code></li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'PatchProposed':
        return (
          <div className="event-details">
            <div className="detail-header">
              <h3>Code Patch (Llama via MCP)</h3>
              {event.payload?.mock && (
                <span className="badge badge-warning">Mock Data</span>
              )}
            </div>
            {formatPatch(event.payload?.patch || '')}
            <div className="patch-meta-info">
              {event.payload?.files_modified && event.payload.files_modified.length > 0 && (
                <div className="files-modified">
                  <strong>Files Modified:</strong>
                  <ul className="file-list">
                    {event.payload.files_modified.map((file: string, idx: number) => (
                      <li key={idx}><code>{file}</code></li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="test-results">
                <strong>Test Results:</strong>
                <div className="test-badges">
                  <span className="badge badge-success">
                    {event.payload?.test_results?.passed?.length || 0} PASSED
                  </span>
                  <span className="badge badge-danger">
                    {event.payload?.test_results?.failed?.length || 0} FAILED
                  </span>
                </div>
              </div>
            </div>
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
