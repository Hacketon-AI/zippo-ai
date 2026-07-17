# Nginx + SSL (VPS)

Contoh konfigurasi production dengan **satu domain**: web UI dan API dilayani
dari domain yang sama, jadi tidak ada masalah CORS sama sekali.

```
Browser ──HTTPS──> Nginx (VPS)
                    ├── /api/  ──> 127.0.0.1:8000  (container api)
                    └── /      ──> 127.0.0.1:3002  (container web)
```

Ollama, PostgreSQL, dan Qdrant TIDAK pernah diekspos lewat Nginx.

## 1. Prasyarat

- Domain sudah mengarah ke IP VPS (A record), misal `ai.example.com`.
- Docker compose sudah jalan: `api` di port 8000, `web` di port 3002.
- Port 8000 dan 3002 cukup bind ke localhost saja (lihat bagian 5).

## 2. Install Nginx + Certbot

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

## 3. Konfigurasi Nginx

Buat `/etc/nginx/sites-available/zippo-ai`:

```nginx
server {
    listen 80;
    server_name ai.example.com;

    # Certbot akan mengubah blok ini menjadi redirect ke HTTPS.
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ai.example.com;

    # Diisi otomatis oleh certbot --nginx; biarkan placeholder ini
    # kalau menjalankan certbot setelahnya.
    ssl_certificate     /etc/letsencrypt/live/ai.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.example.com/privkey.pem;

    # Batas upload (samakan dengan validasi upload di API).
    client_max_body_size 10m;

    # --- API (FastAPI, port 8000) ---
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Jawaban LLM lokal bisa lambat di VPS kecil; jangan putus di 60s.
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # --- Web UI (nginx container, port 3002) ---
    location / {
        proxy_pass http://127.0.0.1:3002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktifkan dan pasang sertifikat:

```bash
sudo ln -s /etc/nginx/sites-available/zippo-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d ai.example.com
```

Certbot otomatis memperpanjang sertifikat (cek: `sudo certbot renew --dry-run`).

## 4. Isi `.env` di VPS

Karena web dan API satu domain, `VITE_API_BASE_URL` diisi domain itu juga —
frontend memanggil `https://ai.example.com/api/v1/...` dan Nginx yang
meneruskan ke container api. CORS tinggal satu origin.

```bash
CORS_ORIGINS=https://ai.example.com
VITE_API_BASE_URL=https://ai.example.com
```

Lalu rebuild (nilai VITE_* di-bake saat build, restart saja tidak cukup):

```bash
docker compose build web
docker compose up -d web api
```

## 5. Tutup port publik

Dengan Nginx di depan, container tidak perlu terbuka ke publik. Di
`docker-compose.yml`, bind api dan web ke localhost:

```yaml
  api:
    ports:
      - "127.0.0.1:8000:8000"
  web:
    ports:
      - "127.0.0.1:3002:3001"
```

Postgres/Qdrant sudah localhost-only, dan Ollama sudah internal-only — jangan
diubah. Pastikan juga firewall hanya membuka 22, 80, 443:

```bash
sudo ufw allow 22,80,443/tcp
sudo ufw enable
```

## 6. Checklist verifikasi

```bash
curl -fsS https://ai.example.com/api/v1/health        # {"status":"ok",...}
curl -i   https://ai.example.com                       # 200, HTML web UI
curl -i   http://IP_VPS:8000/api/v1/health             # HARUS gagal (timeout/refused)
```

Terakhir: buka web di browser → login → kirim chat.

## Troubleshooting

| Gejala | Penyebab umum |
|---|---|
| 502 dari Nginx | Container api mati / port bind salah → `docker compose ps`, `docker logs personal-ai-api` |
| CORS error di console browser | `CORS_ORIGINS` di `.env` tidak sama persis dengan URL di address bar (perhatikan `https://` dan tanpa trailing slash) |
| Frontend memanggil `localhost:8000` | `VITE_API_BASE_URL` belum diset saat build → set di `.env`, lalu `docker compose build web` |
| Jawaban chat terputus | `proxy_read_timeout` terlalu kecil |
