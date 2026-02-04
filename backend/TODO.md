# Arithmetic Merge Backend

## Getting started

- Create a secret key for Flask session in an .env file. You can do so with python's
  secrets.token_hex(32) function.
- Initiailize a database (if it does not exist yet)
  - Go to the project root directory and type python or python3 to initialize a python shell
  - In the python shell, type:
- To test the backend:
  - run pip install pytest if you do not have pytest installed
  - type $pytest to run tests

```python
from backend.app import app, db
with app.app_context():
    db.create_all()
```

## Todo for backend

- Add unit and integration tests
- Change to Postgres for deployment (database only contains test data, so no need to migrate)
- Optional caching, optimizing game.py

After cleaning up the backend and the frontend, prepare for deployment in Vercel.
