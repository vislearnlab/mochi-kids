# .github/

GitHub-specific configuration. Two workflows.

## workflows/test.yml

Runs on every push and PR to `main`. Sets up Node 20 + Python 3.11,
installs Playwright + chromium, then runs `bash tests/run_all.sh`
which executes:

- inline-`<script>` JS syntax check (`node --check`)
- server JS syntax check
- Python compile (`python -m compileall`)
- asset integrity (`tests/check_assets.py`)
- Playwright end-to-end play-through (`tests/e2e_playthrough.py`)

Fails the workflow on any error. See `TESTING.md` at the repo root for
the full strategy.

## workflows/pages.yml

Builds and deploys the static site to GitHub Pages on every push to
`main`. Uploads `public/` as the artifact and runs
`actions/deploy-pages@v4`. After the first run, the site lives at
`https://vislearnlab.github.io/mochi-kids/`.

## Recommended branch protection (set in repo Settings → Branches)

- Require PR before merging to `main`
- Require status checks to pass (`test` from `test.yml`)
- Require branches to be up-to-date before merging
- (Optional) Require linear history
