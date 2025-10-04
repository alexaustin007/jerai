# JERAI - Detailed Execution Plan

> **Current Status**: Project structure exists, but most files are placeholders
> **Goal**: Build working AI-powered bug tracker for hackathon demo
> **Timeline**: 8-12 hours total implementation

---

## 🎯 Project Status Overview

### ✅ Already Complete
- [x] Project structure created
- [x] CLAUDE.md instructions file
- [x] IMPLEMENTATION.md architecture doc
- [x] Backend app.py entry point
- [x] Frontend basic structure
- [x] Git repository initialized

### ⚠️ Needs Implementation (Most files are placeholders)
- [ ] Database schema and seed data
- [ ] Backend models (Issue, Event)
- [ ] Backend services (AI service, Issue service)
- [ ] Backend routes (issues, transitions, ai_fix)
- [ ] MCP Agent implementation
- [ ] Frontend components
- [ ] Docker setup
- [ ] Environment configuration

---

## 📋 Phase 1: Foundation Setup (1-2 hours)

### Step 1.1: Environment Configuration
**Files to create/update:**
- `.env` (copy from .env.example and add real keys)

**Actions:**
```bash
# Create .env file with real values
cp .env.example .env

# Add to .env:
# CEREBRAS_API_KEY=<get from https://cerebras.ai>
# MYSQL_HOST=mysql
# MYSQL_PORT=3306
# MYSQL_DATABASE=jerai
# MYSQL_USER=jerai
# MYSQL_PASSWORD=jerai_pass
# MYSQL_ROOT_PASSWORD=root_pass
# FLASK_ENV=development
# DATABASE_URL=mysql+pymysql://jerai:jerai_pass@mysql:3306/jerai
# MCP_GATEWAY_URL=http://mcp-gateway:3000
# VITE_API_BASE=http://localhost:8000
```

**Status:** ⚠️ Placeholder exists, needs real configuration
**Priority:** CRITICAL (blocks everything else)

---

### Step 1.2: Docker Compose Setup
**File:** `docker-compose.yml`

**Current Status:** Placeholder file exists
**Needs:** Full service definitions

**Implementation:**
```yaml
version: '3.9'

services:
  mysql:
    image: mysql:8.4
    container_name: jerai-mysql
    environment:
      MYSQL_DATABASE: jerai
      MYSQL_USER: jerai
      MYSQL_PASSWORD: jerai_pass
      MYSQL_ROOT_PASSWORD: root_pass
    volumes:
      - ./db/init:/docker-entrypoint-initdb.d:ro
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: jerai-backend
    environment:
      DATABASE_URL: mysql+pymysql://jerai:jerai_pass@mysql:3306/jerai
      CEREBRAS_API_KEY: ${CEREBRAS_API_KEY}
      MCP_GATEWAY_URL: http://mcp-gateway:3000
      FLASK_ENV: development
    volumes:
      - ./backend:/app
    depends_on:
      mysql:
        condition: service_healthy
      mcp-gateway:
        condition: service_started
    ports:
      - "8000:8000"

  mcp-gateway:
    image: mcp/gateway:latest
    container_name: jerai-mcp-gateway
    environment:
      MCP_SERVER_URL: http://mcp_agent:9000
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - mcp_agent
    ports:
      - "3000:3000"

  mcp_agent:
    build: ./mcp_agent
    container_name: jerai-mcp-agent
    environment:
      CEREBRAS_API_KEY: ${CEREBRAS_API_KEY}
    volumes:
      - ./backend/ecommerce:/workspace:ro
      - ./backend/tests:/tests:ro
    ports:
      - "9000:9000"

  frontend:
    build: ./frontend
    container_name: jerai-frontend
    environment:
      VITE_API_BASE: http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
    depends_on:
      - backend
    ports:
      - "5173:5173"

volumes:
  mysql_data:
```

**Validation:**
```bash
docker compose config  # Validate syntax
```

**Priority:** CRITICAL
**Estimated Time:** 30 minutes

---

### Step 1.3: Database Schema
**Files:**
- `db/init/01_schema.sql`
- `db/init/02_seed.sql`

**Current Status:** Placeholder files exist
**Needs:** SQL statements

**Implementation for 01_schema.sql:**
```sql
-- db/init/01_schema.sql
-- Creates issues and events tables (minimal schema)

CREATE DATABASE IF NOT EXISTS jerai;
USE jerai;

-- Issues table (bug tickets)
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
```

**Implementation for 02_seed.sql:**
```sql
-- db/init/02_seed.sql
-- Seeds demo bug (cart rounding issue)

USE jerai;

-- Insert demo bug
INSERT INTO issues (title, type, state, created_by)
VALUES ('Cart shows $21.52, should be $21.53 after discount + tax', 'BUG', 'New', 'demo');

-- Log creation event
INSERT INTO events (issue_id, type, actor, payload_json)
VALUES (
  1,
  'IssueCreated',
  'demo',
  JSON_OBJECT(
    'description', 'Float rounding error in cart.py compute_total() function',
    'expected', '$21.53 (2153 cents)',
    'actual', '$21.52 or $21.54'
  )
);
```

**Validation:**
```bash
# Test SQL syntax
mysql -u root -p < db/init/01_schema.sql
mysql -u root -p < db/init/02_seed.sql
```

