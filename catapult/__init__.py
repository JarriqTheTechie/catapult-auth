import inspect
from .Exceptions import *
import re
from typing import TYPE_CHECKING
from jinja2.ext import Extension
from bs4 import BeautifulSoup


if TYPE_CHECKING:
    from typing import Optional
    from jinja2 import Environment


try:
    from flask import render_template_string, render_template
except ModuleNotFoundError:
    # raise FlaskNotInstalledError
    from masonite.views import View


def render_inline(jinja, **kwargs):
    from markupsafe import Markup
    from jinja2 import Environment
    env = Environment()
    env.add_extension('catapult.catapult_ext.CatapultExt')
    kwargs = {**kwargs, **_render(), **_render_with_collection()}
    tmpl = env.from_string(f'{jinja}')
    output = Markup(tmpl.render(**kwargs))
    if output.startswith("{") and output.endswith("}"):
        tmp = Markup(f"{output}".lstrip("{").rstrip("}"))
        return env.from_string(f'{{{jinja}}}').render(**kwargs)
    return Markup(output)


def annotate_checker():
    try:
        from __init__ import CATAPULT_ANNOTATE
    except:
        CATAPULT_ANNOTATE = False
    return CATAPULT_ANNOTATE


def to_class(path: str):
    try:
        from pydoc import locate
        class_instance = locate(path)
    except ImportError:
        print('Module does not exist')
    return class_instance or None


def render_if(component):
    try:
        render_if = component.render_if
    except AttributeError:
        render_if = lambda: None
    return render_if


def _render():
    def render(component, **kwargs):
        component_py_path = f"templates.components.{component}.{component}"
        component_class = to_class(component_py_path)(**kwargs)

        #try:
        #    component_class = to_class(component_py_path)(**kwargs)
        #except TypeError:
        #    raise ComponentNotFoundError(component)
        if render_if(component_class)() is True or render_if(component_class)() is None:
            arguments_from_component = component_class.__dict__
            template_path = f'components/{component}.html'
            try:
                template = render_template(template_path, **arguments_from_component)
            except NameError:
                from masonite.facades import View
                from masonite.helpers import compact
                template = View.render(template_path, arguments_from_component).get_content()

            if annotate_checker() is True:
                comment_start = f"<!-- BEGIN {template_path} --> \n"
                comment_end = f"\n <!-- END {template_path} --> "
                return render_inline(comment_start + template + comment_end)
            else:
                return render_inline(template)
        else:
            return ""

    return dict(render=render)


def _render_with_collection():
    def render_with_collection(component, collection, **kwargs):
        component_py_path = f"templates.components.{component}.{component}"
        component_class = to_class(component_py_path)(**kwargs)
        #try:
        #    component_class = to_class(component_py_path)(**kwargs)
        #except TypeError:
        #    raise ComponentNotFoundError(component)
        # component_class.with_collection_parameter = collection
        arguments_from_component = component_class.__dict__
        results = ""
        try:
            for n in range(len(component_class.__dict__[f"{collection}"])):
                if f"{collection}_counter" in component_class.__dict__:
                    component_class.__dict__[f"{collection}_counter"] = n + 1
                template_path = f'components/{component}.html'
                arguments = {**component_class.__dict__, **{f"{collection}": arguments_from_component[collection][n]}}
                scoped_class = component_class
                scoped_class.__dict__ = arguments
                if render_if(component_class)() is True or render_if(component_class)() is None:
                    try:
                        template = render_template(template_path, **arguments)
                    except NameError:
                        from masonite.facades import View
                        from masonite.helpers import compact
                        template = View.render(template_path, arguments).get_content()
                    if annotate_checker() is True:
                        comment_start = f"<!-- BEGIN {template_path} --> \n"
                        comment_end = f"\n <!-- END {template_path} --> "
                        #print(template)

                        results += f"{comment_start} {template} {comment_end}"
                    else:
                        results += template
                else:
                    results += ""
            return render_inline(results)
        except TypeError:
            return render_inline(results)

    return dict(render_with_collection=render_with_collection)


def Catapult(app):
    try:
        app.context_processor(_render)
        app.context_processor(_render_with_collection)
    except:
        pass
