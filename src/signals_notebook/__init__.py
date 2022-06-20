import logging
import mimetypes
from os.path import dirname, join

mime_types_file = join(dirname(__file__), 'mime.types')

mimetypes.init([mime_types_file])

logging.getLogger(__name__).addHandler(logging.NullHandler())
