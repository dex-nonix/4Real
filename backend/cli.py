import click
from app import create_app, db


@click.group()
def cli():
    """Simple backend CLI."""


@cli.command('init-db')
def init_db():
    """Create all tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        click.echo('Database initialized')


@cli.command('run')
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000, type=int)
@click.option('--debug/--no-debug', default=True)
def run(host: str, port: int, debug: bool):
    """Run the development server."""
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    cli()

