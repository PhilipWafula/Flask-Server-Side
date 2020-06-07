from app import config
from app.server import db
from app.server import create_app


def drop_and_rebuild_sql():
    app = create_app()
    context = app.app_context()
    context.push()

    # define working database
    working_database = config.DATABASE_NAME

    # drop working database
    print(f"Dropping database: {working_database}")
    db.drop_all()

    # recreate working database
    print(f"Creating database: {working_database}")
    db.create_all()

    context.pop()


def clear_all():
    if config.DEPLOYMENT_ENVIRONMENT == "development":
        drop_and_rebuild_sql()

    else:
        raise Warning(
            "You are about to drop the production database, we do not advise that you do that."
        )


if __name__ == "__main__":
    clear_all()
