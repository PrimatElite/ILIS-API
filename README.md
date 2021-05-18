# ILIS-API

API for Item Lending Intermediary Service

## Database

This application uses a third party database with PostgreSQL. So, it needs to create and run the database for application working.

## Setup requirements

Before running the server it must to setup all packages for server working.

Use the next command for this:
```bash
pip install -r requirements.txt
```

## Environment variables

It needs to set some environment variables for the correct server working.

* This server works on Flask, so it needs to set `FLASK_APP`:
  ```bash
  export FLASK_APP=app_main.py
  ```
* It needs to set variables for connection with database:
  1. `DB_USER` - user
     ```bash
     export DB_USER=<DB_USER_NAME>
     ```
  2. `DB_PASSWD` - password
     ```bash
     export DB_PASSWD=<DP_PASSWORD>
     ```
  3. `DB_HOST` - host
     ```bash
     export DB_HOST=<DB_HOST>
     ```
  4. `DB_PORT` - port
     ```bash
     export DB_PORT=<DB_PORT>
     ```
  5. `DB_NAME` - database
     ```bash
     export DB_NAME=<DB_NAME>
     ```
* It needs to set variable for connection with Redis:
  1. `REDIS_URL` - URL. By default `redis://127.0.0.1:6379`.
     ```bash
     export REDIS_URL=<REDIS_URL>
     ```
* It needs to set variable for connection with Elasticsearch:
  1. `ELASTICSEARCH_URL` - URL. By default `elasticsearch://127.0.0.1:9200`.
     ```bash
     export ELASTICSEARCH_URL=<ELASTICSEARCH_URL>
     ```
* Some variables about server address:
  1. `SCHEME` - `http` or `https`
     ```bash
     export SCHEME=<SCHEME>
     ```
  2. `HOST` - host of your server. For local running it is `127.0.0.1:5000`
     ```bash
     export HOST=<HOST>
     ```
* Some variables for authorization working:
  1. `GOOGLE_CLIENT_SECRET` - secret of authorization GOOGLE application
     ```bash
     export GOOGLE_CLIENT_SECRET=<GOOGLE_CLIENT_SECRET>
     ```
  2. `VK_CLIENT_SECRET` - secret of authorization VK application
     ```bash
     export VK_CLIENT_SECRET=<VK_CLIENT_SECRET>
     ```
* Some variables for admin view working:
  1. `SECRET_KEY` - secret for Flask-Admin and Flask-Login
     ```bash
     export SECRET_KEY=<SECRET_KEY>
     ```
* Some variables for mails sending:
  1. `MAIL_USERNAME` - Gmail login username
     ```bash
     export MAIL_USERNAME=<MAIL_USERNAME>
     ```
  2. `MAIL_PASSWORD` - Gmail login password
     ```bash
     export MAIL_PASSWORD=<MAIL_PASSWORD>
     ```

If you are using Windows instead of Linux, then use command `set` instead of command `export`.

## Database initialization

After setting environment variables it can be initialized database by next command:
```bash
flask createdb
```

## Migration

The method described above can be used only for creating new tables. For other changes in the database, it is recommended to use migrations.

Initialize migration support for the application:
```bash
flask db init
```
Create the migration script with changes detected:
```bash
flask db migrate
```
Upgrade the database:
```bash
flask db upgrade
```

## Third party services running

* Redis
  ```bash
  docker run -d -p 6379:6379 --name <redis_container_name> redis
  ```
* Celery (in the project directory)
  ```bash
  celery --app app.celery.celery worker --loglevel=INFO
  ```
* Elasticsearch
  ```bash
  docker run -d -p 9200:9200 -e "discovery.type=single-node" --name <elasticsearch_container_name> elasticsearch:7.10.1
  ```

## Server running

After setting environment variables it can be run the server by next command:
```bash
flask run
```

## Docker running

It needs to have some files with environment variables to build and run docker containers:

* `.env` - file with common variables:
  1. `PORT` - outer port
  2. `DB_VOLUME` - local path to the volume directory

* `api.env` - file with variables that were mentioned above:
  ```
  DB_USER
  DB_PASSWD
  DB_HOST
  DB_PORT
  DB_NAME
  SCHEME
  FLASK_APP
  HOST
  GOOGLE_CLIENT_SECRET
  VK_CLIENT_SECRET
  SECRET_KEY
  REDIS_URL
  MAIL_USERNAME
  MAIL_PASSWORD
  ELASTICSEARCH_URL
  ```
  and `WORKERS` - number of workers for gunicorn starting.

* `db.env` - file with variables for database initialization:
  1. `POSTGRES_DB` - database name
  2. `POSTGRES_USER` - database user
  3. `POSTGRES_PASSWORD` - user's password for database

Build and run containers through docker-compose:

```bash
docker-compose rm -f -s
docker-compose up -d --build
```

## Usage

The server is started at 127.0.0.1:5000.
- `/admin` - administrator panel (use Google or VK for login if you have initialized db with `flask createdb`)
- `/api/swagger` - REST API swagger
