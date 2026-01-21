# RetroshiftAI Alerts Demo

A demo repository for testing the RetroshiftAI **Alert PR Generator** workflow. This workflow automatically reads incident review documents, extracts alert requirements, and generates Prometheus alert YAML files with a GitHub PR.

## Repository Structure

```
retroshift-alerts-demo/
├── README.md
├── alerts/
│   ├── api/
│   │   ├── high_error_rate.yaml
│   │   └── high_latency.yaml
│   ├── infrastructure/
│   │   ├── cpu_usage.yaml
│   │   ├── disk_usage.yaml
│   │   └── memory_usage.yaml
│   └── database/
│       └── connection_pool.yaml
├── incident-reviews/
│   └── 2024-01-15-checkout-outage.md
└── generated-alerts/
    └── .gitkeep
```

## How It Works

1. **Incident Review** → Engineers document incidents in `incident-reviews/` with structured alert action items
2. **Alert Generation** → RetroshiftAI reads the incident review and extracts alert requirements
3. **Pattern Matching** → The LLM learns from existing alerts in `alerts/` to match your conventions
4. **PR Creation** → New alert YAML files are generated in `generated-alerts/` and a PR is opened

## Alert File Convention

All Prometheus alert YAML files follow this structure:

```yaml
groups:
  - name: <alert-group-name>
    rules:
      - alert: <AlertNameInPascalCase>
        expr: |
          <promql_expression>
        for: <duration>
        labels:
          severity: warning | critical
          team: <team-name>
          component: <component-name>
        annotations:
          summary: "<short description with {{ $labels.xxx }} templating>"
          description: "<detailed description with {{ $value | humanizePercentage }} etc>"
          runbook_url: "https://runbooks.internal/<path>"
          dashboard_url: "https://grafana.internal/d/<dashboard-id>"
```

### Naming Conventions

- **Alert names**: PascalCase (e.g., `HighErrorRate`, `CriticalMemoryUsage`)
- **Group names**: lowercase-with-dashes (e.g., `api-alerts`, `memory-alerts`)
- **File names**: snake_case.yaml (e.g., `high_error_rate.yaml`)

### Label Taxonomy

| Label | Values | Description |
|-------|--------|-------------|
| `severity` | `warning`, `critical` | Alert urgency level |
| `team` | `platform`, `sre`, `payments`, etc. | Owning team |
| `component` | `api`, `infrastructure`, `database` | System component |

### Required Annotations

| Annotation | Description |
|------------|-------------|
| `summary` | One-line description with label templating |
| `description` | Detailed description with value formatting |
| `runbook_url` | Link to operational runbook |
| `dashboard_url` | Link to relevant Grafana dashboard (optional) |

## Incident Review Format

Incident reviews should include an **Alert Action Items** section with structured requirements:

```markdown
## Alert Action Items

### New Alerts to Add

- [ ] **Add alert:** `<promql_expression>` > <threshold> for <duration> → severity: <level>, team: <team>
```

See `incident-reviews/2024-01-15-checkout-outage.md` for a complete example.

## Local Development

### Validate Alert Syntax

```bash
# Using promtool (from Prometheus)
promtool check rules alerts/**/*.yaml
```

### Test Alert Expressions

```bash
# Query against local Prometheus
curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=sum(rate(http_requests_total[5m])) by (service)'
```

## Contributing

1. Create incident review in `incident-reviews/`
2. Run Alert PR Generator workflow
3. Review generated alerts in PR
4. Merge after approval

## License

MIT
