# Incident Review: Payment Processing Cascade Failure

**Date:** 2024-01-15  
**Severity:** P1  
**Duration:** 14:23 - 16:47 UTC (2 hours 24 minutes)  
**Owning Team:** payments  
**Review Lead:** Sarah Chen

---

## Summary

A memory leak in the checkout service caused cascading failures across the payment processing pipeline, resulting in 100% of checkout attempts failing for 2+ hours. The issue was triggered by a deployment that introduced an unbounded cache for promotion codes. The incident was resolved by rolling back to the previous version and implementing an emergency memory limit increase.

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:23 | Memory usage on checkout-service pods begins climbing (unnoticed) |
| 14:41 | First OOMKill event on checkout-service-7d4f8b pod |
| 14:45 | Customer complaints begin appearing in support queue |
| 14:52 | On-call engineer paged via customer escalation (NOT via alert) |
| 15:01 | Incident declared as P1, war room opened |
| 15:18 | Root cause identified: promo code cache unbounded growth |
| 15:34 | Rollback initiated to checkout-service v2.14.3 |
| 15:52 | Rollback complete, new pods healthy |
| 16:15 | Error rate returns to baseline (<0.1%) |
| 16:47 | Incident closed, monitoring period begins |

---

## Impact

- **Users Affected:** ~47,000 users attempted checkout during outage
- **Revenue Impact:** $892,000 estimated lost transactions
- **SLA Breach:** Yes — breached 99.9% availability SLA by 1.8%
- **Services Degraded:** checkout-service, payment-gateway, order-processor
- **Error Rate Peak:** 100% (complete outage)
- **Latency Peak:** Timeout (30s) before failure
- **Failed Transactions:** 12,847 checkout attempts
- **Support Tickets:** 1,247 filed

---

## Root Cause

The incident was caused by PR #4521 which introduced a promotion code validation cache to reduce latency on repeat lookups. The cache implementation used an unbounded `Map<string, PromoCodeResult>` with no TTL or size limit.

During a flash sale event starting at 14:00, the unique promotion code usage spiked from ~500/hour to ~15,000/hour. Each unique code combination created a new cache entry. Within 20 minutes, the cache consumed 3.2GB of heap memory, triggering aggressive garbage collection and eventually OOMKill.

The Kubernetes deployment had `resources.limits.memory: 2Gi` which was insufficient for this failure mode.

**Contributing Factors:**
1. No cache size limit or eviction policy
2. No memory usage alerting on checkout-service
3. Load testing did not include high-cardinality promotion code scenarios
4. Deployment occurred 30 minutes before flash sale (timing coincidence)

---

## Detection Gap Analysis

How did we find out about this incident?

- [ ] Existing alert fired
- [x] Customer reported
- [ ] Internal user noticed
- [ ] Automated testing caught it

**Time to Detection:** 29 minutes (14:23 → 14:52)  
**Detection Gap:** We had no alerting on:
- Memory usage percentage on checkout-service pods
- Checkout success rate / error rate
- Payment processing latency at p99
- OOMKill events in the cluster
- Pod restart frequency

Our existing alerts were focused on infrastructure (CPU, disk) but not on service-specific golden signals.

---

## Alert Action Items

### New Alerts to Add

- [ ] **Add alert:** `container_memory_usage_bytes / container_spec_memory_limit_bytes` > 85% for 5m on service: checkout-service → severity: warning, team: payments
- [ ] **Add alert:** `container_memory_usage_bytes / container_spec_memory_limit_bytes` > 95% for 2m on service: checkout-service → severity: critical, team: payments
- [ ] **Add alert:** `sum(rate(http_requests_total{service="checkout-service", status_code=~"5.."}[5m])) / sum(rate(http_requests_total{service="checkout-service"}[5m]))` > 1% for 3m → severity: warning, team: payments
- [ ] **Add alert:** `sum(rate(http_requests_total{service="checkout-service", status_code=~"5.."}[5m])) / sum(rate(http_requests_total{service="checkout-service"}[5m]))` > 5% for 2m → severity: critical, team: payments
- [ ] **Add alert:** `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service="checkout-service", endpoint="/api/checkout"}[5m]))` > 2s for 5m → severity: warning, team: payments
- [ ] **Add alert:** `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service="checkout-service", endpoint="/api/checkout"}[5m]))` > 5s for 2m → severity: critical, team: payments
- [ ] **Add alert:** `increase(kube_pod_container_status_restarts_total{container="checkout-service"}[15m])` > 3 → severity: critical, team: payments
- [ ] **Add alert:** `kube_pod_container_status_last_terminated_reason{reason="OOMKilled", container="checkout-service"}` == 1 → severity: critical, team: payments
- [ ] **Add alert:** `sum(rate(payment_transactions_total{status="failed"}[5m])) / sum(rate(payment_transactions_total[5m]))` > 2% for 3m → severity: warning, team: payments
- [ ] **Add alert:** `checkout_promo_cache_size_bytes` > 500000000 for 5m → severity: warning, team: payments

