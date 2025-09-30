-- Jerai Database Schema
-- Creates issues and events tables (minimal schema)

CREATE DATABASE IF NOT EXISTS jerai;
USE jerai;

-- Issues table (bug tickets like Jira)
CREATE TABLE IF NOT EXISTS issues (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(500) NOT NULL,
  type ENUM('BUG','STORY','TASK') NOT NULL DEFAULT 'BUG',
  state ENUM('New','Active','Resolved','Closed','Removed') NOT NULL DEFAULT 'New',
  created_by VARCHAR(64) NOT NULL DEFAULT 'system',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_state (state),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Events table (audit trail for all actions)
-- All AI outputs (patches, analysis, test results) stored in payload_json
CREATE TABLE IF NOT EXISTS events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  issue_id BIGINT NOT NULL,
  type VARCHAR(64) NOT NULL,
  actor VARCHAR(64) NOT NULL DEFAULT 'system',
  payload_json JSON NULL,
  ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
  INDEX idx_issue_id (issue_id),
  INDEX idx_type (type),
  INDEX idx_ts (ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;