# UI Architecture Assessment

## Target Architecture

Human interaction begins with Conversation. UI is a localized, scope-aware presentation adapter; it must use canonical Mission and Kernel projections rather than own architectural state.

## Current Repository

Factory Chat uses authenticated views in `projects/factory_chat.py`, Factory workspace projections in `projects/factory_workspace.py`, and UI routes in `projects/ui_urls.py`. Runtime execution detail, controls, and SSE are served by `projects/runtime_api.py` and rendered as presentation projections.

## Gap Analysis

**Partial/strong:** Conversation-first human path exists, and presentation projections already exist. **Missing:** localization, scope-aware organization/workspace selection, neutral Kernel naming/contracts, and an intake projection not coupled to Factory session and ORKI Runtime.

## Migration Strategy

Keep current pages as Conversation and Kernel presentation adapters. Introduce neutral projection contracts behind existing URLs, then migrate templates/clients. UI localization follows the approved localization foundation; no business state should move into UI.

## Risks and Dependencies

User workflow disruption and client contract changes are the key risks. Depends on Mission Intake, Kernel projection, scope model, and localization policy.

## Readiness

**Ready.** It can progress as an adapter migration once its backend contracts are introduced; localization remains separately blocked.

## Evidence

`projects/factory_chat.py`; `projects/factory_workspace.py`; `projects/ui_urls.py`; `projects/runtime_api.py`; `bridge/urls.py`.
