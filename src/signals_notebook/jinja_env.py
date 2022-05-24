from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(loader=PackageLoader('signals_notebook'), autoescape=select_autoescape())
