#!/usr/bin/env bash
# Run every layer of tests. Exit non-zero on first failure.
# Used by .github/workflows/test.yml and `make test`.
set -e
cd "$(dirname "$0")/.."

echo "=== Layer 1: static checks ==="
echo "--> JS syntax (extracts inline <script> from index.html and node --check)"
python3 - <<'PY'
import re, subprocess, tempfile, sys
html = open('public/index.html').read()
scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)
js = '\n'.join(scripts)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write(js); p = f.name
r = subprocess.run(['node','--check', p])
sys.exit(r.returncode)
PY
echo "    OK"

echo "--> Server JS syntax"
node --check server/server.js
echo "    OK"

echo "--> Python compile (rendering + tests)"
python3 -m compileall -q rendering tests
echo "    OK"

echo "--> Asset integrity"
python3 tests/check_assets.py

echo
echo "=== Layer 2: end-to-end ==="
python3 tests/e2e_playthrough.py

echo
echo "=== ALL TESTS PASSED ==="