### Existing Alerts to Update

- [ ] **Update alert:** `high_pod_cpu_usage` — add checkout-service to critical services list with lower threshold (70% instead of 85%)
- [ ] **Update alert:** `api_gateway_error_rate` — decrease threshold from 5% to 2% for payment endpoints
- [ ] **Update alert:** `kubernetes_deployment_replicas_mismatch` — reduce for duration from 10m to 5m

### Alerts to Remove/Deprecate

- [ ] **Remove alert:** `checkout_legacy_health_endpoint` — deprecated endpoint removed in v2.12.0

---

## Remediation Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Implement LRU cache with 10k entry limit and 5m TTL | @michael.wong | 2024-01-22 | In Progress |
| Increase checkout-service memory limit to 4Gi | @ops-team | 2024-01-16 | Done |
| Add cache metrics exporter (size, hit rate, evictions) | @michael.wong | 2024-01-22 | Pending |
| Create runbook for checkout-service memory issues | @sarah.chen | 2024-01-19 | Pending |
| Add high-cardinality promo codes to load test suite | @qa-team | 2024-01-26 | Pending |
| Implement deployment freeze 2hr before major sales | @release-team | 2024-01-31 | Pending |
| Post-mortem review with eng leadership | @sarah.chen | 2024-01-17 | Scheduled |

---

## Metrics Reference

For alert generation, here are the relevant metrics:

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `http_request_duration_seconds` | histogram | service, endpoint, method, status_code | Request latency buckets |
| `http_requests_total` | counter | service, endpoint, method, status_code | Total HTTP requests |
| `container_memory_usage_bytes` | gauge | pod, container, namespace | Container memory usage |
| `container_spec_memory_limit_bytes` | gauge | pod, container, namespace | Container memory limit |
| `kube_pod_container_status_restarts_total` | counter | pod, container, namespace | Container restart count |
| `kube_pod_container_status_last_terminated_reason` | gauge | pod, container, reason | Last termination reason |
| `payment_transactions_total` | counter | status, payment_method, region | Payment transaction count |
| `checkout_promo_cache_size_bytes` | gauge | instance | Promo code cache memory |
| `checkout_promo_cache_entries` | gauge | instance | Promo code cache entry count |

---

## Lessons Learned

1. **What went well:**
   - War room communication was excellent — clear updates every 10 minutes
   - Rollback process worked smoothly (18 minutes from decision to complete)
   - Customer support team handled volume professionally with prepared messaging

2. **What could be improved:**
   - Zero alerting on service-level metrics (error rate, latency, memory)
   - Code review missed unbounded cache pattern (need checklist item)
   - Deployment timing relative to business events not considered
   - No canary deployment — went straight to 100% traffic

3. **Where we got lucky:**
   - Incident happened on a Monday, not during weekend flash sale
   - Previous stable version was only 2 days old, rollback was safe
   - Database remained healthy despite connection surge during restarts

---

## Attendees

- Sarah Chen (Engineering Manager, Payments — Review Lead)
- Michael Wong (Senior Engineer, Payments — PR Author)
- David Park (SRE On-Call)
- Lisa Martinez (Customer Support Lead)
- James Thompson (VP Engineering — Executive Sponsor)
- Priya Sharma (QA Lead)
