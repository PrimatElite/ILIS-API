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
  1. `DB_USER` - User
     ```bash
     export DB_USER=db_user_name
     ```
  2. `DB_PASSWD` - Password
     ```bash
     export DB_PASSWD=dp_password
     ```
  3. `DB_HOST` - Host
     ```bash
     export DB_HOST=db_host
     ```
  4. `DB_PORT` - Port
     ```bash
     export DB_PORT=db_port
     ```
  5. `DB_NAME` - Database
     ```bash
     export DB_NAME=db_name
     ```
* It needs to set variable for connection with Redis:
  1. `REDIS_URL` - URL. By default `redis://localhost:6379`.
     ```bash
     export REDIS_URL=redis_url
     ```
* Some variables about server address:
  1. `SCHEME` - `http` or `https`
     ```bash
     export SCHEME=scheme
     ```
  2. `HOST` - host of your server. For local running it is `127.0.0.1:5000`
     ```bash
     export HOST=host
     ```
* Some variables for authorization working:
  1. `GOOGLE_CLIENT_SECRET` - secret of authorization GOOGLE application
     ```bash
     export GOOGLE_CLIENT_SECRET=google_client_secret
     ```
  2. `VK_CLIENT_SECRET` - secret of authorization VK application
     ```bash
     export VK_CLIENT_SECRET=vk_client_secret
     ```
* Some variables for admin view working:
  1. `SECRET_KEY` - secret for Flask-Admin and Flask-Login
     ```bash
     export SECRET_KEY=secret_key
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

## Server running

After setting environment variables it can be run the server by next command:
```bash
flask run
```
