#!/usr/bin/env bash

# Mostly using shebangs to find files, if they are not in the right format,
# they will be ignored

# Format python files
rg 'env -S uv run' --files-with-matches | sed '/health/d' | xargs -I{} uvx ruff format {}

# Check python files
rg 'env -S uv run' --files-with-matches | sed '/health/d' | xargs -I{} uvx ruff check --fix {}

# Check bash files
rg 'env bash' | awk -F: '{print $1}' | xargs -I{} shellcheck -f diff -- {}
