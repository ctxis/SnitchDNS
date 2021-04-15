# Update Version

Below are the instructions on how to update an existing installation of SnitchDNS.

## Update Codebase

```
# Stop the SnitchDNS system service
sudo systemctl stop snitchdns.service

# Switch to the user that owns the files in the installation directory. This is usually the user running the web server.
sudo -u www-data /bin/bash

# Navigate to SnitchDNS' installation path.
cd /opt/snitch

# Make sure you're on the master branch, and pull the latest and greatest code.
git checkout master
git pull
```

## Update Requirements and Database

```
# Enable the virtual environment.
. venv/bin/activate

# Install requirements.
pip install -r requirements.txt

# Now that you have the latest and greatest code, update the database.
flask db migrate
flask db upgrade
flask snitchdb
```

## Restart Service

```
# After exiting from the www-data user's shell, start the service.
sudo systemctl start snitchdns.service
```
