# Chat Behaviour Audit

**Status: PARTIAL — conversational form exists; operational reasoning is not an independent behaviour layer.**

The prompt defines a Hungarian digital COO persona, clarification behavior, structured understanding, alternatives and Product Owner decisions (`factory_orki.py:113-242`). Context includes project identity, one latest roadmap item, five approved-memory titles, recent messages and cognitive projections (`:63-111`). Durable messages and session ownership exist.

However, no evidence shows a separate versioned Behaviour/Decision layer that deterministically selects COO/architect/planner/advisor behavior from mission, roadmap, AKB, repository and history. The response protocol is a long provider prompt and JSON decoder. Repository semantic retrieval, repository receipts, configuration, and previous-mission retrieval are not mandatory inputs to `_bounded_context`. Consequently Orki can converse, but its promised project-aware operational behaviour is not proven independent of prompt wording or comprehensive evidence resolution.

