import click
from flask.cli import with_appcontext





@click.command(name="cs50")
@with_appcontext
def cs50():
    db.create_all()