**Priority:** CRITICAL
**Estimated Time:** 20 minutes

---

## 📋 Phase 2: Backend Core (2-3 hours)

### Step 2.1: Database Models
**Files:**
- `backend/models/base.py`
- `backend/models/issue.py`
- `backend/models/event.py`

**Current Status:** Placeholders exist

**Implementation for base.py:**
```python
# backend/models/base.py
"""
SQLAlchemy base configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://jerai:jerai_pass@localhost:3306/jerai')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL debugging
)

# Session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base class for all models
Base = declarative_base()

def init_db(app=None):
    """Initialize database connection"""
    # Import all models here to register them with SQLAlchemy
    from models.issue import Issue
    from models.event import Event

    # Create all tables (if not exists)
    Base.metadata.create_all(bind=engine)

    return engine

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Implementation for issue.py:**
```python
# backend/models/issue.py
"""
Issue model (bug tickets)
"""

from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, func
from models.base import Base
import enum

class IssueType(enum.Enum):
    BUG = "BUG"
    STORY = "STORY"
    TASK = "TASK"

class IssueState(enum.Enum):
    NEW = "New"
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    REMOVED = "Removed"

class Issue(Base):
    __tablename__ = 'issues'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    type = Column(Enum(IssueType), nullable=False, default=IssueType.BUG)
    state = Column(Enum(IssueState), nullable=False, default=IssueState.NEW)
    created_by = Column(String(64), nullable=False, default='system')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type.value,
            'state': self.state.value,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

**Implementation for event.py:**
```python
# backend/models/event.py
"""
Event model (audit trail)
"""

from sqlalchemy import Column, BigInteger, String, JSON, TIMESTAMP, ForeignKey, func
from models.base import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    issue_id = Column(BigInteger, ForeignKey('issues.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False, default='system')
    payload_json = Column(JSON, nullable=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'type': self.type,
            'actor': self.actor,
            'payload': self.payload_json,
            'ts': self.ts.isoformat() if self.ts else None
        }
```

**Priority:** CRITICAL
**Estimated Time:** 45 minutes

---

### Step 2.2: Issue Service (State Machine)
**File:** `backend/services/issue_service.py`

**Current Status:** May exist partially
**Needs:** State transition logic

**Implementation:**
```python
# backend/services/issue_service.py
"""
Issue service - handles state machine transitions
"""

from models.issue import Issue, IssueState
from models.event import Event
from sqlalchemy.orm import Session
from typing import Optional

# State machine: allowed transitions
ALLOWED_TRANSITIONS = {
    IssueState.NEW: {IssueState.ACTIVE},
    IssueState.ACTIVE: {IssueState.RESOLVED},
    IssueState.RESOLVED: {IssueState.CLOSED},
    IssueState.CLOSED: set(),
    IssueState.REMOVED: set()
}

class StateTransitionError(Exception):
    """Raised when invalid state transition attempted"""
    pass

def transition_issue(db: Session, issue_id: int, to_state: str, actor: str = 'system') -> Issue:
    """
    Transition issue to new state (enforces state machine)

    Args:
        db: Database session
        issue_id: Issue ID
        to_state: Target state string (e.g., 'Active')
        actor: Who initiated the transition

    Returns:
        Updated Issue object

    Raises:
        StateTransitionError: If transition is not allowed
    """
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise ValueError(f"Issue {issue_id} not found")

    # Parse target state
    try:
        target_state = IssueState(to_state)
    except ValueError:
        raise ValueError(f"Invalid state: {to_state}")

    # Check if transition is allowed
    current_state = issue.state
    if target_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
        raise StateTransitionError(
            f"Cannot transition from {current_state.value} to {target_state.value}"
        )

    # Update issue state
    issue.state = target_state
    db.add(issue)

    # Log event
    event = Event(
        issue_id=issue_id,
        type=f"StateChanged({current_state.value}→{target_state.value})",
        actor=actor,
        payload_json=None
    )
    db.add(event)

    db.commit()
    db.refresh(issue)

    return issue

def create_issue(db: Session, title: str, type: str = 'BUG', created_by: str = 'user') -> Issue:
    """Create new issue"""
    issue = Issue(title=title, type=type, created_by=created_by)
    db.add(issue)
    db.commit()
    db.refresh(issue)

    # Log creation event
    event = Event(
        issue_id=issue.id,
        type='IssueCreated',
        actor=created_by,
        payload_json={'title': title, 'type': type}
    )
    db.add(event)
    db.commit()

    return issue

def get_issue_events(db: Session, issue_id: int) -> list:
    """Get all events for an issue"""
    events = db.query(Event).filter(Event.issue_id == issue_id).order_by(Event.ts).all()
    return [e.to_dict() for e in events]
```

**Priority:** CRITICAL
**Estimated Time:** 45 minutes

---

### Step 2.3: AI Service (3 Sponsors Integration)
**File:** `backend/services/ai_service.py`

**Current Status:** Placeholder exists
**Needs:** Full implementation with Cerebras + MCP Gateway

