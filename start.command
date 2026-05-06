#!/bin/bash
# Double-click this file in Finder to start the game.
# It cd's into the public/ folder, starts a local web server, and opens
# Chrome at http://localhost:8000. Cmd+C in the Terminal window to stop.

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/public"

PORT=8000
# If 8000 is busy, try 8001..8010
for p in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010; do
  if ! lsof -iTCP:$p -sTCP:LISTEN >/dev/null 2>&1; then PORT=$p; break; fi
done

echo "Serving Shape Detective on http://localhost:$PORT"
echo "Cmd+C in this window when you're done."
sleep 0.5
( sleep 1 && open "http://localhost:$PORT/?save=false" ) &
python3 -m http.server $PORT
