# Issue #17 corrective sprint — closure report

Date: 2026-08-01

## AI Bridge publication

- Branch: `agent/issue-17-conversational-po`
- Implementation commit: `555b71cba673475d9c14db235894ec75a0abd2c3`
- Push: `origin/agent/issue-17-conversational-po` accepted
- Draft PR: https://github.com/zsambokia/ai-bridge/pull/18

## Gate disposition

| Gate | Result | Evidence |
| --- | --- | --- |
| Backend corrective release | PASS | Django test suite: 32 passing |
| Frontend corrective release | PASS | Ruff and Mypy repository checks pass |
| Conversational UX | PASS | Chromium discovery, plan, approval, URL tests |
| Plain-language projection | PASS | Template search plus Chromium assertion |
| New project flow | PASS | Chromium desktop and mobile tests |
| Mobile browser | PASS | Playwright 390×844 journey |
| Desktop browser | PASS | Playwright 1440×960 journey |
| Demo17 end-to-end | BLOCKED | Exact remote returns `Repository not found` |
| Operational acceptance | BLOCKED | Cannot bootstrap, deliver, or run the inaccessible target |
| Independent corrective audit | BLOCKED | Its required end-to-end delivery evidence cannot exist without the target |

## Required external input

Provide access to, or create, `https://github.com/zsambokia/demo17-repo` with
authority to clone and push.  Then rerun the real Factory Chat mission against
that exact repository, collect its commit SHA and runtime/preview URL, and
complete the remaining three gates.

## Closure state

`CORRECTIVE SPRINT: BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`
