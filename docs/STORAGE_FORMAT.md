# Storage Format (Legacy)

This document describes the JSON/NumPy layout used by earlier versions of Compact Memory to persist a memory store on disk. It is kept for reference only.
Current releases focus on in-memory operation or external vector store backends.

```
memory/
├── meta.yaml
├── belief_prototypes.json
├── prototype_vectors.npy
├── raw_memories.jsonl
└── evidence.jsonl        # log of prototype ↔ memory links
```

## `meta.yaml`

`meta.yaml` holds global information about the store:

```yaml
version: 1                     # storage schema version
embedding_model: all-MiniLM-L6-v2
embedding_dim: 384            # vector dimension
normalized: true              # embeddings must be unit vectors
created_at: "2024-01-01T00:00:00Z"
updated_at: "2024-01-01T00:00:00Z"
```

The `version` field defines the storage schema.  The current code understands
version `1`.  Should a future release change the file layout, this value will be
incremented and migration logic will be added.  Tools loading a memory store should
check the `version` field before attempting to read the other files.

## Prototype files

`belief_prototypes.json` stores the prototype metadata without vectors.  Each
entry is a JSON object matching the `BeliefPrototype` model.  The associated
vectors are stored row‑for‑row in `prototype_vectors.npy` which is loaded with
NumPy.

## Memories

Individual chunks of text are appended to `raw_memories.jsonl`.  Each line is a
`RawMemory` JSON object containing the text, its hash, optional embedding and the
prototype it belongs to.

## Logs

During ingestion the agent writes an auxiliary log:

- `evidence.jsonl` records which memories contributed to each prototype.  It can
  be analysed offline to track provenance or compute statistics.

The storage format is purposely lightweight and versioned so that different
backends or migration tools can be implemented without breaking existing data.
