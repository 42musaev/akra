Test task for a Arka

How to run

First, create a Docker container:

```sh
docker run --name postgres_db -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test_db -d postgres
```

Perform migration:

```sh
make migrate
```

Then start the application::

```sh
make run
```

Be glad that you're alive.:)
