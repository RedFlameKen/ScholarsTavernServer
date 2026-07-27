# Scholar's Tavern Server
This is the Django backend server of the [Scholar's
Tavern](https://github.com/RedFlameKen/ScholarsTavern) React app.

## Requirements
Make sure to have the following installed:
- Python (>= 3.14.5)
- postgres (optional)

## Setup
Clone the project:
```bash
git clone https://github.com/RedFlameKen/ScholarsTavernServer
cd ScholarsTavernServer
```

---
### Postgres
Make sure a `.pg_service.conf` and a `.pass_file` file is needed as
configuration for the postgres db connection.

if the postgres db server is running locally, the following format for
`.pg_service.conf` is recommended:
```conf
[st_db_service]
host=localhost
dbname=scholars_tavern_db
user=<postgres_user>
port=5432
```

The following `.pass_file` should then be used:
```
localhost:5432:scholars_tavern_db:<postgres_user>:<password>
```

The `.pass_file` might require its permission to be changed, in which case, run
the following:
```bash
chmod 600 .pass_file
```

if postgres is running elsewhere, edit the configuration files accordingly.

---
### Django Server
Create a python virtual environment, and then source it. for example:
```bash
python -m venv .venv/
source .venv/bin/activate
```

Next, make sure you have the dependencies installed in the project by running
the following command:
```bash
pip install -r requirements.txt
```
---

## Running
After ensuring that the postgres server is running, the python environment is
set up, and dependencies are installed, setup PGSERVICEFILE environment
variable to tell the system where to find the `.pg_service.conf` file.
Otherwise, the server will fail to start. For example:
```bash
export PGSERVICEFILE=.pg_service.conf
```

Finally, to run the server, run the following command:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

If running on a platform like "Render", the `runserver` command might need to
be adjusted:
```bash
python manage.py 0.0.0.0:8000
```
