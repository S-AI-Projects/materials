# Test execution results

## Baseline
Existing integration test: 1 failed.
Reason: HTTP 403 from localhost:5000; no working local application server.
This does not establish a rendering defect.

## Focused regression tests
Command: python3 work/R32-T031/check.py
Result: 3 passed, 16 protobuf deprecation warnings.
- Empty recommendations: passed.
- Three ordinary recommendations: passed.
- Repeated titles: passed.

The focused tests mock the gRPC client and make no network requests.
