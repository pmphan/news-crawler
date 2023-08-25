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
pip install -r requirements.txt
      pipenv run python read_result.py [-h] [-o OUTPUT] SITENAME

5. Run scrapy crawler (`days_ago=DATE` determines article's published time from which crawler will crawl):
```bash
scrapy crawl [vnexpress|tuoitre] [-a days_ago=DATE] [--logfile FILE] [--loglevel LEVEL]
      pipenv run python read_result.py [-h] [-o OUTPUT] SITENAME
      ```

5. Connect to Postgres instance to read result, or use script (Postgres credentials must be pre-supplied in `.env` or default will be used):
    - With `pipenv`:
      ```bash
```