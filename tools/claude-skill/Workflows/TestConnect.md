---
workflow: test-connect
purpose: Test API connectivity and check job status
---

# Test & Connect

**Purpose:** Verify API connectivity and check async job status.

## Test Connectivity

```bash
python tools/nca.py test
```

Returns a success message if the API is reachable and authenticated.

## Check Job Status

```bash
python tools/nca.py status <JOB_ID>
```

Returns the current status of an async job (queued, running, done, failed).

## Troubleshooting

If the test fails, verify:
1. `NCA_API_URL` is set to the correct URL (no trailing slash)
2. `NCA_API_KEY` matches the API_KEY configured on the server
3. The server is running and accessible from your network
