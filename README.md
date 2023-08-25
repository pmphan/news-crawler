# News crawler for VnExpress and TuoiTre.vn

## Description

Crawl news from vnexpress.net and tuoitre.vn and rank them by total likes in their comments.

## Functionality

- VnExpress crawler: Crawl articles from VnExpress.net, rank them by comment's likes and store results in database.
- TuoiTre crawler: Crawl articles from TuoiTre.vn, rank them by comment's likes and store results in database.

## Quick Start

### Prerequisites

- A running Postgres instance.
- Require Python 3.10 and above.
  - [pipenv](https://pipenv.pypa.io/en/latest/) for ensuring consistent packages and Python version and [asdf](https://asdf-vm.com/) or [pyenv](https://github.com/pyenv/pyenv) for switching between Python versions.
  - _(Alternatively)_ Docker image with appropriate Python version can also be used.

### Installation

1. Clone and go to this repository:
   ```bash
   git clone git@github.com:pmphan/news-crawler.git
   cd news-crawler
   ```

2. Preparing the Python environment:
    - With `pipenv` and `asdf`/`pyenv`. Note `pipenv` might prompt to install appropriate Python version if not present on system:
      ```bash
      pipenv install --python 3.10 --deploy --ignore-pipfile
      ```
    - _(Or)_ Build the Python image with Docker:
      ```
      docker build -t crawler:latest .
      ```

3. Set up Postgres database.
    - `docker-compose.yml` file configures `postgres` and `pgadmin` by default. `docker-compose up -d` for quick set up.
    - Create an `.env` file and populate it with an existing postgres instance:
      ```bash
      # These are default settings even if not set.
      POSTGRES_DB=postgres
      POSTGRES_USER=postgres
      POSTGRES_PASSWORD=postgres
      POSTGRES_HOST=localhost
      POSTGRES_PORT=5432
      # Or, overwritting all above
      POSTGRES_URI=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
      ```

4. Run scrapy crawler (`days_ago=DATE` determines article's published time from which crawler will crawl):
    - With `pipenv`:
      ```bash
      pipenv run scrapy crawl [vnexpress|tuoitre] [-a days_ago=DATE] [--logfile FILE] [--loglevel LEVEL]
      ```
    - With prebuilt Docker image:
      ```bash
      docker run -t --env-file .env [--name container_name] [--network network_name] crawler (vnexpress|tuoitre) [-a days_ago=DATE] [--loglevel LEVEL] [&> LOGFILE]
      ```
      Note on `network` argument:
        - If `.env` use `POSTGRES_HOST=localhost`, `network` has to be `host`, unless Postgres is configured on the same container.
        - If Postgres instance is not connected via loopback interface (e.g. `POSTGRES_HOST=192.168/16` or remote IP) setting `network` argument is not neccessary.
        - When setting up Postgres instance with given `docker-compose.yml`, `network` could be set to `news-crawler_default` (default naming scheme of bridge network created by Docker Compose is `foldername_default`, so change it if your folder name is different, list of networks can be inspected with `docker network ls`), and `.env` can use `POSTGRES_HOST=postgres`.

5. Connect to Postgres instance to read result, or use script (Postgres credentials must be pre-supplied in `.env` or default will be used):
    - With `pipenv`:
      ```bash
      pipenv run python read_result.py [-h] [-o OUTPUT] SITENAME
      ```
    - With Docker image:
      ```bash
      docker run -t --env-file .env [--name container_name] [--network network_name] --entrypoint python crawler read_result.py [-h] (vnexpress|tuoitre) [&> OUTPUTFILE]
      ```
