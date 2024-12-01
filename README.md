# shop-backend

*English* | [简体中文](https://github.com/Jay-716/shop-backend/blob/master/README.zh-CN.md)

---

A backend api implementation for an online shopping website, based on FastAPI.

This repo will stay in public for **3 months only**!

Student ID: 202230442159

Student Name: 卢俊杰


## Requirements

 - Python >= 3.12
 - Packages listed in `requirements.txt`

This is the recommended requirements. Older versions may work but is not tested.


## Usage

Create your own `config.yaml` according to `config.py` first. (See `config.yaml.example`)

### Docker

```sh
# mkdir /srv/shop/{mysql,log,file}
# docker compose up
```

### Manually

 - Create a virtualenv (Optional)
 - `pip install -r requirements.txt`
 - `uvicorn app:app`


## Development Guide

Source tree explained:

Dockerfile, docker-\*: Docker related files.

config.py: Config loading entrypoint.

alembic: alembic root directory, for migrating db models.

app: Program source.

 - models: sqlalchemy orm models.
 - routers: API endpoints. Main API logic.
 - schemas: API params and output schemas.
 - utils: Utilities.
 - auth.py: Authentication logic.
 - db.py: Database sessions.


## Tips

Once you have successfully started the application, you can get an informational api and schema list by accessing `http://${BaseURL}/docs` if `enable_doc` is `true` in your `config.yaml`.


