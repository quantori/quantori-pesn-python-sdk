import logging
import os

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape, Template, TemplateNotFound

package_env = Environment(loader=PackageLoader('signals_notebook'), autoescape=select_autoescape())

log = logging.getLogger(__name__)


class TemplateLocationWrapper:
    """Wrapper to get template location"""

    def get_template(self, template_name: str) -> Template:
        """Get template

        Args:
            template_name: Full path to the template

        Returns:

        """
        dir_path, file_name = os.path.split(template_name)
        try:
            file_system_env = Environment(loader=FileSystemLoader(os.path.abspath(dir_path)))
            return file_system_env.get_template(file_name)
        except TemplateNotFound:
            log.info('There is no template in the system. Searching in package location...')

        try:
            return package_env.get_template(file_name)
        except TemplateNotFound:
            log.info('There is no template in the package.')
            raise


env = TemplateLocationWrapper()
