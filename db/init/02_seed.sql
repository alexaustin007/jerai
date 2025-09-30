-- Jerai Demo Data
-- Seeds demo bug (cart rounding issue)

USE jerai;

-- Insert demo bug: Cart calculation rounding error
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
    'actual', '$21.52 or $21.54',
    'test_case', 'Items: $19.99 + $1.99 with 10% discount and 8.875% tax'
  )
);