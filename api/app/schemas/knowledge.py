from pydantic import BaseModel


class KnowledgeUploadResponse(BaseModel):
    """Response returned after a successful knowledge document upload."""

    document_id: str
    chunk_count: int
