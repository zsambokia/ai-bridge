# R22 — Claim closure

`ResolutionClaim` is an immutable scoped Resolution Subject with a required accountable domain, bounded resolution context, and L1 Evidence/L2 Provenance references. Creating it neither decides, approves, publishes nor mutates a domain object. Empty owner/context is rejected. It is intentionally not a status machine or generic uncertainty store: no such lifecycle was approved for this bounded implementation.
