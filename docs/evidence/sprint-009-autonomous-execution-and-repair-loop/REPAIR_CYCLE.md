# Controlled repair cycle

During the first required gate run, `ruff check .` rejected 20 long lines in
the manually introduced Django migration and one long dispatcher docstring.
This was classified as a routine build/lint/type defect, not escalated to the
Product Owner. `ruff format` repaired the migration mechanically and the
dispatcher text was made compliant; the exact same lint gate was rerun and
passed. The final suite also exercises `repair_failure`: routine lint failures
enter `REPAIRING` with ordered root-cause and repair events, while unavailable
providers and reserved business decisions are rejected as automatic repairs.

This is a controlled real repair: the failed gate, diagnosis, bounded change,
and successful rerun are all preserved rather than reporting the first pass
only.

At final contract binding, the ignored local SQLite runtime database did not
contain the previously consumed contract record. The immutable issued artifact
(`ISSUED_EXECUTION_CONTRACT.json`) remained available and its recorded hash is
the authority for recovery. The operational record is therefore reconstructed
from that exact payload as already consumed, rather than generating a new
contract or altering its issued contents, and is then bound to the final
commit. This repairs transient local runtime state without changing the
approved scope or the committed evidence.
