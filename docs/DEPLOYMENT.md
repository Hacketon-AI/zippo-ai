# Deployment Guide — VPS Docker

## Basic Commands

```bash
docker compose up -d
```

Check containers:

```bash
docker ps
```

Check logs:

```bash
docker compose logs -f api
```

Pull models:

```bash
docker exec -it ollama ollama pull qwen3:4b
docker exec -it ollama ollama pull nomic-embed-text
```

## Security Notes

- Do not expose Ollama public port.
- Use Nginx reverse proxy for API/Open WebUI.
- Use firewall.
- Use SSL.
- Backup PostgreSQL and Qdrant volumes.
