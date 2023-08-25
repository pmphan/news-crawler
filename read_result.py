import asyncio
from os import environ
from dotenv import load_dotenv
from argparse import ArgumentParser

from database.services.article_service import crawler_db_mapping
from database.postgres import Postgres


load_dotenv()

def init_postgres():
    """
    Initiate a postgres instance from settings in .env
    Return a Postgres instance
    """
    pguri = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
        environ.get("POSTGRES_USER", "postgres"),
        environ.get("POSTGRES_PASSWORD", "postgres"),
        environ.get("POSTGRES_HOST", "localhost"),
        environ.get("POSTGRES_PORT", 5432),
        environ.get("POSTGRES_DB", "postgres")
    )
    postgres = Postgres(uri=pguri)
    return postgres

async def close_postgres(postgres: Postgres):
    """Close the Postgres instance."""
    await postgres.close_db()

async def get_ranked_result(postgres: Postgres, DBService, output=None):
    """
    Save output to a file. If not specified print to stdout instead.

    Args:
        postgres: The Postgres instance
        DBService: One of Service type class
        output: path to output file.
    """
    async with postgres.engine.connect() as db_conn:
        result = await DBService.get_all_article_ranked(db_conn)
    result_map = map(lambda a: f"{a.score:7d} {a.url}\n", result)
    if output:
        with open(output, 'w') as f:
            f.writelines(f"Wrote {len(result)} output to {output}\n")
            f.writelines(result_map)
    else:
        print(f"Logging {len(result)} output to stdout...")
        for line in result_map:
            print(line, end="")

async def main():
    parser = ArgumentParser(prog="read_result", description="Read result from Postgres Database.")
    parser.add_argument("SITENAME", help="Select database to read from (vnexpress|tuoitre)")
    parser.add_argument("-o", "--output", help="File to save result to. If not set default to stdout.", required=False, default=None)
    args = parser.parse_args()
    DBService = crawler_db_mapping[args.SITENAME]
    pg_conn = init_postgres()
    await get_ranked_result(pg_conn, DBService, args.output)
    await close_postgres(pg_conn)

if __name__ == "__main__":
    asyncio.run(main())
