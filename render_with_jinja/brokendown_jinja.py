import time
import io
from jinja2 import Undefined, environment, FunctionLoader
from jinja2.utils import missing, object_type_repr
import os
import json
import sqlite3
database_cursor = None


class Environment(environment.Environment):
    def _generate(self, source, name, filename, defer_init=False):
        # With a normal template with FileSystemLoader, the name is the name of the file. If it is BytesIO,
        # it's from the test case body, and will be named as such.
        # TODO: get the name from varmap.mapped.id somehow?
        if type(name) == io.BytesIO:
            name = 'Embedded Test Case Template'
        return super(Environment, self)._generate(source, name, filename, defer_init=defer_init)


class KeepUndefined(Undefined):
    # Jinja renders undefined variables to empty string by default. This overrides that behavior to have it
    # return the original {{ variable }} so it can be replaced by ninja, as with assigned variables through the
    # test run.
    def __str__(self):
        if self._undefined_hint is None:
            if self._undefined_obj is missing:
                return u'{{ %s }}' % self._undefined_name
            # here -- what to do here.. nested dictionary with a value that isn't originally in the varmap/testData.
            # TODO: be cleverer...
            return u'{{ %s[%r] }}' % (object_type_repr(self._undefined_obj), self._undefined_name)
        return u'{{ undefined value printed: %s }}' % self._undefined_hint


def render_string_with_jinja(string_value, jinja_env, jinja_map):
    print(type(string_value), string_value)
    if isinstance(string_value, str):
        bytes_template = io.BytesIO()
        bytes_template.write(string_value.encode('utf-8'))
        bytes_template.seek(0)
    else:
        print('bytes templ', string_value)
        bytes_template = string_value
    template = jinja_env.get_template(bytes_template)
    rendered_string = template.render(jinja_map)
    print('rendered string is: {}'.format(rendered_string))
    return rendered_string


def db_connect(db_url='G:\\ext\\code\\jinja_play\\flask_version\\render_with_jinja\\render.db'):
    print(db_url)
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    return cursor


def db_loader(template):
    mtime = time.time()
    if isinstance(template, io.BytesIO):
        template_str = template.getvalue().decode()
        contents = template_str
        print('decded string value', template.getvalue().decode())
        filename = 'Embedded Test Case Template'  # could be a temp file name, None seemed apt enough. maybe the uid of test case?
        return contents, filename, mtime
    try:
        cursor = db_connect()
        cursor.execute("select filename, contents from templates where filename='{0}'".format(template))
        result = cursor.fetchone()
        cursor.close()
        print('using_db on result : {0}'.format(result[1]))
        return str(result[1]), str(result[0]), mtime
    except Exception:
        raise


def main():
    env = Environment(loader=FunctionLoader(db_loader),
                      undefined=KeepUndefined,
                      block_start_string='{~',
                      block_end_string='~}',
                      comment_start_string='{!',
                      comment_end_string='!}')
    string = render_string_with_jinja("{~ include 'astro_post_y2k.json' ~}", env, {})

if __name__ == '__main__':
    main()
