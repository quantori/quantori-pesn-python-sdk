import os

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape, TemplateNotFound

package_env = Environment(loader=PackageLoader('signals_notebook'), autoescape=select_autoescape())


class TemplateLocationWrapper:
    """Wrapper to get template location

    """
    def get_template(self, template_name: str):
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
            return package_env.get_template(file_name)


env = TemplateLocationWrapper()
