# Manual Setup

The following instructions have been put together for Ubuntu 18.04 and 20.04. However, the templates and instructions should work on other versions/distributions with minimal changes.

# Table of Contents

* [Prerequisites](#prerequisites)
  * [Minimum Python Version](#python)
  * [Required Packages](#packages)
* [Database Support](#database)
* [SnitchDNS](#setup-snitchdns)
  * [Clone Repo](#clone)
  * [Virtual Environment](#virtual-environment)
  * [Environment Variables](#setup-env-variables)
  * [Initialise Database and Cron](#setup-database-and-cron)
  * [Initialise Settings](#initial-settings-optional) (optional)
  * [Permissions](#permissions)
* [System Service](#setup-system-service)
  * [Create Service](#create-service-file)
  * [Install Service](#install-service)
* [Web Server](#web-server)
  * [SSL Certificates](#ssl-certificates)
  * [Apache](#apache)
    * [Install](#install-apache)
    * [Virtual Host](#setup-apache-vhost)
  * [nginx](#nginx)
    * [Install](#install-nginx)
    * [Virtual Host](#setup-nginx-vhost)
* [Forwarding DNS Port](#iptables)
* [Conclusion](#conclusion)
    
## Prerequisites

### Python

Python 3.6+ is required for SnitchDNS to work.

### Packages

Install the following required packages:

```
sudo apt install git python3-pip python3-venv libpq-dev
```

`libpq-dev` is required by the `psycopg2` requirement for Postgres support (to be built while installing requirements.txt).

## Database

Decide which database you want to use in the backend. This document will **not** guide you through installing a DBMS.

For MySQL and Postgres you will need the following details:

* Username
* Password
* Hostname
* Database

Ideally, the user you will use will not be `root`, but a user who will only have access to this one database.

## Setup SnitchDNS

### Clone

Clone this repo locally to the path where SnitchDNS will be running from. In this example, we will use `/opt/snitch`. Keep in mind that you may need elevated permissions to create folders under `/opt`. 

```
git clone https://github.com/ctxis/SnitchDNS /opt/snitch
```

### Virtual Environment

Install python's venv

```
cd /opt/snitch
python3 -m venv venv
. venv/bin/activate
pip --no-cache-dir install -r requirements.txt
deactivate
```

### Setup ENV Variables

This step is very important because SnitchDNS relies heavily in environment variables. Create the following directory and file:

```
mkdir -p /opt/snitch/data/config/env
touch /opt/snitch/data/config/env/snitch.conf
```

Inside `/opt/snitch/data/config/env/snitch.conf` set the following variables (without double quotes):

```
# One of sqlite, mysql, postgres
SNITCHDNS_DBMS=postgres
# The following _DB_ variables are only required for mysql and postgres.
SNITCHDNS_DB_USER=db_user
SNITCHDNS_DB_PW=db_pass
SNITCHDNS_DB_URL=db_host
SNITCHDNS_DB_DB=db_name
# This is used to encrypt session keys, make sure it's random and very long.
SNITCHDNS_SECRET_KEY=RosesAreRedVioletsAreBlueThisMustBeSecretAsWellAsLongToo
# This one is optional. If you decide to use a 'data' folder outside of this folder, set the absolute path here, otherwise do not set this variable.
SNITCHDNS_DATA_PATH=/some/path/to/another/data/folder
```

**Important**: If you use an external `SNITCHDNS_DATA_PATH` path, you need to create a soft link between the 2 `snitch.conf` files, as the service will look into the above path for the file. Also, make sure the user under which SnitchDNS will run, has read/write access to that folder.

Once the config file is ready, create a link to the root directory (this is for the cron to work properly):

```
ln -s /opt/snitch/data/config/env/snitch.conf /opt/snitch/.env
```

### Setup Database and Cron

`venv.sh` helps run `flask` commands without having to manually activate `venv.sh` so you can proxy all your commands through it.

To initialise the database run:

```
./venv.sh flask db init
./venv.sh flask db migrate
./venv.sh flask db upgrade
./venv.sh flask snitchdb
```

### Initial Settings (optional)

This step is optional and can be done via the GUI as well, but it's easier if done now so you could test if the service is working properly.

The `dns_daemon_bind_ip` and `dns_daemon_bind_port` setting will define where the daemon will be listening on.

The `dns_base_domain` is used only for low privileged users as they are restricted to a specific subdomain of the format `*.username.snitch.lan`. However, even if you do not plan on having low privileged users, this variable needs to be set.

```
./venv.sh flask settings set --name dns_daemon_bind_ip --value 0.0.0.0
./venv.sh flask settings set --name dns_daemon_bind_port --value 2024
./venv.sh flask settings set --name dns_base_domain --value www.snitch.lan
```

### Permissions

As SnitchDNS will be running under a web server, we need to make sure that the web user (`www-data` under Ubuntu) has read/write privileges.

```
sudo chown -R www-data:www-data /opt/snitch
```

If you have set an external `SNITCHDNS_DATA_PATH` path, use the above command for that folder too.

Switch to the `www-data` user and install the cron, run:

```
sudo -u www-data /bin/bash
./venv.sh flask crontab add
```

## Setup System Service

### Create Service File

These instructions apply for `systemd`. Under your `./data` directory, create the following structure and file:

```
mkdir -p ./data/config/service/
touch ./data/config/service/snitchdns.service
```

Use the following file as your template: [systemd](/setup/ansible/roles/service/templates/systemd.j2)

Replace the variables in the file with:

| Variable | Replace With | Comment |
| -------- | ------------ | ------- |
| `{{ web.user }}` | `www-data` | This is the user running the service. |
| `{{ web.group }}` | `www-data` | This is the group of the user above. |
| `{{ snitch.destination }}` | `/opt/snitch` | Location where you cloned SnitchDNS |
| `{{ var_data_path }}` | `/opt/snitch/data` | If you specified an external `SNITCHDNS_DATA_PATH`, use that location here. |
| `{{ web.bind_host }}` | `127.0.0.1` | Where the gunicorn web server will be listening on. This should be a localhost address unless you have reason for it not to be. |
| `{{ web.bind_port }}` | `8888` | Port where the gunicorn (not the DNS Daemon) will be listening on. Any port will do. |

### Install Service

Now that the `snitchdns.service` file is ready, we can install the service.

First, create a soft link between the service file and the systemd location where it has to be:

```
sudo ln -s /opt/snitch/data/config/service/snitchdns.service /etc/systemd/system/snitchdns.service
```

Enable the service

```
sudo systemctl enable snitchdns.service
```

And start it

```
sudo systemctl start snitchdns.service
```

To check whether it was successful run:

```
sudo systemctl status snitchdns.service
```

## Web Server

Now that we have SnitchDNS running as a gunicorn service, we need to create a proxy with the web server.

### SSL Certificates

All certificates should be (but you can change their location) in:

```
mkdir -p ./data/config/http
```

If you need to create self signed, use:

```
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout ./data/config/http/ssl.pem -out ./data/config/http/ssl.crt
```

Otherwise put your `ssl.crt` and `ssl.pem` files within the folder `./data/config/http` folder.

### Apache

#### Install Apache

Install Apache and enable all the required modules:

```
sudo apt install apache2
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2enmod ssl
```

#### Setup Apache vhost

Using [this template](/setup/ansible/roles/webserver/templates/apache/ubuntu.vhost.conf.j2) create a config file under `./data/config/http/vhost.conf` and replace the variables with:

| Variable | Replace With | Comment |
| -------- | ------------ | ------- |
| `{{ web.domain }}` | `www.snitch.lan` | Or whichever domain you will be running under. |
| `{{ web.bind_host }}` | `127.0.0.1` | Same as where the gunicorn service is running on. |
| `{{ web.bind_port }}` | `8888` | Same as where the gunicorn service is running on. |
| `{{ var_data_path }}` | `/opt/snitch/data` | If you specified an external `SNITCHDNS_DATA_PATH`, use that location here. |

Now that the configuration is ready, we need to create a link to the `/sites-available` folder of Apache.

```
# Create link
sudo ln -s /opt/snitch/data/config/http/vhost.conf /etc/apache2/sites-available/snitch.conf

# Enable site
sudo a2ensite snitch.conf

# Restart Apache
sudo systemctl restart apache2.service
```

You should be able to visit SnitchDNS via `https://www.snitch.lan` (or whichever domain you set)

### nginx

#### Install nginx

Install nginx and enable all the required modules:

```
sudo apt install nginx
```

#### Setup nginx vhost

Using [this template](/setup/ansible/roles/webserver/templates/nginx/ubuntu.vhost.conf.j2) create a config file under `./data/config/http/vhost.conf` and replace the variables with:

| Variable | Replace With | Comment |
| -------- | ------------ | ------- |
| `{{ web.domain }}` | `www.snitch.lan` | Or whichever domain you will be running under. |
| `{{ web.bind_host }}` | `127.0.0.1` | Same as where the gunicorn service is running on. |
| `{{ web.bind_port }}` | `8888` | Same as where the gunicorn service is running on. |
| `{{ var_data_path }}` | `/opt/snitch/data` | If you specified an external `SNITCHDNS_DATA_PATH`, use that location here. |

Now that the configuration is ready, we need to create a link to the `/sites-enabled` folder of nginx.

```
# Create link
sudo ln -s /opt/snitch/data/config/http/vhost.conf /etc/nginx/sites-enabled/snitchdns

# Restart nginx
sudo systemctl restart nginx.service
```

You should be able to visit SnitchDNS via `https://www.snitch.lan` (or whichever domain you set)

## iptables

SnitchDNS is designed to run under a web server, however it needs to bind a privileged port - 53. To do so, `sudo` privileges are required, but running any web app as `root` is a **bad idea**. Therefore, we need to create an `iptables` rule to forward all traffic from port 53 to 2024 (or whichever port you have configured the SnitchDNS daemon to run).

```
# tcp
sudo iptables -t nat -I PREROUTING --src 0/0 -p tcp --dport 53 -j REDIRECT --to-ports 2024

# udp
sudo iptables -t nat -I PREROUTING --src 0/0 -p udp --dport 53 -j REDIRECT --to-ports 2024
``` 

## Conclusion

At this point, you should have a working SnitchDNS installation and by visiting the home page you will be prompted to create your first user.
