from app.server import create_app, db
from app.server.constants import SUPPORTED_ROLES
from app.server.models.role import Role


def system_seed():
    app = create_app()
    app_context = app.app_context()
    app_context.push()

    # seed role data
    for role in SUPPORTED_ROLES:
        # create role
        user_role = Role(name=role)
        db.session.add(user_role)

    db.session.commit()
    app_context.pop()


if __name__ == '__main__':
    system_seed()
