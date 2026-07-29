# Security review

Provider output is untrusted. The repair applies recursive credential-key and
credential-pattern redaction before it is stored in event details or exposed by
any Activity, Provider Output, or Raw Events view. Large text is bounded while
retaining useful beginning and end context. The defensive warning created for a
projection error stores only the exception type, never exception text or the
provider line.

The change does not weaken contract validation, scope binding, worker leases,
or provider launch authorization.
