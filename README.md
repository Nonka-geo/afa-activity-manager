# AFA Activity Manager

## Local development

Install the project dependencies with uv:

```text
uv sync
```

Initialize the local database and create the built-in application roles:

```text
uv run python manage.py migrate
```

Run Django checks and tests:

```text
uv run python manage.py check
uv run pytest
```

Start the local development server:

```text
uv run python manage.py runserver
```
