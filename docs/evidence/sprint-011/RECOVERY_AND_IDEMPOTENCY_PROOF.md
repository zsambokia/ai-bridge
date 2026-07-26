# Recovery and idempotency proof

After the Storybook contract had been consumed, the coordinator held a stale
in-memory contract reference and stopped before provider start. The repair
refreshes the consumed contract before starting the run. Resuming used the same
issued contract and produced no duplicate approval, contract issuance, or
provider execution. Technical repair followed DETECT → DIAGNOSE → REPAIR →
RERUN without a Product Owner escalation.
