# Alert PR Generator Demo

This repository demonstrates the **Alert PR Generator** workflow - an automated system that parses incident review documents and generates alerting configurations as pull requests.

## 🎯 What This Demo Shows

The Alert PR Generator workflow:

1. **Parses** an incident review markdown file
2. **Extracts** alerting recommendations from the "Alerts to Create" section
3. **Generates** YAML alert definition files
4. **Creates** a pull request with the new alerts

## 📁 Repository Structure

```
demo/
├── README.md                    # This file
├── example-incident-review.md   # Sample incident review document
├── workflows/
│   └── alert-pr-generator.json  # Workflow definition
└── alerts/                      # Generated alert files (created by workflow)
```

## 🔄 Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Incident       │────▶│  Parse Review    │────▶│  Generate Alerts   │
│  Review File    │     │  Document        │     │  Definitions       │
└─────────────────┘     └──────────────────┘     └────────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  PR Created!    │◀────│  Create Pull     │◀────│  Write Alert       │
│  Ready to merge │     │  Request         │     │  YAML Files        │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

## 📋 Example Input

The `example-incident-review.md` contains a realistic incident review with:
- Incident summary and timeline
- Root cause analysis
- **8 alerts to create** (extracted by the workflow)
- Action items and lessons learned

## 🚀 Running the Demo

1. Trigger the Alert PR Generator workflow
2. Input: `example-incident-review.md`
3. Output: A pull request with 8 new alert definition files in the `alerts/` directory

## 📊 Generated Alerts

The workflow will generate alerts for:

| Alert | Severity | Service |
|-------|----------|---------|
| Auth Service High Latency | Critical | Authentication |
| Database Slow Query | Critical | Database |
| API Gateway Connection Pool High | Warning | API Gateway |
| API Gateway Connection Pool Exhausted | Critical | API Gateway |
| High API Error Rate | Critical | API |
| Payment Processing Failure | Critical | Payments |
| Order Queue Backlog | Warning | Orders |
| Database CPU High | Critical | Database |

## 📝 License

MIT
