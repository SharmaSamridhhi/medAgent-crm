# EPIC-03: LangGraph AI Agent & Tools

**Status:** To Do

## Goal

Build the LangGraph agent that powers the conversational side of the Log
Interaction Screen: a Groq-backed graph with a set of typed tools for
logging, editing, and enriching HCP interaction data, exposed behind a
chat API endpoint.

## Specs in this epic

| Spec | Title | Status |
|------|-------|--------|
| [MEDGENT-009](../MEDGENT-009-groq-langgraph-scaffold.md) | Groq LLM integration & agent scaffolding | To Do |
| [MEDGENT-010](../MEDGENT-010-tool-log-interaction.md) | Tool: Log Interaction | To Do |
| [MEDGENT-011](../MEDGENT-011-tool-edit-interaction.md) | Tool: Edit Interaction | To Do |
| [MEDGENT-012](../MEDGENT-012-tool-retrieve-hcp-history.md) | Tool: Retrieve HCP History | To Do |
| [MEDGENT-013](../MEDGENT-013-tool-schedule-follow-up.md) | Tool: Schedule Follow-up | To Do |
| [MEDGENT-014](../MEDGENT-014-tool-compliance-flag.md) | Tool: Compliance Flag | To Do |
| [MEDGENT-015](../MEDGENT-015-agent-orchestration-endpoint.md) | Agent orchestration & conversational endpoint | To Do |

## Notes

Depends on EPIC-02 (needs the HCP/Interaction data models to read and write
against). This epic delivers the five-plus required agent tools, including
the two mandatory ones (Log Interaction, Edit Interaction).