**Implementation:**
```python
# backend/services/ai_service.py
"""
AI Service - integrates all 3 sponsor technologies:
1. Cerebras API (fast inference with Llama 3.3 70B)
2. Meta Llama 3.3 70B (the AI model)
3. Docker MCP Gateway (containerized agent)
"""

import os
import requests
from models.event import Event
from sqlalchemy.orm import Session

CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
CEREBRAS_API_URL = 'https://api.cerebras.ai/v1/chat/completions'
MCP_GATEWAY_URL = os.getenv('MCP_GATEWAY_URL', 'http://mcp-gateway:3000')

def ai_fix_workflow(db: Session, issue_id: int, title: str) -> dict:
    """
    Complete AI fix workflow using all 3 sponsor technologies

    Flow:
    1. CEREBRAS API: Fast bug analysis
    2. DOCKER MCP GATEWAY: Route to containerized agent
    3. MCP AGENT: Generate patch using Cerebras/Llama
    4. Validate and return results

    Args:
        db: Database session
        issue_id: Issue ID to fix
        title: Issue title (used for context)

    Returns:
        dict with status, patch, test results
    """

    # STEP 1: Log AI fix request
    db.add(Event(issue_id=issue_id, type="AIFixRequested", actor="user"))
    db.commit()

    try:
        # STEP 2: CEREBRAS - Fast bug analysis
        print(f"[Cerebras] Analyzing bug #{issue_id}...")
        analysis = analyze_with_cerebras(title)

        db.add(Event(
            issue_id=issue_id,
            type="AnalysisComplete",
            actor="cerebras",
            payload_json={"analysis": analysis}
        ))
        db.commit()
        print(f"[Cerebras] Analysis complete: {analysis[:100]}...")

        # STEP 3: DOCKER MCP GATEWAY - Route to agent
        print(f"[MCP Gateway] Requesting patch generation...")
        response = requests.post(
            f"{MCP_GATEWAY_URL}/generate-patch",
            json={
                "issue_id": issue_id,
                "title": title,
                "analysis": analysis
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        # STEP 4: Process MCP agent results
        patch_diff = result.get('patch', '')
        tests_passed = result.get('tests_passed', 0)
        tests_failed = result.get('tests_failed', 0)

        db.add(Event(
            issue_id=issue_id,
            type="PatchProposed",
            actor="llama-mcp",
            payload_json={
                "patch": patch_diff,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "summary": result.get('summary', '')
            }
        ))
        db.commit()
        print(f"[MCP Agent] Patch generated. Tests: {tests_passed} passed, {tests_failed} failed")

        # STEP 5: Validate results
        if tests_failed == 0 and patch_diff:
            db.add(Event(
                issue_id=issue_id,
                type="TestsValidated",
                actor="system",
                payload_json={"status": "success", "tests_passed": tests_passed}
            ))
            db.commit()
            return {
                "status": "success",
                "patch": patch_diff,
                "tests_passed": tests_passed,
                "analysis": analysis
            }
        else:
            db.add(Event(
                issue_id=issue_id,
                type="AIFixFailed",
                actor="system",
                payload_json={"reason": "Tests failed or no patch generated"}
            ))
            db.commit()
            return {
                "status": "failed",
                "reason": "Tests failed",
                "tests_failed": tests_failed
            }

    except Exception as e:
        print(f"[ERROR] AI fix failed: {e}")
        db.add(Event(
            issue_id=issue_id,
            type="AIFixFailed",
            actor="system",
            payload_json={"error": str(e)}
        ))
        db.commit()
        return {"status": "error", "message": str(e)}


def analyze_with_cerebras(title: str) -> str:
    """
    SPONSOR #1: CEREBRAS API
    SPONSOR #2: META LLAMA 3.3 70B

    Fast bug analysis using Llama 3.3 70B on Cerebras hardware (< 3 seconds)
    """
    if not CEREBRAS_API_KEY:
        raise ValueError("CEREBRAS_API_KEY not set in environment")

    response = requests.post(
        CEREBRAS_API_URL,
        headers={
            'Authorization': f'Bearer {CEREBRAS_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'llama-3.3-70b',  # META LLAMA 3.3 70B
            'messages': [{
                'role': 'user',
                'content': f"""Analyze this bug briefly:

Bug: {title}

Provide in 2-3 sentences:
1. Likely root cause
2. Affected files (guess based on title: cart.py, checkout.py, etc.)
3. Suggested fix approach (be specific about Python code changes)"""
            }],
            'max_tokens': 300,
            'temperature': 0.2  # Lower temperature for deterministic analysis
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
```

