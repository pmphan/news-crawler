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

2. Set up Postgres database. `docker-compose` file configures `postgres` and `pgadmin` by default. `docker-compose up -d` for quick set up.

3. Configure `config/*.ini file` to fit purpose of run.
    - Change `days_ago` in `service.ini` to determine how far back the crawl should run. 
    - Change fields in `[postgres]` to connect to existing database.
    - In `logging.ini`, use `handlers=file` to log to file and `handlers=root` to log to `stdout`.

4. Set up virtual environment and install required packages.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Run script:
```bash
python main.py
```
Or only read result from database without crawling:
```bash
python main.py --result
```