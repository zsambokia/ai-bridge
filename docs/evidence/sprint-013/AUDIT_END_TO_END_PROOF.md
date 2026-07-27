# Audit end-to-end proof

Remote MCP endpoint: `https://stage.artificial-software-factory.com/mcp/`.

1. `work_item.propose` created scope
   `bridge:ai-bridge:work-item:fd72da37-0041-484f-8a08-b22e015bc05f` as
   `WORK_ITEM` / `AUDIT`.
2. `scope.review` returned `next_tool: conversation.confirm` and proposal hash
   `263fd3c27392bcbb815014f5431294c845836d5f76c087830735bd26fbea9115`.
3. The Product Owner phrase `Igen, jó lesz.` invoked `conversation.confirm`.
4. The flow created one durable approval, one orchestration, publication,
   preparation, contract generation, validation, issuance, consumption, and a
   real `codex-cli` provider run.

The proof did not use `scope.approve` as a conversational entry point and did
not use bootstrap authority.
