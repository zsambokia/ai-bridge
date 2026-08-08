# Performance Measurement

The focused acceptance command was executed with pytest duration reporting:

```text
python -m pytest projects/tests/test_knowledge_pipeline.py --durations=3 -q
```

Result: 3 passed in **3.60 s**.

The longest reported phase was fresh test setup for the promotion/retrieval
scenario (**3.31 s**); its pipeline call was **0.04 s**. The duplicate pipeline
call was **0.05 s**. These are development-machine measurements, not production
SLOs, and they establish a reproducible baseline for later vector-provider
migration comparisons.
