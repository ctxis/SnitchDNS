FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

# Locations.
ARG INSTALL_PATH=/opt/snitchdns
ARG DATA_PATH=$INSTALL_PATH/data
ARG CONFIG_PATH=$DATA_PATH/config
ARG REPO=https://github.com/ctxis/SnitchDNS

# Configuration.
ARG SNITCHDNS_DBMS=sqlite
ARG SNITCHDNS_DB_USER=none
ARG SNITCHDNS_DB_PW=none
ARG SNITCHDNS_DB_URL=none
ARG SNITCHDNS_DB_DB=none
ARG SNITCHDNS_SECRET_KEY=RosesAreRedVioletsAreBlueThisMustBeSecretAsWellAsLongToo

ARG SNITCH_DOMAIN=www.snitch.docker
ARG BASE_DOMAIN=snitchdns.docker

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install pre-requisites.
RUN apt update && \
    apt install -y \
    git \
    python3-pip \
    python3-venv \
    libpq-dev \
    apache2 \
    openssl \
    cron \
    iptables && rm -rf /var/lib/apt/lists/*

# Install SnitchDNS.
RUN git clone $REPO /opt/snitchdns

WORKDIR $INSTALL_PATH

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip --no-cache-dir install -r requirements.txt && \
    deactivate

# Configure SnitchDNS.
RUN mkdir -p $CONFIG_PATH/env
RUN mkdir -p $CONFIG_PATH/service
RUN mkdir -p $CONFIG_PATH/http
RUN touch $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_DBMS=$SNITCHDNS_DBMS > $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_DB_USER=$SNITCHDNS_DB_USER >> $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_DB_PW=$SNITCHDNS_DB_PW >> $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_DB_URL=$SNITCHDNS_DB_URL >> $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_DB_DB=$SNITCHDNS_DB_DB >> $CONFIG_PATH/env/snitch.conf && \
    echo SNITCHDNS_SECRET_KEY=$SNITCHDNS_SECRET_KEY >> $CONFIG_PATH/env/snitch.conf
RUN ln -s $CONFIG_PATH/env/snitch.conf $INSTALL_PATH/.env

RUN ./venv.sh flask db init && \
    ./venv.sh flask db migrate && \
    ./venv.sh flask db upgrade && \
    ./venv.sh flask snitchdb && \
    ./venv.sh flask crontab add

RUN ./venv.sh flask settings set --name dns_daemon_bind_ip --value 0.0.0.0 && \
    ./venv.sh flask settings set --name dns_daemon_bind_port --value 2024 && \
    ./venv.sh flask settings set --name dns_base_domain --value $BASE_DOMAIN

RUN a2enmod proxy proxy_http rewrite ssl
RUN openssl req \
    -x509 \
    -nodes \
    -days 3650 \
    -newkey rsa:2048 \
    -keyout $CONFIG_PATH/http/ssl.pem \
    -out $CONFIG_PATH/http/ssl.crt \
    -subj "/C=GB/CN=${SNITCH_DOMAIN}"

RUN cp ./setup/ansible/roles/webserver/templates/apache/ubuntu.vhost.conf.j2 $CONFIG_PATH/http/vhost.conf
RUN sed -i "s|{{ web.domain }}|${SNITCH_DOMAIN}|g" $CONFIG_PATH/http/vhost.conf
RUN sed -i "s|{{ web.bind_host }}|127.0.0.1|g" $CONFIG_PATH/http/vhost.conf
RUN sed -i "s|{{ web.bind_port }}|8888|g" $CONFIG_PATH/http/vhost.conf
RUN sed -i "s|{{ var_data_path }}|${DATA_PATH}|g" $CONFIG_PATH/http/vhost.conf
RUN ln -s $CONFIG_PATH/http/vhost.conf /etc/apache2/sites-available/snitch.conf
RUN a2ensite snitch.conf

VOLUME $DATA_PATH

EXPOSE 80 443 2024

CMD ["/bin/bash", "setup/docker/entrypoint.sh"]