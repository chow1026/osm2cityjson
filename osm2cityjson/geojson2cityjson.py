import click

@cli.command('export')
@click.argument('input_filename')
@click.argument('output_filename')
def convert(input_filename, output_filename):
    """Export the CityJSON to another format.
    """
    pass