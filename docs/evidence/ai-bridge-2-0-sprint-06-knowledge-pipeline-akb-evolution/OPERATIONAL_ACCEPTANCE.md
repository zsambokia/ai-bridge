# Operational Acceptance

## Intended runtime

Local Factory Development Mode execution on `main`, based on baseline
`4831371c1903d3f5a652f44912cbb8ca1711fdea`. No managed provider, heartbeat or
Bridge-issued execution was used, as explicitly authorized by the Product
Owner for this self-development Sprint.

## Runtime smoke

The executed `test_pipeline_requires_governed_promotion_then_indexes_and_retrieves`
scenario is the operational smoke for the new pipeline. It runs the real Django
ORM, canonical Runtime candidate producer, AKB governance approval, local
embedding/cache provider, `DjangoVectorStore` and durable
`KnowledgeContextPackage` storage in a fresh test database. It verified this
observable chain:

```text
Runtime candidate -> review -> approval -> active AKB entry
-> embedding/index -> semantic retrieval package
```

Result: PASS. The full repository regression also passed 361 tests in 109.20
seconds. This evidence is local Factory evidence only; it makes no claim about
an unobserved deployed environment or managed-provider execution.
