-- Jerai Demo Data
-- Seeds demo bug (cart rounding issue)

USE jerai;

-- Insert demo bug: Clothing cart calculation rounding error
INSERT INTO issues (title, type, state, created_by)
VALUES ('ClothingCo cart shows $42.10, should be $42.11 after discount + tax', 'BUG', 'New', 'demo');

-- Log creation event
INSERT INTO events (issue_id, type, actor, payload_json)
VALUES (
  1,
  'IssueCreated',
  'demo',
  JSON_OBJECT(
    'description', 'Float rounding error in ecommerce/cart.py compute_total() function',
    'expected', '$42.11 (4211 cents)',
    'actual', '$42.10 or $42.12 due to float precision',
    'test_case', 'Items: Classic Cotton Shirt ($29.99) + Wool Socks ($12.99) with 10% discount and 8.875% tax',
    'affected_files', 'backend/ecommerce/cart.py',
    'category', 'clothing-ecommerce'
  )
);