from sqlalchemy import create_engine
from app import config

from app.server.utils.models import BaseModel


def drop_and_rebuild_sql(base, uri):
    engine = create_engine(uri)
    print(f'Dropping for uri: {uri}')
    base.metadata.drop_all(engine)
    print(f'Creating for uri: {uri}')
    base.metadata.create_all(engine)


def clear_all():
    if config.DEPLOYMENT_ENVIRONMENT == 'development':
        drop_and_rebuild_sql(BaseModel, config.SQLALCHEMY_DATABASE_URI)

    else:
        raise Warning('You are about to drop the production database, we do not advise that you do that.')


if __name__ == '__main__':
    clear_all()
