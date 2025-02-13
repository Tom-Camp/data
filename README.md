# Tom.Camp Data

A modern FastAPI application using MongoDB with Beanie ODM, and UV for dependency management. The
application is configured to run with the application and the database running in Docker
containers using docker-compose.

The site is configured to ingest and serve data from different sources, using both API key and
username and password authentication.

## Features

* [FastAPI](https://fastapi.tiangolo.com/) for building high-performance APIs
* [MongoDB](https://www.mongodb.com/) integration using Beanie ODM
* Async database operations
* Comprehensive test suite with pytest
* Code quality tools with [pre-commit](https://pre-commit.com/) hooks
* Dependency management with [UV](https://docs.astral.sh/uv/)

## Prerequisites

* Python 3.11+
* MongoDB 4.0+
* UV package manager

## Project Structure

```shell
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   └── __init__.py
│   ├── routes/
│   │   └── __init__.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```
## Installation

```shell
# Clone the repository
git clone https://github.com/Tom-Camp/data.git
cd data

# Initialize UV project
uv init --app

# Install dependencies
uv sync
```
## Configuration

Create a .env file in the project root:

```shell
APP_NAME="[APP_NAME]"

MONGO_DB="[MONGO_DB]"
MONGO_HOST="[MONGO_HOST]"
MONGO_PASS="[MONGO_PASS]"
MONGO_PORT="27017"
MONGO_USER="[MONGO_USER]"

SECRET_KEY="[SECRET_KEY]"
HASH_ALGORITHM="[HASH_ALGORITHM]"

INITIAL_USER_NAME="[INITIAL_USER_NAME]"
INITIAL_USER_MAIL="[INITIAL_USER_MAIL]"
INITIAL_USER_PASS="[INITIAL_USER_PASS]"
```

The application will create an initial user with the provided credentials if
the user does not exist in the database. This user will have admin privileges.

## Development Setup

```shell
# Install pre-commit hooks
pre-commit install

# Start the development server
uv run uvicorn app.main:app --reload
```

## Testing

```shell
# Run tests with coverage
uv run pytest --cov=app tests/
```

## Pre-commit Hooks

* trailing-whitespace
* end-of-file-fixer
* [isort](https://github.com/pycqa/isort)
* [flake8](https://github.com/PyCQA/flake8)
* [mypy](https://github.com/pre-commit/mirrors-mypy)
* [bandit](https://github.com/PyCQA/bandit)
* [uv-export](https://github.com/astral-sh/uv-pre-commit)

## API Documentation

Once running, access the API documentation at:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
