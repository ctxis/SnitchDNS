# Environment Variables

## Database

| Type | Name | Description | Required | Expected Value(s) | Default |
| ---- | ---- | ----------- | -------- | ----------------- | ------- |
| Database | `SNITCHDNS_DBMS` | DBMS | No | `sqlite`, `mysql`, `postgres` | `sqlite` |
| Database | `SNITCHDNS_DB_USER` | DB User | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_PW` | DB Password | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_URL` | DB Hostname | Only for `mysql` and `postgres` | | None |
| Database | `SNITCHDNS_DB_DB` | DB Name | Only for `mysql` and `postgres` | | None |
| Data | `SNITCHDNS_DATA_PATH` | Data path to store user files, must be writable by the user running the server. | No | Absolute path to location | `./data` folder within this repo. |
| Session | `SNITCHDNS_SECRET_KEY` | Secret Key used to encrypt sessions | Yes | Random value | | |
