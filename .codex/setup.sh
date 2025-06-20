#!/usr/bin/env bash
# Setup script executed automatically during Codex container setup.
# Not intended for general use; local installations should run setup.sh.
# Install dependencies used during testing and examples.

set -euo pipefail

# Update package lists
#apt-get update

# Install Python and basic tools
#apt-get install -y --no-install-recommends python3 python3-pip git
#apt-get clean

# Install a minimal subset of dependencies for the test suite. The environment
# already includes Python and common tooling, so we avoid heavy optional
# packages and model downloads during the 300s setup window.
# Install the project and its dependencies as declared in pyproject.toml
if [ -f pyproject.toml ]; then
    # Editable install with extras so source changes are picked up without
    # reinstalling and optional dependencies are available for the CLI.
    pip3 install --upgrade setuptools
    pip3 install -e ".[embedding,local]" --no-build-isolation
fi

# Tools used by CI for linting and testing
pip3 install flake8 pytest

# Additional tools and libraries used in tests and linting
pip3 install nltk pre-commit

# CLI dependencies that may not be declared in requirements.txt
# (rich and typer are already installed above)

# Heavy optional dependencies needed for evaluations and local model examples
pip3 install torch sentence-transformers transformers spacy \
    google-generativeai evaluate


