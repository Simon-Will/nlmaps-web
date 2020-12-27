import click
from flask import current_app as app

from tutron.app import db
from tutron.models import User


def user():
    """List, add and remove users"""
    pass


def show_all():
    """List all users"""
    users = db.session.query(User).all()
    if users:
        for db_user in users:
            print(f"{db_user}")
    else:
        print("No users could be found.")


@click.argument('username')
def set_new_password(username):
    """
    Set a new password for the given user. A password prompt will be shown
    with a password suggestion for convenience.
    """
    dbuser = db.session.query(User).filter_by(name=username).one_or_none()
    if dbuser:
        password_suggestion = random_string_with_digits(8)
        password = input(f"Password [{password_suggestion}]: ")
        if not password:
            password = password_suggestion
        dbuser.set_password(password)
        db.session.commit()
        print(f"Updated password for user {str(dbuser)}.")
    else:
        print(f"No user {str(username)} found.", file=sys.stderr)


@click.argument('username')
def add(username):
    """Add user interactively"""
    user = db.session.query(User).filter_by(name=username).one_or_none()
    if user:
        print(f"User {str(username)} already exists.", file=sys.stderr)
    else:
        email = input("Email []: ")
        first_name = input("First Name []: ")
        last_name = input("Last Name []: ")
        password_suggestion = random_string_with_digits(8)
        password = input(f"Password [{password_suggestion}]: ")
        if not password:
            password = password_suggestion

        user = User(
            name=username,
            admin=False,
            active=True,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        print(f"Created {str(user)}.")


@click.argument('username')
def rm(username):
    """
    Remove the given user from the database.
    """
    user = db.session.query(User).filter(
        User.name == username).one_or_none()
    if user:
        db.session.delete(user)
        db.session.commit()
        print('User {user} deleted.'.format(user=username))
    else:
        print('User {user} is not existing.'.format(user=username))


spec = {
    'group': user,
    'commands': [show_all, add, rm, set_new_password]
}
