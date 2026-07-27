# Secret redaction and storage proof

Provider secret material is external only. Database records retain an optional identifier-like reference, never a value. MCP projections omit `configuration` and `credential_binding`; execution event filtering removes secret-like keys. A repository scan found no supplied credential value in the diff or evidence.
