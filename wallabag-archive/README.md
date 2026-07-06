# Wallabag Archive (decommissioned 2026-07-06)

Decommissioned because the reads repo (brfid/reads) + git history provides
all the value with none of the operational overhead.

## What was deployed
- wallabag/wallabag:latest (2.6.14) + postgres:16-alpine
- Docker Compose on RPi 5 (jean-claude)
- HTTPS via Tailscale Serve at raspberrypi.tailc4f7d6.ts.net
- 1 user: bede (toteslates@gmail.com), OAuth client id=2

## To reconstruct
1. Restore docker-compose.yml and .env (secrets: DB_PASSWORD, WALLABAG_SECRET)
2. `docker compose up -d`
3. Re-run Tailscale Serve: `tailscale serve --bg --https 443 http://127.0.0.1:8080`
4. Create user: `docker exec wallabag-app php bin/console wallabag:user:create bede toteslates@gmail.com <password> --env=prod`
5. Create OAuth client via the wallabag:oauth:create-client command
6. API credentials at /opt/wallabag/api_credentials.json

## Why it was removed
- Wallabag's value is distraction-free reading + offline save — not needed when
  reading at source URLs and tracking links in git
- Docker maintenance, OAuth token management, health checks, backups
- Fragile integer IDs that break on rebuild
- The reads repo's `url` field + git history is sufficient

## Data
- Database: /opt/wallabag/data/postgres (PostgreSQL data volume)
- App data: /opt/wallabag/data/wallabag (images, cache)
- These persist on disk but are not backed up after decommission
