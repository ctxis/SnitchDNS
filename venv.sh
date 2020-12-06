#!/usr/bin/env bash
# Use this script as a proxy to run flask commands either via CLI or the service.

# Get current script's path - https://stackoverflow.com/a/4774063
VENV_SCRIPT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd "$VENV_SCRIPT"

# Load the SnitchDNS config environment variables.
export $(grep -v '^#' data/config/env/snitch.conf)

SNITCH_FLASK_ENVIRONMENT="production"
if [[ -n "$SNITCHDNS_ENV" ]]; then
  if [[ "$SNITCHDNS_ENV" == "development" ]] || [[ "$SNITCHDNS_ENV" == "production" ]]; then
    SNITCH_FLASK_ENVIRONMENT="$SNITCHDNS_ENV"
  fi
fi

. venv/bin/activate
export FLASK_APP=app
export FLASK_ENV="$SNITCH_FLASK_ENVIRONMENT"

# And now execute whatever was passed through the command line.
"$@"