#!/usr/bin/env bash
# Dedicated ephemeral GitHub-hosted runner only. No external database input.
set -euo pipefail
test "$GITHUB_ACTIONS" = true
test "$RUNNER_ENVIRONMENT" = github-hosted
test "$RW_SI_ENABLE_G04_A2_LAB" = 1
password="$(openssl rand -hex 32)"
marker="$(openssl rand -hex 32)"
echo "::add-mask::$password"
echo "::add-mask::$marker"
# No volume, no reuse of existing containers, loopback host port only.
docker run -d --rm --name rw-g04-a2-lab \
  -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=g04_bootstrap -e POSTGRES_DB=rw_g04_a2_lab \
  -e POSTGRES_PASSWORD="$password" -e POSTGRES_HOST_AUTH_METHOD=scram-sha-256 postgres:16 >/dev/null
for i in $(seq 1 60); do
  if docker exec rw-g04-a2-lab pg_isready -h 127.0.0.1 -U g04_bootstrap -d rw_g04_a2_lab >/dev/null; then break; fi
  sleep 1
done
docker exec rw-g04-a2-lab pg_isready -h 127.0.0.1 -U g04_bootstrap -d rw_g04_a2_lab >/dev/null
printf "CREATE TABLE public.g04_ephemeral_marker(marker text NOT NULL); INSERT INTO public.g04_ephemeral_marker VALUES ('%s');\n" "$marker" |
  docker exec -i rw-g04-a2-lab psql -X -v ON_ERROR_STOP=1 -U g04_bootstrap -d rw_g04_a2_lab >/dev/null
printf 'RW_G04_A2_DSN=postgresql://g04_bootstrap:%s@127.0.0.1:55432/rw_g04_a2_lab\nRW_G04_A2_MARKER=%s\n' "$password" "$marker" >> "$GITHUB_ENV"
