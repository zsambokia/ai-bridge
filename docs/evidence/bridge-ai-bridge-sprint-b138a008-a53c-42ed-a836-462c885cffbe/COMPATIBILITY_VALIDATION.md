# Compatibility validation

- Existing `ExecutionProgressEvent` sequence ordering remains authoritative.
- `provider_event_id` is nullable, so historical events and non-provider events
  require no backfill.
- The event API keeps its existing Activity response and adds explicit Provider
  Output and Raw Events views.
- Unknown provider event shapes fall back to a durable observational message;
  no provider command, contract, or lifecycle decision is inferred from them.
- The adapter keeps the existing `start_with_activity` interface while adding a
  defaulted `source_stream` argument to the private reader.