**Priority:** CRITICAL (sponsors #1 and #2)
**Estimated Time:** 1 hour

---

### Step 2.4: Backend Routes
**Files:**
- `backend/routes/issues.py`
- `backend/routes/transitions.py`
- `backend/routes/ai_fix.py`

**Current Status:** Placeholders exist

**Implementation for issues.py:**
```python
# backend/routes/issues.py
"""
Issue CRUD endpoints
"""

from flask import Blueprint, request, jsonify
from models.base import SessionLocal
from models.issue import Issue
from services.issue_service import create_issue, get_issue_events

issues_bp = Blueprint('issues', __name__)

@issues_bp.route('/', methods=['GET'])
def list_issues():
    """GET /api/issues - List all issues"""
    db = SessionLocal()
    try:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
        return jsonify([issue.to_dict() for issue in issues])
    finally:
        db.close()

@issues_bp.route('/', methods=['POST'])
def create_issue_endpoint():
    """POST /api/issues - Create new issue"""
    data = request.get_json()

    title = data.get('title')
    if not title:
        return jsonify({'error': 'title is required'}), 400

    issue_type = data.get('type', 'BUG')
    created_by = data.get('created_by', 'user')

    db = SessionLocal()
    try:
        issue = create_issue(db, title, issue_type, created_by)
        return jsonify(issue.to_dict()), 201
    finally:
        db.close()

@issues_bp.route('/<int:issue_id>', methods=['GET'])
def get_issue(issue_id):
    """GET /api/issues/:id - Get single issue"""
    db = SessionLocal()
    try:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            return jsonify({'error': 'Issue not found'}), 404
        return jsonify(issue.to_dict())
    finally:
        db.close()

@issues_bp.route('/<int:issue_id>/events', methods=['GET'])
def get_events(issue_id):
    """GET /api/issues/:id/events - Get issue event trail"""
    db = SessionLocal()
    try:
        events = get_issue_events(db, issue_id)
        return jsonify(events)
    finally:
        db.close()
```

**Implementation for transitions.py:**
```python
# backend/routes/transitions.py
"""
State transition endpoints
"""

from flask import Blueprint, request, jsonify
from models.base import SessionLocal
from services.issue_service import transition_issue, StateTransitionError

transitions_bp = Blueprint('transitions', __name__)

@transitions_bp.route('/<int:issue_id>/transition', methods=['POST'])
def transition_endpoint(issue_id):
    """
    POST /api/issues/:id/transition
    Body: {"to": "Active", "actor": "user"}
    """
    data = request.get_json()

    to_state = data.get('to')
    if not to_state:
        return jsonify({'error': 'to state is required'}), 400

    actor = data.get('actor', 'user')

    db = SessionLocal()
    try:
        issue = transition_issue(db, issue_id, to_state, actor)
        return jsonify(issue.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except StateTransitionError as e:
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()
```

**Implementation for ai_fix.py:**
```python
# backend/routes/ai_fix.py
"""
AI fix endpoint
"""

from flask import Blueprint, request, jsonify
from models.base import SessionLocal
from models.issue import Issue
from services.ai_service import ai_fix_workflow
from services.issue_service import transition_issue

ai_fix_bp = Blueprint('ai_fix', __name__)

@ai_fix_bp.route('/<int:issue_id>/ai-fix', methods=['POST'])
def trigger_ai_fix(issue_id):
    """
    POST /api/issues/:id/ai-fix
    Triggers complete AI fix workflow
    """
    db = SessionLocal()
    try:
        # Get issue
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            return jsonify({'error': 'Issue not found'}), 404

        # Check state (must be Active)
        if issue.state.value != 'Active':
            return jsonify({'error': 'Issue must be in Active state'}), 400

        # Run AI fix workflow
        result = ai_fix_workflow(db, issue_id, issue.title)

        # If successful, auto-resolve
        if result['status'] == 'success':
            transition_issue(db, issue_id, 'Resolved', 'system')
            # Auto-close after resolve
            transition_issue(db, issue_id, 'Closed', 'system')

        return jsonify(result)

    finally:
        db.close()
```

**Update app.py to register new blueprints:**
```python
# backend/app.py - ADD THESE IMPORTS AND REGISTRATIONS

from routes.transitions import transitions_bp
from routes.ai_fix import ai_fix_bp

# ADD AFTER OTHER BLUEPRINT REGISTRATIONS:
app.register_blueprint(transitions_bp, url_prefix='/api/issues')
app.register_blueprint(ai_fix_bp, url_prefix='/api/issues')
```

**Priority:** CRITICAL
**Estimated Time:** 1 hour

---

## 📋 Phase 3: MCP Agent Implementation (2-3 hours)

### Step 3.1: MCP Agent HTTP Server
**File:** `mcp_agent/agent.py`

**Current Status:** Placeholder exists
**Needs:** Full FastAPI implementation

**Implementation:**
```python
# mcp_agent/agent.py
"""
MCP Agent - Containerized code analysis agent
SPONSOR #3: Docker MCP Gateway integration

Provides:
- Code file search and reading
- Test execution
- Patch generation via Cerebras API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from tools import fs_tools, test_runner

app = FastAPI(title="Jerai MCP Agent", version="1.0.0")

CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
CEREBRAS_API_URL = 'https://api.cerebras.ai/v1/chat/completions'

class PatchRequest(BaseModel):
    issue_id: int
    title: str
    analysis: str

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-agent"}

@app.post("/generate-patch")
def generate_patch(req: PatchRequest):
    """
    Generate patch using Cerebras + filesystem tools

    Flow:
    1. Search for relevant files based on bug title
    2. Read file contents
    3. Call Cerebras with code context to generate patch
    4. Run tests to validate
    5. Return patch + test results
    """

    # Step 1: Extract keywords and search files
    keywords = extract_keywords(req.title)
    print(f"[MCP Agent] Searching for files with keywords: {keywords}")
    files = fs_tools.search_files(keywords, path='/workspace')

    if not files:
        raise HTTPException(status_code=404, detail="No relevant files found")

    print(f"[MCP Agent] Found {len(files)} files: {files}")

    # Step 2: Read code context (limit to 3 files)
    code_context = ""
    for file_path in files[:3]:
        content = fs_tools.read_file(file_path)
        code_context += f"\n\n=== {file_path} ===\n{content}"

    # Step 3: Call Cerebras to generate patch
    print(f"[MCP Agent] Calling Cerebras to generate patch...")
    patch_diff = call_cerebras_for_patch(req.title, req.analysis, code_context)

    # Step 4: Run tests (before applying patch, to show current state)
    print(f"[MCP Agent] Running tests...")
    test_results = test_runner.run_pytest('/tests')

    # Step 5: Return results
    return {
        "job_id": f"J-{req.issue_id}",
        "patch": patch_diff,
        "tests_passed": test_results.get('passed', 0),
        "tests_failed": test_results.get('failed', 0),
        "summary": f"Generated patch for {len(files)} files"
    }


def call_cerebras_for_patch(title: str, analysis: str, code_context: str) -> str:
    """
    Call Cerebras API with full code context to generate patch
    Uses Llama 3.3 70B for high-quality code generation
    """
    if not CEREBRAS_API_KEY:
        raise HTTPException(status_code=500, detail="CEREBRAS_API_KEY not set")

    prompt = f"""You are an expert Python debugger. Generate a minimal patch to fix this bug.

Bug: {title}

Analysis: {analysis}

Current Code:
{code_context}

Generate a unified diff patch (use --- and +++ format) that:
1. Replaces float with Decimal for money calculations
2. Fixes order of operations: (subtotal - discount) * (1 + tax_rate)
3. Adds proper rounding using integer cents

Output ONLY the diff, no explanations. Start with --- and +++."""

    response = requests.post(
        CEREBRAS_API_URL,
        headers={
            'Authorization': f'Bearer {CEREBRAS_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'llama-3.3-70b',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1000,
            'temperature': 0.2
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def extract_keywords(title: str) -> list:
    """Extract relevant keywords from bug title for file search"""
    common_words = {'the', 'a', 'an', 'is', 'are', 'for', 'by', 'with', 'after', 'shows', 'should', 'be'}
    words = title.lower().split()
    keywords = [w.strip('.,!?$') for w in words if w not in common_words and len(w) > 2]
    return keywords[:5]  # Limit to 5 most relevant


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

**Priority:** CRITICAL (sponsor #3)
**Estimated Time:** 1 hour

---

### Step 3.2: MCP Agent Tools
**Files:**
- `mcp_agent/tools/fs_tools.py`
- `mcp_agent/tools/test_runner.py`
- `mcp_agent/tools/__init__.py`

**Current Status:** Some files may exist (git_tools.py exists)

**Implementation for fs_tools.py:**
```python
# mcp_agent/tools/fs_tools.py
"""
Filesystem tools for code reading (read-only)
"""

import os
from pathlib import Path

def search_files(keywords: list, path: str = '/workspace') -> list:
    """
    Search for Python files containing any of the keywords in their name or path

    Args:
        keywords: List of keywords to search for
        path: Base path to search in

    Returns:
        List of matching file paths
    """
    matches = []
    base_path = Path(path)

    if not base_path.exists():
        return matches

    for py_file in base_path.rglob('*.py'):
        file_str = str(py_file).lower()
        if any(kw.lower() in file_str for kw in keywords):
            matches.append(str(py_file))

    return matches[:10]  # Limit results


def read_file(file_path: str) -> str:
    """
    Read file contents (safe, read-only)

    Args:
        file_path: Path to file

    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
```

**Implementation for test_runner.py:**
```python
# mcp_agent/tools/test_runner.py
"""
Test runner tool - executes pytest and returns results
"""

import subprocess
import json
import re

def run_pytest(test_path: str = '/tests') -> dict:
    """
    Run pytest and return pass/fail counts

    Args:
        test_path: Path to tests directory

    Returns:
        dict with passed, failed, total counts
    """
    try:
        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse stdout for test results
        output = result.stdout + result.stderr

        # Look for pytest summary line: "X passed in Y.YYs" or "X failed, Y passed"
        passed = 0
        failed = 0

        # Pattern: "3 passed in 0.12s"
        passed_match = re.search(r'(\d+) passed', output)
        if passed_match:
            passed = int(passed_match.group(1))

        # Pattern: "2 failed, 3 passed"
        failed_match = re.search(r'(\d+) failed', output)
        if failed_match:
            failed = int(failed_match.group(1))

        return {
            'passed': passed,
            'failed': failed,
            'total': passed + failed,
            'output': output[:500]  # Truncate for brevity
        }

    except subprocess.TimeoutExpired:
        return {'passed': 0, 'failed': 1, 'error': 'Tests timed out'}
    except Exception as e:
        return {'passed': 0, 'failed': 1, 'error': str(e)}
```

**Implementation for __init__.py:**
```python
# mcp_agent/tools/__init__.py
"""
Tools package exports
"""

from . import fs_tools
from . import test_runner

__all__ = ['fs_tools', 'test_runner']
```

**Priority:** CRITICAL
**Estimated Time:** 45 minutes

---

### Step 3.3: MCP Agent Docker Setup
**Files:**
- `mcp_agent/Dockerfile`
- `mcp_agent/requirements.txt`

**Current Status:** Placeholders exist

**Implementation for Dockerfile:**
```dockerfile
# mcp_agent/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 9000

# Run FastAPI server
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "9000"]
```

**Implementation for requirements.txt:**
```txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.6.0
requests==2.31.0
pytest==8.0.0
```

**Priority:** CRITICAL
**Estimated Time:** 15 minutes

---

## 📋 Phase 4: Demo Code & Tests (1 hour)

### Step 4.1: Demo Cart Code (Buggy)
**File:** `backend/ecommerce/cart.py`

**Current Status:** File exists (need to verify it has the bug)

**Expected Implementation:**
```python
# backend/ecommerce/cart.py

def compute_total(items, discount_pct=0.0, tax_pct=0.0):
    """
    BUG: Using float causes rounding errors

    Example: 21.98 - 10% discount + 8.875% tax
    Should be $21.53, but float math gives $21.52 or $21.54

    Args:
        items: List of dicts with 'price' (in cents) and 'qty'
        discount_pct: Discount percentage (0.0 to 1.0)
        tax_pct: Tax percentage (0.0 to 1.0)

    Returns:
        Total in cents (integer)
    """
    # Convert cents to dollars (introduces float error)
    subtotal = sum(item['price'] * item.get('qty', 1) for item in items) / 100.0

    # Calculate discount and tax
    discount = subtotal * discount_pct
    after_discount = subtotal - discount
    tax = after_discount * tax_pct
    total = after_discount + tax

    # Round back to cents (but rounding is already wrong!)
    return round(total * 100)
```

**Priority:** CRITICAL (demo code)
**Estimated Time:** 10 minutes

---

### Step 4.2: Test Case (Failing)
**File:** `backend/tests/test_cart.py`

**Current Status:** File exists (need to verify test)

**Expected Implementation:**
```python
# backend/tests/test_cart.py

import sys
sys.path.insert(0, '/workspace')  # MCP agent needs this

from cart import compute_total

def test_discount_then_tax_rounding():
    """
    Test case that fails with float math

    Items: $19.99 + $1.99 = $21.98
    Discount 10%: $21.98 * 0.90 = $19.782
    Tax 8.875%: $19.782 * 1.08875 = $21.5354...
    Correct result: $21.53 (2153 cents)

    This test FAILS with current float implementation!
    """
    items = [
        {"price": 1999, "qty": 1},  # $19.99 in cents
        {"price": 199, "qty": 1}     # $1.99 in cents
    ]

    total_cents = compute_total(items, discount_pct=0.10, tax_pct=0.08875)

    assert total_cents == 2153, f"Expected 2153 cents ($21.53), got {total_cents} cents"
```

**Priority:** CRITICAL
**Estimated Time:** 10 minutes

---

## 📋 Phase 5: Frontend Implementation (2-3 hours)

### Step 5.1: API Client
**File:** `frontend/src/api/issues.ts`

**Current Status:** File exists (likely placeholder)

**Implementation:**
```typescript
// frontend/src/api/issues.ts

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

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
```

**Priority:** CRITICAL
**Estimated Time:** 30 minutes

---

### Step 5.2: Frontend Components
**Files:**
- `frontend/src/components/Board.tsx`
- `frontend/src/components/IssueCard.tsx`
- `frontend/src/components/EventTrail.tsx`

**Current Status:** Files exist (need implementation)

**Implementation for Board.tsx:**
```tsx
// frontend/src/components/Board.tsx

import { useState, useEffect } from 'react';
import { getIssues, type Issue } from '../api/issues';
import IssueCard from './IssueCard';

export default function Board() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);

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

  const columns = ['New', 'Active', 'Resolved', 'Closed'];

  if (loading) {
    return <div className="loading">Loading issues...</div>;
  }

  return (
    <div className="board">
      {columns.map(state => (
        <div key={state} className="column">
          <h2>{state}</h2>
          <div className="issues">
            {issues
              .filter(issue => issue.state === state)
              .map(issue => (
                <IssueCard
                  key={issue.id}
                  issue={issue}
                  onUpdate={loadIssues}
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Implementation for IssueCard.tsx:**
```tsx
// frontend/src/components/IssueCard.tsx

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
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="issue-card">
      <div className="issue-header">
        <span className="issue-id">#{issue.id}</span>
        <span className="issue-type">{issue.type}</span>
      </div>

      <p className="issue-title">{issue.title}</p>

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
            {loading ? '⏳ AI Fixing...' : '🤖 AI Fix'}
          </button>
        )}

        <a href={`/issues/${issue.id}/events`} className="btn-link">
          View Events →
        </a>
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

**Implementation for EventTrail.tsx:**
```tsx
// frontend/src/components/EventTrail.tsx

import { useState, useEffect } from 'react';
import { getEvents, type Event } from '../api/issues';

interface Props {
  issueId: number;
}

export default function EventTrail({ issueId }: Props) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getEvents(issueId);
        setEvents(data);
      } catch (error) {
        console.error('Failed to load events:', error);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [issueId]);

  if (loading) {
    return <div>Loading events...</div>;
  }

  return (
    <div className="event-trail">
      <h2>Event History</h2>
      {events.length === 0 && <p>No events yet</p>}

      {events.map(event => (
        <div key={event.id} className="event">
          <div className="event-header">
            <strong>{event.type}</strong>
            <span className="event-time">
              {new Date(event.ts).toLocaleString()}
            </span>
          </div>

          {event.type === 'PatchProposed' && event.payload?.patch && (
            <div className="event-content">
              <h4>Generated Patch:</h4>
              <pre className="patch">{event.payload.patch}</pre>
              <p>
                Tests: {event.payload.tests_passed} passed, {event.payload.tests_failed} failed
              </p>
            </div>
          )}

          {event.type === 'AnalysisComplete' && event.payload?.analysis && (
            <div className="event-content">
              <h4>Cerebras Analysis:</h4>
              <p>{event.payload.analysis}</p>
            </div>
          )}

          {event.payload && !['PatchProposed', 'AnalysisComplete'].includes(event.type) && (
            <pre className="event-payload">
              {JSON.stringify(event.payload, null, 2)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
```

**Priority:** CRITICAL
**Estimated Time:** 1.5 hours

---

### Step 5.3: Frontend Docker Setup
**Files:**
- `frontend/Dockerfile`
- `frontend/vite.config.ts`

**Current Status:** vite.config.ts exists

**Implementation for Dockerfile:**
```dockerfile
# frontend/Dockerfile

FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Update vite.config.ts (if needed):**
```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
```

**Priority:** HIGH
**Estimated Time:** 15 minutes

---

## 📋 Phase 6: Integration & Testing (1-2 hours)

### Step 6.1: Backend Dockerfile
**File:** `backend/Dockerfile`

**Current Status:** May exist

**Implementation:**
```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Wait for DB and run app
CMD ["python", "app.py"]
```

**Priority:** CRITICAL
**Estimated Time:** 15 minutes

---

### Step 6.2: Backend Requirements
**File:** `backend/requirements.txt`

**Current Status:** May have partial requirements

**Complete Implementation:**
```txt
flask==3.0.3
flask-cors==4.0.0
sqlalchemy==2.0.32
pymysql==1.1.1
cryptography==42.0.0
requests==2.32.3
python-dotenv==1.0.0
pytest==8.0.0
```

**Priority:** CRITICAL
**Estimated Time:** 5 minutes

---

### Step 6.3: Full System Test
**Commands:**

```bash
# 1. Verify all files exist
ls -la db/init/
ls -la backend/models/
ls -la backend/services/
ls -la backend/routes/
ls -la mcp_agent/tools/
ls -la frontend/src/components/

# 2. Validate docker-compose
docker compose config

# 3. Build all containers
docker compose build

# 4. Start services
docker compose up

# 5. Test endpoints (in another terminal)
curl http://localhost:8000/health
curl http://localhost:8000/api/issues/
curl http://localhost:9000/health
curl http://localhost:5173/

# 6. Verify database
docker exec -it jerai-mysql mysql -u jerai -pjerai_pass -e "USE jerai; SELECT * FROM issues;"

# 7. Test AI fix workflow
curl -X POST http://localhost:8000/api/issues/1/transition \
  -H "Content-Type: application/json" \
  -d '{"to": "Active", "actor": "user"}'

curl -X POST http://localhost:8000/api/issues/1/ai-fix

# 8. Check events
curl http://localhost:8000/api/issues/1/events
```

**Priority:** CRITICAL
**Estimated Time:** 1 hour (includes debugging)

---

## 📋 Phase 7: Documentation & Demo (1 hour)

### Step 7.1: Update README.md
**File:** `README.md`

**Current Status:** Placeholder exists

**Implementation:**
```markdown
# Jerai - AI-Powered Bug Tracker

Minimal hackathon demo using Cerebras API, Meta Llama 3.3 70B, and Docker MCP Gateway.

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Add your CEREBRAS_API_KEY to .env

# 2. Run
docker compose up --build

# 3. Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## Demo Flow (15 seconds)

1. Open http://localhost:5173
2. Click "Activate" on demo bug
3. Click "AI Fix" button
4. Wait 5 seconds → bug auto-resolves
5. Click "View Events" → see patch

## Sponsor Technologies

- ✅ **Cerebras API**: Fast inference (< 3s)
- ✅ **Meta Llama 3.3 70B**: AI model
- ✅ **Docker MCP Gateway**: Container orchestration

## Architecture

- Frontend: React + TypeScript (Vite)
- Backend: Flask + MySQL
- MCP Agent: FastAPI (containerized)
- AI: Cerebras API with Llama 3.3 70B

## Prize Eligibility

All 3 sponsors integrated in `backend/services/ai_service.py` and `mcp_agent/agent.py`.
```

**Priority:** HIGH
**Estimated Time:** 20 minutes

---

### Step 7.2: Record Demo Video
**Steps:**

1. Start fresh environment
2. Record screen showing:
   - `docker compose up` command
   - Frontend loading at http://localhost:5173
   - Clicking "Activate" button
   - Clicking "AI Fix" button (show loading)
   - Bug moving to Resolved → Closed
   - Event trail showing patch
3. Keep video under 2 minutes
4. Upload to YouTube or Loom

**Priority:** CRITICAL (mandatory for hackathon)
**Estimated Time:** 30 minutes

---

## ✅ Definition of Done Checklist

### Infrastructure
- [ ] `.env` file created with real CEREBRAS_API_KEY
- [ ] `docker-compose.yml` complete with all 5 services
- [ ] All Dockerfiles created (backend, frontend, mcp_agent)
- [ ] Database init scripts complete

### Backend
- [ ] Models: base.py, issue.py, event.py
- [ ] Services: issue_service.py, ai_service.py
- [ ] Routes: issues.py, transitions.py, ai_fix.py
- [ ] app.py registers all blueprints
- [ ] requirements.txt complete

### MCP Agent
- [ ] agent.py with FastAPI server
- [ ] tools/fs_tools.py
- [ ] tools/test_runner.py
- [ ] Dockerfile and requirements.txt

### Frontend
- [ ] api/issues.ts client
- [ ] components/Board.tsx
- [ ] components/IssueCard.tsx
- [ ] components/EventTrail.tsx
- [ ] Dockerfile

### Demo Code
- [ ] backend/ecommerce/cart.py (with bug)
- [ ] backend/tests/test_cart.py (failing test)

### Integration
- [ ] `docker compose up` starts all services
- [ ] Database seeds demo bug
- [ ] Health checks pass (all services)
- [ ] Frontend renders board at :5173
- [ ] Backend API responds at :8000
- [ ] MCP agent responds at :9000

### End-to-End Flow
- [ ] Create bug (or use seeded bug)
- [ ] Activate bug → moves to Active column
- [ ] Click "AI Fix" → Cerebras analyzes bug
- [ ] MCP agent generates patch
- [ ] Bug auto-resolves and closes
- [ ] Event trail shows all steps + patch diff

### Documentation
- [ ] README.md with setup instructions
- [ ] EXECUTION_PLAN.md (this file) complete
- [ ] Comments in code showing sponsor tech usage

### Demo
- [ ] 2-minute demo video recorded
- [ ] Video shows complete workflow
- [ ] Video uploaded (YouTube/Loom)

---

## 🎯 Execution Order (Recommended)

**Day 1 (4-5 hours):**
1. Phase 1: Foundation (Steps 1.1-1.3) - 1.5 hours
2. Phase 2: Backend Core (Steps 2.1-2.4) - 3 hours

**Day 2 (4-5 hours):**
3. Phase 3: MCP Agent (Steps 3.1-3.3) - 2 hours
4. Phase 4: Demo Code (Steps 4.1-4.2) - 30 minutes
5. Phase 5: Frontend (Steps 5.1-5.3) - 2 hours

**Day 3 (2-3 hours):**
6. Phase 6: Integration & Testing (Step 6.1-6.3) - 1.5 hours
7. Phase 7: Documentation & Demo (Steps 7.1-7.2) - 1 hour

---

## 🚨 Critical Path Items

These MUST be completed for demo to work:

1. **CEREBRAS_API_KEY** in .env (blocks AI workflow)
2. **Database schema** (blocks everything)
3. **ai_service.py** (sponsor integration)
4. **agent.py** (MCP agent server)
5. **docker-compose.yml** (orchestration)
6. **Frontend Board component** (UI demo)

---

## 🛠️ Development Tips

### Local Development (without Docker)

```bash
# Backend
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
export CEREBRAS_API_KEY=your_key_here
export DATABASE_URL=mysql+pymysql://jerai:jerai_pass@localhost:3306/jerai
python app.py

# Frontend
cd frontend
npm install
npm run dev

# MCP Agent
cd mcp_agent
source ../venv/bin/activate
pip install -r requirements.txt
export CEREBRAS_API_KEY=your_key_here
uvicorn agent:app --host 0.0.0.0 --port 9000
```

### Debugging Tips

```bash
# Check logs
docker compose logs -f backend
docker compose logs -f mcp_agent

# Enter container
docker exec -it jerai-backend bash
docker exec -it jerai-mcp-agent bash

# Check database
docker exec -it jerai-mysql mysql -u jerai -pjerai_pass jerai

# Restart service
docker compose restart backend

# Rebuild service
docker compose up --build backend
```

---

## 📊 Progress Tracking

Use this section to track your progress:

```
Phase 1: Foundation
  [_] Step 1.1: Environment Configuration
  [_] Step 1.2: Docker Compose
  [_] Step 1.3: Database Schema

Phase 2: Backend Core
  [_] Step 2.1: Database Models
  [_] Step 2.2: Issue Service
  [_] Step 2.3: AI Service
  [_] Step 2.4: Backend Routes

Phase 3: MCP Agent
  [_] Step 3.1: Agent Server
  [_] Step 3.2: Agent Tools
  [_] Step 3.3: Agent Docker

Phase 4: Demo Code
  [_] Step 4.1: Cart Code
  [_] Step 4.2: Test Case

Phase 5: Frontend
  [_] Step 5.1: API Client
  [_] Step 5.2: Components
  [_] Step 5.3: Frontend Docker

Phase 6: Integration
  [_] Step 6.1: Backend Dockerfile
  [_] Step 6.2: Requirements
  [_] Step 6.3: Full System Test

Phase 7: Documentation
  [_] Step 7.1: README
  [_] Step 7.2: Demo Video
```

---

## 🎉 Success Metrics

You're done when:
- ✅ `docker compose up` works without errors
- ✅ Demo bug exists in database
- ✅ Can activate bug via UI
- ✅ "AI Fix" button triggers Cerebras analysis
- ✅ MCP agent generates patch
- ✅ Bug auto-resolves and closes
- ✅ Event trail shows all steps
- ✅ Demo video recorded (< 2 minutes)

**Good luck! 🚀**