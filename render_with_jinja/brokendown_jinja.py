"""Until pynet is packaged and I can use it, this is where the pieces of pynet that I need for this tool will be stored."""


import io
import os
import sys
import json
import time
import sqlite3
import xml.etree.ElementTree as etree
from jinja2 import Undefined, environment, FunctionLoader
from jinja2.utils import missing, object_type_repr

database_cursor = None


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


# figure out how to default this stupid db
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

############ BEGIN THE SAD COPY-PASTE. PACKAGE PYNET THEN GET RID OF THIS ############

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



def return_exc_printed_nice(string, exc_line_number):
    """ base for the pretty printing of exceptions"""
    string = string.split(os.linesep) if os.linesep in string else string.split('\n')
    string[exc_line_number - 1] = '>>>>>>' + string[exc_line_number - 1].strip()
    string = os.linesep.join(string)
    return string


def pretty_print_xml_tostring(xml_string):
    """ Pretty print helper for XML strings.

    :param xml_string: String representing a well-formed XML document
    :return: Pretty-printed XML string
    """
    root = etree.fromstring(xml_string)
    _indent_xml(root)

    return etree.tostring(root, encoding='utf-8')


def python_to_json(string):
    # This hurts my soul a little bit. depending on where these values are rendered, they may or may not be
    # python or json friendly. pass through the string, make it dump-able by the json module.
    # if anyone has a better idea... I'm around and usually not cranky.
    python_to_json_dict = {'True,': 'true,', 'False,': 'false,', 'None,': 'null,'}
    for from_python, to_json in python_to_json_dict.items():
        string = string.replace(from_python, to_json)
    return string


def check_then_dump_json(strings):
    # TODO: there must be a better way to handle empty values. this is uglier than I want it to be
    safe_values = []
    for possible_danger_string in strings:
        # If item in list of strings is not emtpy, try to make it json-friendly and dump it.
        # If that fails, return failure and string with indicator of where the exception occurred.
        if possible_danger_string:
            possible_danger_string = python_to_json(possible_danger_string)
            try:
                json_dict = json.loads(possible_danger_string, cls=UselessJsonDecoderClass)
            except ValueError as err:
                # override text of value error with something more useful
                err.args = ('Invalid JSON and content type indicates application/json! \n %s'
                            % return_line_no_of_json_value_exc(possible_danger_string),)
                raise
            else:
                safe_json_string = json.dumps(json_dict, indent=4)
                safe_values.append(safe_json_string)
        else:
            safe_values.append(possible_danger_string)
    return safe_values


def return_line_no_of_json_value_exc(string):
    """ returns the string that caused the exception with indicators of where the error is."""
    if sys.version_info < (3, 5):
        last_error_pos = error_pos[0]
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        last_error_pos = exc_obj.lineno
    string = return_exc_printed_nice(string, last_error_pos)
    return 'JSON Error! Look for >>>>>> \nLine: %s\n%s' % (last_error_pos, string)

if sys.version_info < (3, 5):
    original_errmsg = json.decoder.errmsg


def custom_errmsg(msg, doc, pos, end=None):
    global error_pos
    error_pos = json.decoder.linecol(doc, pos)
    return original_errmsg(msg, doc, pos, end)


class UselessJsonDecoderClass(json.JSONDecoder):
    json.decoder.errmsg = custom_errmsg
    if sys.version_info < (3, 5):
        json.decoder.errmsg = custom_errmsg
