from textx import language, metamodel_from_file
from os.path import dirname, join
from textx import generator as file_generator
from .generator import generate


__version__ = "0.1.0.dev"


@language('reporter', '*.rpt')
def reporter_language():
    "reporter language"
    current_dir = dirname(__file__)
    mm = metamodel_from_file(join(current_dir, 'reporter.tx'))

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    return mm


@file_generator('reporter', 'html+pdf')
def reporter_generate_files(metamodel, model, output_path, overwrite, debug): 
    "reporter generator"
    generate()
    