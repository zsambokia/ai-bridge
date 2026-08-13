# Negative invariants

These are architectural exclusions recovered from the conversation, not merely
implementation preferences.

| Invariant | Evidence |
|---|---|
| Conversation does not decide Mission semantics. | `CHAT-0031`–`0032` |
| CU does not write Conversation State directly and does not decide domain consequences. | `CHAT-0085`–`0086`, `0147`–`0150` |
| Profile resolver does not ask the user, skip to a different profile, or repair state directly on resolution failure. | `CHAT-0123`–`0128` |
| CSM is not a universal “Master Orchestrator.” | `CHAT-0139`–`0142` |
| A processing invocation is not automatically a durable Artifact. | `CHAT-0107`–`0108` |
| Evidence is not optional logging; provenance relations are not erased. | `CHAT-0161`–`0164`, `0209`–`0216` |
| Artifact identity/version is not a mutable document overwrite. | `CHAT-0245`–`0246`, `0412`–`0417` |
| An entire Artifact is not copied into AKB merely because it exists. | `CHAT-0263`–`0266` |
| Claim is not a generic bucket for every ambiguity. | `CHAT-0275`–`0290` |
| L4 is not Resolution-only and Factory Message is not merely payload transport. | `CHAT-0285`–`0304` |
| FFS is not a data-plane proxy or an MVP HA requirement. | `CHAT-0317`–`0328` |
| Communication authorization is not a separate inbound/outbound/forbidden contract once Zoning is canonical. | `CHAT-0355`–`0358` |
| Factory Chat is not Runtime or Conversation owner. | `CHAT-0347`–`0350` |
| AI Kernel is not Cognitive Processing; unreviewed domains are not imported into LAN topology. | `CHAT-0351`–`0354`, `0365`–`0366` |
| Current Constitution is not automatically the target architecture. | `CHAT-0369`–`0370` |
| Existing reconstruction IDs/documents are not primary decision evidence. | `CHAT-0418`–`0423` |
