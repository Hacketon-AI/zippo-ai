# External API Fallback Policy

External API can be used only when:

1. PostgreSQL exact cache has no valid answer.
2. Qdrant semantic memory score is below threshold.
3. Local Qwen3 fails or gives low confidence.
4. The question requires updated external information.
5. User explicitly allows external API.

External API must not be used when:

1. Cache has valid answer.
2. Qdrant has high-confidence memory.
3. User chooses local-only mode.
4. Question is about internal documents already ingested.
5. Task is simple summarization or formatting.

Every external answer must be saved to PostgreSQL and Qdrant with metadata and expiry policy.
