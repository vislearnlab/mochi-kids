.PHONY: serve test test-static test-e2e clean

# Serve the static site locally and open the browser.
serve:
	cd public && python3 -m http.server 8000 &
	sleep 1 && open "http://localhost:8000/?save=false"

# Full test suite (matches CI).
test:
	bash tests/run_all.sh

# Just the cheap static checks.
test-static:
	python3 tests/check_assets.py

# Just the Playwright e2e.
test-e2e:
	python3 tests/e2e_playthrough.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf rendering/meshes rendering/rotation_frames
