# Single-confirmation orchestration proof

The Product Owner reviews a durable `scope.review` proposal, then confirms the
displayed version and exact proposal hash once through `conversation.confirm`.
The coordinator records that confirmation and advances the existing governed
operations in order: approval, publication, preparation, contract generation,
validation, issuance, consumption, provider start, and eventual completion.
Each remains a separately audited lifecycle transition.

The independent normal-path Storybook run proves the sequence with one normal
confirmation reference, `PO-STORYBOOK-S011-20260726`, for proposal version `1`
and hash `7f758752849d5ecbc8f1bedabf5473238f7aa8c5e9209ab44f53d3adeb55074a`.
Its durable orchestration token is
`df8a1150-2dac-44d2-b746-02fb00ff5882`; its issued-and-consumed contract is
`bridge:ai-bridge:contract:6ba8151f-b3ac-4635-a5d2-4bd86c899429`; and its real
provider run is `f92b4953-eba5-49e3-bacf-4b81abf78e57` (`codex-cli`).

No bootstrap authority was used for that Work Item.
