#!/usr/bin/env bash
# When SnitchDNS is running via gunicorn, it's not loading the virtual environment - so we have to use this script as
# a proxy.
. venv/bin/activate
export FLASK_APP=app
export FLASK_ENV=development

# Load the SnitchDNS config environment variables.
. data/config/env/snitch.conf

# And now execute whatever was passed through the command line.
"$@"