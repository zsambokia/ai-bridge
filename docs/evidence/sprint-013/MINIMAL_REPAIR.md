# Minimal repair

The repair adds `AUDIT` to canonical work-type validation and carries approved
audit metadata in the existing proposal and contract payloads. It adds exactly
one selected provider identity and eligible-identity list to the existing
contract provider policy. Consumption rejects an unselected identity and run
dispatch uses the durable receipt identity. Focused regression tests cover the
Audit scope, provider binding, unavailable-provider rejection, and read-only
Audit completion boundary.
