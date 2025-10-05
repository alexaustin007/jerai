# Jerai - AI that solves your backlog, not just bugs

Jerai is an issue tracker and solver that automatically fixes bugs for you. Think of it like Jira, but with an AI assistant that can actually read your code, understand what's wrong, and write the fix.

## What does it do?

You report a bug, click "AI Fix", and the system:
1. Analyzes what's wrong in your code
2. Generates a patch to fix it
3. Tests the fix to make sure it works
4. Shows you exactly what changed

All of this happens automatically in about 10-15 seconds.

## Why did we build this?

As developers, we spend hours debugging simple issues like calculation errors, type mismatches, or logic bugs. We wanted to see if AI could handle the boring stuff so we can focus on building features.

## How it works

We combined three Cerebras, Meta's Llama and Docker MCP to make this possible:

**1. Cerebras API** 
- Analyzes your bug in under 1 second
- Uses the Llama 3.3 70B model for understanding code
- Tells us what's likely broken and where to look

**2. Meta's Llama 3.3 70B**
- Reads your actual code files
- Understands context and patterns
- Generates the fix based on best practices

**3. Docker MCP Gateway** 
- Runs the AI in an isolated container
- Gives it read-only access to your code
- Prevents any accidental damage

## Demo: The Shopping Cart Bug

We included a real-world example: a clothing e-commerce website with a cart calculation bug.

**For eg take a real world problem which has occurred:**
When you buy a shirt for $29.99 and socks for $12.99, apply a 10% discount, and add 8.875% tax, the total should be $42.11, But because the code uses regular floating-point math, you might get $42.10 or $42.12 instead.

**The Fix:**
The AI detects this is a precision issue and rewrites the calculation to use Python's `Decimal` type, which handles money correctly.

You can see this bug in action by:
1. Opening the shopping app at https://jerai-creb.vercel.app/
2. Adding items to your cart
3. Clicking "Calculate Total"
4. Seeing the warning that shows the wrong amount

Then you can:
1. Go to the main tracker at https://jerai.vercel.app/
2. Find the cart bug issue
3. Click "AI Fix"
4. Watch it automatically fix the code

## Getting Started

You need:
- Docker installed on your computer
- A Cerebras API key (free from https://cerebras.ai)

Then run:

```bash
# 1. Clone the project
git clone https://github.com/yourusername/jerai.git
cd jerai
# 2. Start everything
docker compose up --build


## What's inside?

**Frontend** - A simple board view where you can:
- See all your bugs in columns (New, Active, Resolved, Closed)
- Click "AI Fix" on any active bug
- View the complete history of what the AI did

**Backend** - A Python Flask server that:
- Manages your issues and their states
- Calls Cerebras for fast analysis
- Routes requests to the Docker MCP Gateway
- Stores everything in a MySQL database

**Shopping Demo** - A React app that:
- Shows a clothing store with real products
- Has a working shopping cart
- Contains the intentional bug for demonstration

**MCP Agent** - A containerized AI that:
- Reads your code files safely
- Generates fixes using Llama
- Runs tests to validate the fix
- Never has write access to your actual code

## The workflow explained

**When you click "AI Fix":**

1. **Cerebras analyzes the bug** (~1-2 second)
   - Reads your bug description
   - Figures out what type of problem it is
   - Suggests which files to check

2. **Docker MCP Gateway activates** (~2-5 seconds)
   - Spins up a safe container
   - Gives the AI read-only access to your code
   - Sends the analysis to Llama

3. **Llama generates a patch** (~5-10 seconds)
   - Reads the relevant source files
   - Understands the bug pattern
   - Writes corrected code
   - Creates a proper code diff

4. **Tests run automatically** (~2 seconds)
   - Validates the fix against your test suite
   - Makes sure nothing else broke
   - Reports success or failure

5. **Issue auto-resolves** (instant)
   - If tests pass, moves to "Resolved"
   - Shows you the complete patch
   - Logs everything in the event history

## Why these three technologies?

**Cerebras** gives us incredible speed. Most AI APIs take 3-5 seconds just to think. Cerebras does it in under 1 second, which makes the whole experience feel instant.

**Llama 3.3 70B** is open-source and really good at understanding code. It can spot patterns, understand context across multiple files, and generate fixes that actually make sense.

**Docker MCP Gateway** solves the safety problem. We can't just let an AI modify files directly. The gateway gives us a secure way to let the AI read code and propose changes without any risk.

Together, they create a fast, smart, and safe bug-fixing system.

## Project structure

```
jerai/
├── frontend/           # React app - the bug tracker UI
├── ecommerce-app/      # React app - the shopping demo
├── backend/            # Flask API - handles everything
│   ├── ecommerce/      # Shopping cart code (with the bug)
│   ├── services/       # AI integration code
│   └── tests/          # Tests that expose the bug
├── mcp_agent/          # The containerized AI agent
└── db/                 # Database setup and demo data
```


## How Jerai Works as Your AI-Powered Issue Tracker and Solver

Jerai isn't just a bug fixer - it's a complete issue tracking system like Jira, but with an AI layer that can actually help resolve issues instead of just organizing them.

### Issue Types We Support

Just like Jira, Jerai handles different types of work:

**Bugs** - Things that are broken and need fixing
- Production errors that customers report
- Failed test cases in your CI/CD pipeline
- Performance issues or memory leaks
- Security vulnerabilities found in scans

**Tasks** - Work that needs to be done
- Refactoring messy code
- Adding input validation to existing functions
- Updating deprecated API calls
- Converting code to use new libraries

**Stories** - New features to implement
- Adding new API endpoints
- Implementing business logic
- Creating utility functions
- Building data transformations

### Use Cases

Here's where Jerai's AI layer actually saves you time:

#### 1. The "Junior Developer Bug" Scenario
**Problem**: Your QA team finds a null pointer exception in the checkout flow. Usually, a junior developer would spend 2 hours tracing through logs, finding the file, and writing the fix.

**With Jerai**:
- Create the bug with stack trace
- Click "AI Fix"
- AI finds the file, sees the missing null check, adds proper validation
- 15 seconds instead of 2 hours

### What Makes This Different from Regular Jira

**Traditional Jira**:
1. Developer reads bug description
2. Developer searches codebase manually
3. Developer figures out the fix
4. Developer writes code
5. Developer tests it
6. Developer creates PR
7. Code review happens
8. Merge and deploy

**Jerai with AI**:
1. Developer reads bug description (or AI reads it for them)
2. AI searches codebase automatically
3. AI figures out the fix
4. AI writes the code
5. AI tests it automatically
6. Developer reviews the AI's patch (30 seconds instead of 30 minutes)
7. Copy patch to PR and commit
8. Merge and deploy

### The Bottom Line

Jerai won't replace your developers but will boost productivity. What it does is handle the mechanical parts of debugging - the searching, pattern matching, and code generation, so your team can focus on the parts that need human creativity, judgment, and problem-solving.

## License

MIT License - Feel free to use and modify

---

