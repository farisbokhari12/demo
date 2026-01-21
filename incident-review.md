# Incident Review: Production Service Degradation

## Incident Summary

**Date**: 2025-12-15  
**Duration**: 2 hours 30 minutes  
**Severity**: High  
**Services Affected**: API Gateway, User Service, Order Service

### Impact
- Elevated error rates across API endpoints
- Degraded response times for end users
- ~500 failed customer transactions

---

## What Happened

A production deployment introduced performance regressions that weren't caught during staging. The issues cascaded across dependent services before the on-call team was alerted.

---

## Root Cause

Database query regression in the User Service caused response times to spike from 50ms to 3+ seconds. This exhausted connection pools upstream and triggered timeouts across the API Gateway.

### Contributing Factors
- No alerting on User Service response time
- Connection pool metrics weren't monitored
- Error rate threshold was set too high (10%) to catch early degradation

---

## Timeline

| Time | Event |
|------|-------|
| 14:00 | Deployment to User Service |
| 14:15 | Response times start climbing |
| 14:30 | Connection pools at 80% |
| 14:45 | First 503 errors appear |
| 15:00 | On-call paged (45 min delay) |
| 15:30 | Root cause identified |
| 16:00 | Rollback complete |
| 16:30 | All services recovered |

---

## Alerts to Create

Based on this incident, we need to add the following alerts:

1. **Error rate alert** - We should alert when error rate goes above 5% for more than 3 minutes. This should page on-call immediately.

2. **Response time alert** - Need to catch when p95 latency exceeds 2 seconds. This was a key early indicator we missed.

3. **Connection pool utilization** - Alert when connection pools hit 75% so we have time to react before exhaustion.

4. **Database query duration** - If p95 query time exceeds 500ms for 5 minutes, something is wrong with the database layer.

5. **Upstream dependency health** - We need visibility when downstream services start failing. Alert on dependency error rate > 10%.

6. **CPU/Memory alerts** - Basic resource alerts at 80% CPU and 90% memory would help catch resource exhaustion earlier.

---

## Action Items

- [ ] Implement the alerts listed above
- [ ] Add query performance tests to CI
- [ ] Review connection pool sizing
- [ ] Update runbooks with new alerts

---

## Lessons Learned

**What went well**: Team responded quickly once paged, rollback was smooth

**What went poorly**: 45-minute detection delay, missing alerts for early warning signs
