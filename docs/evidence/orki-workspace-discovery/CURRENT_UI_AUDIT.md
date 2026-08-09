# Current UI Audit

**Method:** route/template/source inspection at baseline
`bf6f886bb5a08187eafb9cccd02b662ff9856f66`.

| Surface | Purpose and state | Backend/services | Decision |
| --- | --- | --- | --- |
| `GET /` | Authenticated Factory Chat; modes `planning`, `coding`, `memory`; panels `context`, `chat`, `projects` | `factory_chat._context`, Cognitive State, plans, runtime projection | Keep; make it the Orki landing area. |
| `POST /factory/message/` | Natural-language goal intake | Factory session, runtime ingress/dispatch, provider adapter | Keep as canonical Orki interaction. |
| `GET /factory/status/` | Server-rendered context fragment | Cognitive workspace, mission, plan, memory, runtime | Merge as reusable cards; do not retain as a navigation root. |
| `GET/POST /factory/new-project/` | Durable Project Registry/bootstrap entry | Project model and Factory session | Keep; evolve to Projects/Repository flow. |
| `POST /factory/plan/*` | Create/approve/change/reject plan | factory planning and governance | Merge into Execution/Workflows; governed action remains. |
| `POST /factory/memory/*` | Search/review memory | `factory_memory`, `knowledge.review_candidate` | Merge into Knowledge; retain governance. |
| `/reasoning/decision*`, `/reasoning/schema` | Structured reasoning API | decision API | Keep API; future Decisions screen is missing. |
| `/runtime/executions/*` + SSE | detail, dispatch, pause/resume/recover and events | `runtime_api`, `orki_runtime` | Keep API; future Execution/Runtime screens are missing. |
| `/factory/proofs/github-provider/` | proof endpoint | GitHub provider E2E API | Operational evidence, not Workspace navigation. |
| `/admin/` | model administration | Django admin | Keep as Administration, outside everyday Workspace. |
| `/accounts/*` | authentication | Django auth | Keep utility surface. |
| `/health/`, `/mcp/` | health and MCP ingress | core/projects endpoints | Operational interfaces, not UI navigation. |

## Inventory conclusion

There are no dedicated current pages for Repository, Roadmap, Architecture,
Decisions, Meetings, Workflows, Runtime or Evidence. Their eventual Workspace
areas are an information-architecture proposal, not a claim of implemented UI.
The single `factory_context_status.html` is a fragment embedded in
`factory_chat.html`; it is not a separate screen.

**Evidence:** `bridge/urls.py`, `projects/ui_urls.py`,
`projects/factory_chat.py`, and the three templates under
`projects/templates/projects/`.
