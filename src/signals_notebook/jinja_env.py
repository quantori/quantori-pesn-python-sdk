from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape, TemplateNotFound

file_system_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
package_env = Environment(loader=PackageLoader('signals_notebook'), autoescape=select_autoescape())


class TemplateLocationMiddleware:

    def __call__(self, template_name):
        try:
            return package_env.get_template(template_name)
        except TemplateNotFound:
            return file_system_env.get_template(template_name)


env = TemplateLocationMiddleware()
