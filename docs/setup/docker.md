# Docker

Note: The provided Dockerfile is meant to be used as a demo only.

Navigate to `./setup/docker` and run:

```
docker build -t snitchdns .
docker run -p 80:80 -p 443:443 -p 53:2024/udp --name snitch snitchdns
```

The following build arguments are available:

```
ARG REPO=https://github.com/ctxis/SnitchDNS

ARG SNITCHDNS_DBMS=sqlite
ARG SNITCHDNS_DB_USER=none
ARG SNITCHDNS_DB_PW=none
ARG SNITCHDNS_DB_URL=none
ARG SNITCHDNS_DB_DB=none
ARG SNITCHDNS_SECRET_KEY=RosesAreRedVioletsAreBlueThisMustBeSecretAsWellAsLongToo

ARG SNITCH_DOMAIN=www.snitch.docker
ARG BASE_DOMAIN=snitchdns.docker
```

If the default values are not changed, make sure to put `127.0.0.1 www.snitch.docker` in your `/etc/hosts` file.
After the container has been built and has been started, test it by:

```
dig -t TXT www.google.com @YOUR_LOCAL_IP_ADDRESS
```