# Incident Review: API Gateway Timeout Cascade Failure

## Incident Summary

**Date**: 2025-12-28
**Duration**: 3 hours 45 minutes
**Severity**: Critical
**Incident Commander**: Engineering Team Lead
**Services Affected**: API Gateway, Authentication Service, Order Processing, Payment Service
**Impact**:

- 25,000+ failed API requests
- Complete authentication service unavailability for 45 minutes
- $50,000+ in lost revenue from failed transactions
- 500+ customer support tickets

---

## What Happened

At 09:15 UTC on December 28th, 2025, our API Gateway experienced a cascading timeout failure that resulted in widespread service disruption across our platform. The incident began when a deployment to the authentication service introduced a database query regression that increased average response times from 50ms to 8-12 seconds.

The authentication service is called by nearly every API endpoint for token validation. As authentication response times degraded, API Gateway connections began to pile up, exhausting the connection pool. This triggered timeouts across all downstream services including order processing and payment services.

The incident escalated when our monitoring systems failed to alert quickly enough due to inadequate threshold configurations. By the time the on-call engineer was paged, the API Gateway had already exhausted its connection pool and was returning 503 errors to all incoming requests.

---

## Root Cause Analysis

### Primary Cause

A missing database index on the `auth_tokens.last_validated_at` column combined with a new token validation query introduced in deployment v2.14.5. The query performed a full table scan across 50M+ token records on every authentication request.

### Contributing Factors

1. **Insufficient Pre-Production Testing**: The staging environment only contained 10,000 token records, which didn't expose the query performance issue
2. **Missing Query Performance Alerts**: No alerts configured for slow database queries or authentication service latency
3. **Connection Pool Misconfiguration**: API Gateway connection pool size (100 connections) was too small for production load
4. **Inadequate Circuit Breaker**: No circuit breaker configured between API Gateway and authentication service
5. **Alert Threshold Tuning**: Existing alerts had thresholds set too high (response time > 5s for 10m) causing delayed notification

---

## Timeline

| Time (UTC) | Event                                                                              |
| ---------- | ---------------------------------------------------------------------------------- |
| **09:15**  | Authentication service v2.14.5 deployed to production                              |
| **09:20**  | Database CPU usage begins climbing (40% → 75%)                                     |
| **09:25**  | Authentication service response times increase to 3-5 seconds                      |
| **09:30**  | API Gateway connection pool utilization reaches 80%                                |
| **09:35**  | First customer complaints about slow login times                                   |
| **09:45**  | API Gateway connection pool exhausted, 503 errors begin                            |
| **09:50**  | Order processing service starts queueing requests due to auth timeouts             |
| **09:55**  | Payment service failures spike - transaction success rate drops to 15%             |
| **10:05**  | On-call engineer paged for high error rate (30 min delay from initial degradation) |
| **10:15**  | Engineer identifies slow query in database logs                                    |
| **10:25**  | Database team begins creating index on auth_tokens table                           |
| **10:45**  | Index creation completes, authentication latency drops to 100ms                    |
| **11:00**  | API Gateway connection pool recovers, error rate decreases                         |
| **11:30**  | All queued orders processed, payment processing normalized                         |
| **12:00**  | Incident declared resolved, post-mortem scheduled                                  |
| **13:00**  | Post-incident review meeting conducted                                             |

---

## Impact Metrics

### Technical Impact

- **API Error Rate**: Spiked to 87% (normal: <0.1%)
- **Authentication Service**: 100% timeout rate for 45 minutes
- **Database CPU**: Peaked at 98% utilization
- **Connection Pool**: 100% exhausted for 90 minutes
- **Queue Backlog**: 35,000+ pending order processing jobs

### Business Impact

- **Failed Transactions**: 12,500+ payment failures
- **Lost Revenue**: Estimated $50,000 in abandoned carts
- **Customer Support**: 500+ tickets created
- **User Experience**: 25,000+ users affected
- **SLA Breach**: 99.9% uptime SLA violated for December

---

## Alerts to Create

### Alert 1: Slow Authentication Service Response Time

- **Alert Name**: auth-service-high-latency
- **Type**: threshold
- **Severity**: critical
- **Metric**: service.auth.response_time_ms
- **Condition**: >
- **Threshold**: 1000
- **Duration**: 3m
- **Description**: Authentication service response time exceeds 1 second for 3 consecutive minutes
- **Actions**:
  - PagerDuty: platform-team
  - Slack: #incidents
  - Email: engineering-oncall@company.com

### Alert 2: Database Query Performance Degradation

- **Alert Name**: database-slow-query-critical
- **Type**: threshold
- **Severity**: critical
- **Metric**: database.query.p95_duration_ms
- **Condition**: >
- **Threshold**: 500
- **Duration**: 5m
- **Description**: Database P95 query duration exceeds 500ms indicating performance issues
- **Actions**:
  - PagerDuty: database-team
  - Slack: #database-alerts
  - Email: dba-team@company.com

### Alert 3: API Gateway Connection Pool High Utilization

