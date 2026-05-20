# API SPEC — Personal AI Assistant

## Base URL

```text
/api/v1
```

## GET /health

Returns service status.

## POST /chat

Request:

```json
{
  "message": "string",
  "session_id": "optional",
  "mode": "auto|local_only|external_allowed",
  "use_memory": true
}
```

Response:

```json
{
  "answer": "string",
  "source": "cache|memory|ollama|external",
  "session_id": "string",
  "metadata": {}
}
```

## POST /knowledge/upload

Upload knowledge document.

## POST /feedback

Save correction from user.
