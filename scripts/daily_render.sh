#!/bin/bash
# Daily: re-pull mochi-kids data from Mongo and re-render the analysis reports.
# Meant to be run unattended (launchd / cron) at the end of each day.
# Uses absolute interpreter paths because launchd runs with a bare environment.
#
# Manual run:  bash scripts/daily_render.sh
set -uo pipefail

REPO="/Users/brialong/Documents/GitHub/mochi-kids"
PY="/opt/anaconda3/bin/python3"
RSCRIPT="/usr/local/bin/Rscript"
LOG="$REPO/analysis/daily_render.log"

cd "$REPO" || exit 1
stamp() { date "+%Y-%m-%d %H:%M:%S %Z"; }
{
  echo "===== $(stamp) : daily_render start ====="
  echo "-- fetch_data.py --"
  "$PY" analysis/fetch_data.py 2>&1
  echo "-- render kid_analysis.Rmd --"
  "$RSCRIPT" -e 'rmarkdown::render(here::here("analysis","kid_analysis.Rmd"), quiet=TRUE)' 2>&1 \
    && echo "  kid_analysis.html OK" || echo "  kid_analysis FAILED"
  echo "-- render crossover_analysis.Rmd --"
  "$RSCRIPT" -e 'rmarkdown::render(here::here("analysis","crossover_analysis.Rmd"), quiet=TRUE)' 2>&1 \
    && echo "  crossover_analysis.html OK" || echo "  crossover_analysis FAILED"
  echo "===== $(stamp) : daily_render done ====="
  echo
} >> "$LOG" 2>&1
