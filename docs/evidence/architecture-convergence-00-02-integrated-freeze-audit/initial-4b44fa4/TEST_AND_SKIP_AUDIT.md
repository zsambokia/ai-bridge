# Test and skip audit

`python -m pytest`: **369 passed, 29 skipped** in 110.21 seconds. The skips
are established environment/optional-browser or release-gate cases; they were
not treated as proof for this architecture audit and do not conceal the
Diagram 99 conflict. `projects/tests/test_factory_protocol.py` passed all eight
tests, including pre-retrieval L0 rejection, zoning and FFS behavior.
