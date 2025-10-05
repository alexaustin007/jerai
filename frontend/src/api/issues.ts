// API client for backend communication

const API_BASE = import.meta.env.VITE_API_BASE ||
  (window.location.hostname.includes('vercel.app') || window.location.hostname.includes('jerai.vercel.app')
    ? 'https://backend-production-f113.up.railway.app'
    : 'http://localhost:8000');

export interface Issue {
  id: number;
  title: string;
  type: 'BUG' | 'STORY' | 'TASK';
  state: 'New' | 'Active' | 'Resolved' | 'Closed' | 'Removed';
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: number;
  issue_id: number;
  type: string;
  actor: string;
  payload: any;
  ts: string;
}

// Get all issues
export async function getIssues(): Promise<Issue[]> {
  const response = await fetch(`${API_BASE}/api/issues/`);
  if (!response.ok) throw new Error('Failed to fetch issues');
  return response.json();
}

// Get single issue
export async function getIssue(id: number): Promise<Issue> {
  const response = await fetch(`${API_BASE}/api/issues/${id}`);
  if (!response.ok) throw new Error('Failed to fetch issue');
  return response.json();
}

// Create issue
export async function createIssue(title: string, type: string = 'BUG'): Promise<Issue> {
  const response = await fetch(`${API_BASE}/api/issues/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, type, created_by: 'user' })
  });
  if (!response.ok) throw new Error('Failed to create issue');
  return response.json();
}

// Transition issue state
export async function transition(issueId: number, toState: string): Promise<Issue> {
  const response = await fetch(`${API_BASE}/api/issues/${issueId}/transition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to: toState, actor: 'user' })
  });
  if (!response.ok) throw new Error('Failed to transition issue');
  return response.json();
}

// Trigger AI fix
export async function aiFix(issueId: number): Promise<any> {
  const response = await fetch(`${API_BASE}/api/issues/${issueId}/ai-fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!response.ok) throw new Error('Failed to trigger AI fix');
  return response.json();
}

// Get events for issue
export async function getEvents(issueId: number): Promise<Event[]> {
  const response = await fetch(`${API_BASE}/api/issues/${issueId}/events`);
  if (!response.ok) throw new Error('Failed to fetch events');
  return response.json();
}

// Delete issue
export async function deleteIssue(issueId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/issues/${issueId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!response.ok) throw new Error('Failed to delete issue');
}