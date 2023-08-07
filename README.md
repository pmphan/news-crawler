# News crawler for VnExpress and TuoiTre.vn

## Description

Crawl news from vnexpress.net and tuoitre.vn and rank them by total likes in their comments.

## Functionality

- VnExpress crawler: Crawl articles and comments from their exposed API point and store them in database.

## Quick Start

1. Clone this repository:
```bash
git clone git@github.com:pmphan/news-crawler.git
```

2. Set up Postgres database. 
    - Create an .env file and populate it with an existing postgres instance:
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
    - `docker-compose` file configures `postgres` and `pgadmin` by default. `docker-compose up -d` for quick set up.

4. Set up virtual environment and install required packages.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Run scrapy crawler (`days_ago=DATE` determines article's published time from which crawler will crawl):
```bash
scrapy crawl [vnexpress|tuoitre] [-a days_ago=DATE] [--logfile FILE] [--loglevel LEVEL]
```

4. Connect to Postgres instance to read result, or use script (Postgres credentials must be pre-supplied in `.env` or default will be used):
```bash
python read_result.py [-h] [-t TABLENAME] [-o OUTPUT]
```