- **Alert Name**: api-gateway-connection-pool-high
- **Type**: threshold
- **Severity**: warning
- **Metric**: gateway.connection_pool.utilization_percent
- **Condition**: >
- **Threshold**: 75
- **Duration**: 5m
- **Description**: API Gateway connection pool utilization above 75%, may lead to connection exhaustion
- **Actions**:
  - Slack: #platform-alerts
  - Email: platform-team@company.com

### Alert 4: API Gateway Connection Pool Exhausted

- **Alert Name**: api-gateway-connection-pool-exhausted
- **Type**: threshold
- **Severity**: critical
- **Metric**: gateway.connection_pool.utilization_percent
- **Condition**: >=
- **Threshold**: 95
- **Duration**: 2m
- **Description**: API Gateway connection pool nearly exhausted, immediate action required
- **Actions**:
  - PagerDuty: platform-team
  - Slack: #incidents
  - Email: engineering-oncall@company.com

### Alert 5: High API Error Rate

- **Alert Name**: api-error-rate-critical
- **Type**: threshold
- **Severity**: critical
- **Metric**: api.error_rate_percent
- **Condition**: >
- **Threshold**: 5
- **Duration**: 3m
- **Description**: API error rate exceeds 5% indicating widespread service degradation
- **Actions**:
  - PagerDuty: platform-team
  - Slack: #incidents
  - Email: engineering-oncall@company.com

### Alert 6: Payment Processing Failure Rate

- **Alert Name**: payment-processing-failure-high
- **Type**: threshold
- **Severity**: critical
- **Metric**: service.payment.failure_rate_percent
- **Condition**: >
- **Threshold**: 10
- **Duration**: 5m
- **Description**: Payment processing failure rate above 10%, impacting revenue
- **Actions**:
  - PagerDuty: payments-team
  - Slack: #payments-critical
  - Email: payments-oncall@company.com

### Alert 7: Order Processing Queue Backlog Critical

- **Alert Name**: order-queue-backlog-critical
- **Type**: threshold
- **Severity**: warning
- **Metric**: queue.orders.pending_count
- **Condition**: >
- **Threshold**: 5000
- **Duration**: 10m
- **Description**: Order processing queue has critical backlog exceeding 5000 pending orders
- **Actions**:
  - Slack: #orders-team
  - Email: orders-team@company.com
  - Ticket: create-ops-ticket

### Alert 8: Database CPU High Utilization

- **Alert Name**: database-cpu-critical
- **Type**: threshold
- **Severity**: critical
- **Metric**: database.cpu.utilization_percent
- **Condition**: >
- **Threshold**: 85
- **Duration**: 5m
- **Description**: Database CPU utilization critically high, may impact all services
- **Actions**:
  - PagerDuty: database-team
  - Slack: #database-critical
  - Email: dba-team@company.com

---

## Action Items

### Immediate (Week 1)

1. ✅ Rollback authentication service to v2.14.4
2. ✅ Create index on `auth_tokens.last_validated_at` column
3. ✅ Implement all 8 alerts listed above
4. [ ] Increase API Gateway connection pool size from 100 to 500
5. [ ] Add circuit breaker between API Gateway and authentication service
6. [ ] Review and optimize all authentication service database queries

### Short-term (Week 2-4)

7. [ ] Implement query performance profiling in staging environment
8. [ ] Add automated index recommendation system for production database
9. [ ] Create runbook for connection pool exhaustion scenarios
10. [ ] Implement connection pool monitoring dashboard
11. [ ] Add database query performance tests to CI/CD pipeline
12. [ ] Configure circuit breaker patterns for all critical service dependencies

### Long-term (Month 2-3)

13. [ ] Migrate authentication service to read replicas for validation queries
14. [ ] Implement distributed tracing for end-to-end request monitoring
15. [ ] Build automated load testing with production-scale data
16. [ ] Conduct chaos engineering exercises for similar failure scenarios
17. [ ] Review and update all SLA commitments based on current architecture
18. [ ] Implement auto-scaling for API Gateway based on connection pool metrics

---

## Lessons Learned

### What Went Well

- ✅ Team responded quickly once paged
- ✅ Database team efficiently created index under pressure
- ✅ Clear communication in incident channel
- ✅ Rollback procedure was well-documented and executed smoothly
- ✅ No data loss or corruption occurred

### What Went Poorly

- ❌ Staging environment didn't catch the performance regression
- ❌ 30-minute delay before on-call engineer was paged
- ❌ No circuit breaker prevented cascade failure
- ❌ Missing alerts for critical performance metrics
- ❌ Connection pool size inadequate for production load
- ❌ No automated query performance analysis in deployment pipeline

---

## Sign-off

**Reviewed By**:

- Engineering Lead: [Name] - 2025-12-29
- Database Team Lead: [Name] - 2025-12-29
- Platform Team Lead: [Name] - 2025-12-29
- CTO: [Name] - 2025-12-29

**Status**: Approved for Implementation
**Next Review**: 2026-01-29 (30-day follow-up)
