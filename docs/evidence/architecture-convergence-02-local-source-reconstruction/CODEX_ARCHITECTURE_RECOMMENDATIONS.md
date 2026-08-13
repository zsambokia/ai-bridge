# Architecture recommendations

1. Approve a terminology/ownership mapping for CSM, CSE, Cognitive Processing,
   Context Profile, Context Package, and Artifact before code changes.
2. Run a repository write-path audit for Conversation, CU, CSE/CSM, Mission
   Resolution, Mission, and Factory Chat; make authority violations visible in
   tests.
3. Create a separately approved Artifact/Evidence contract covering
   immutability, version creation, claims, relations, assurance, and retention.
4. Specify FactoryIP, Factory Message, FFS, and zoning as protocol/boundary
   architecture before adding transport or UI features.
5. Adopt approved changes into the Constitution Book and ADRs in small,
   evidence-backed sprints; then measure implementation conformance.

These recommendations do not authorize implementation work.
