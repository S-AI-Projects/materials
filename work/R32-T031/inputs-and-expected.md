# Test cases: render_homepage

## Contract
- Input: no route parameters.
- gRPC request: user_id=1, category=MYSTERY, max_results=3.
- Output: HTTP 200 HTML containing one list item per returned book title.
- External dependency: recommendations_client.Recommend (mocked in tests).
- Mutation: no local application data is modified.

## Cases and expected results

1. Empty recommendations
   Input: []
   Expected: HTTP 200; homepage title and heading present; no list items.

2. Ordinary recommendations
   Input: The Silent Patient, Gone Girl, The Guest List
   Expected: HTTP 200; all three titles appear in separate list items.

3. Repeated title boundary
   Input: Duplicate, Duplicate
   Expected: HTTP 200; two separate list items containing Duplicate.

All expected results are defined from the template and function contract,
not copied from test execution.
