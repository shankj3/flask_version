import os, sys
import sqlite3
import json
from flask import Flask, request, session, g, redirect, render_template, flash, url_for
from werkzeug import secure_filename
from collections import ChainMap
from jinja2 import FunctionLoader, TemplateSyntaxError, UndefinedError
import xml.etree.ElementTree as etree

import brokendown_jinja as jinj
import gibson
import jsondiff


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'render.db'),
    SECRET_KEY='dev key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list-templates', methods=['GET'])
def show_entries():
    db = get_db()
    cur = db.execute('select filename, contents from templates order by id desc')
    entries = cur.fetchall()
    render_dict = {"templates": entries}
    db.close()
    return render_template('list_templates.html', entries=render_dict)


@app.route('/list-templates/<template_name>', methods=['GET', 'POST'])
def show_template(template_name):
    db = get_db()
    cur = db.execute('select filename, contents from templates order by id desc')
    entries = cur.fetchall()
    render_dict = {"templates": entries}
    if request.method == 'GET':
        cur = db.execute("select filename, contents from templates where filename = '{0}'".format(template_name))
        file_contents = cur.fetchone()['contents']
        render_dict["template_contents"] = file_contents
    elif request.method == 'POST':
        updated_template = request.form.get('output')
        print(type(updated_template))
        db.execute("""update templates set contents = ? where filename = ?""",
            (updated_template, template_name))
        db.commit()
        flash('Template successfully updated.')
        render_dict['template_contents'] = updated_template
    db.close()
    return render_template('list_templates.html', entries=render_dict)


@app.route('/upload', methods=['GET', 'POST'])
def add_entry():
    error = None
    print(request.files)
    if request.method == 'GET':
        return render_template('input.html')
    elif request.method == 'POST':
        file = request.files['file']
        if file and secure_filename(file.filename):
            filename = secure_filename(file.filename)
            db = get_db()
            if not is_in_db(filename, db):
                a = file.stream.read().decode()
                db.execute('insert into templates (filename, contents) values (?, ?)',
                           [secure_filename(filename), a])
                db.commit()
                db.close()
                print(type(a))
                print(a)
                flash('New template {0} was successfully added'.format(filename))
            else:
                flash('Name of file uploaded matches one in database. File not loaded.')
        else:
            flash('Not loaded, filename error')
    return render_template('input.html')


@app.route('/render', methods=['GET', 'POST'])
def render_a_template():
    print(request)
    if request.method == 'POST':
        env = jinj.Environment(loader=FunctionLoader(jinj.db_loader),
                               undefined=jinj.KeepUndefined,
                               block_start_string='{~',
                               block_end_string='~}',
                               comment_start_string='{!',
                               comment_end_string='!}')
        form = {
        "string_to_render": request.form.get('string_to_render'),
        "test_map": request.form.get('map'),
        "output": request.form.get('output'),
        "compare": request.form.get('compare')
        }
        print(form)
        try:
            if form.get('test_map'):
                jinja_map = json.loads(form.get('test_map'))
                pretty_dumped = json.dumps(jinja_map, indent=4)
            else:
                jinja_map = {}
                pretty_dumped = ''
        except ValueError:
            flash('Map to render had a JSON exception! See below')
            pretty_dumped = 'Invalid JSON! \n %s' \
                            % jinj.return_line_no_of_json_value_exc(request.form.get('map'))
            form['test_map'] = pretty_dumped
        else:
            print('FORM',[(k, v) for k,v in request.form.items()])
            if 'render' in request.form:
                print("RENDERRRRR")
                try:
                    generated = jinj.render_string_with_jinja(request.form.get('string_to_render'), env, jinja_map)

                except Exception as e:
                    # return string based on what type of exception it is.
                    flash(return_template_exc(e))

                else:
                    try:
                        validated_generated = validate(request.form.get('choices'), generated)
                    except Exception as exc:
                        # broad for a reason
                        flash('Incorrect {0} rendered!!'.format(request.form.get('choices')))

                        if isinstance(exc, ValueError):
                            validated_generated = jinj.return_line_no_of_json_value_exc(generated)
                        elif isinstance(exc, etree.ParseError):
                            line_no, _ = exc.position
                            validated_generated = jinj.return_exc_printed_nice(generated, line_no)
                        else:
                            flash('Unexpected error! {0}'.format(exc.args))
                            validated_generated = generated

                    form['test_map'] = pretty_dumped
                    form['output'] = validated_generated
            elif 'check' in request.form:
                output_string = request.form.get('output')
                msg = {"output_string": output_string}
                session['messages'] = msg
                return redirect(url_for('compare'))
    else:
        return render_template('name.html')
    return render_template('name.html', entries=form)


@app.route('/compare',  methods=['GET', 'POST'])
def compare():
    choice = request.form.get('choices')
    form = {
        "output": request.form.get('output'),
        "compare": request.form.get('compare')
        }
    # you can only get here from a redirect, which will create the session message. so it's fine to explicitly
    # call output_string
    if request.method == 'GET':
        flash('Add a compare with string and PYNET will compare the rendered string to what you think it should be.')
        output_string = session['messages']['output_string']
        form['output'] = output_string
        form['compare'] = ''

    elif request.method == 'POST':
        if choice == 'other':
            flash('Must have either JSON or XML as form type')
            return render_template('compare.html', entries=form)
        try:
            if choice == 'JSON':
                compare_xml = jsondiff.json_to_xml(form['compare'])
                output_xml = jsondiff.json_to_xml(form['output'])
            elif choice == 'XML':
                compare_xml = etree.fromstring(form['compare'])
                output_xml = etree.fromstring(form['output'])
        except (ValueError, etree.ParseError) as e:
            flash('Exception in loading strings in {0} format! Exception: {1}'.format(choice, e.args))
        else:
            _, compare_xml_objects, output_xml_objects = gibson.diff_xml(compare_xml, output_xml, False)
            if not compare_xml_objects and not output_xml_objects:
                flash('They match! Good job!')
            else:
                flash('There are differences! Check Below')
                diffs = gibson.pretty_print_differences(compare_xml_objects, output_xml_objects)
                form['failures'] = [diff for diff in diffs]
    return render_template('compare.html', entries=form)


def validate(string_type, string_value):
    if string_type == 'JSON':
        json_safe = jinj.python_to_json(string_value)
        safe_value = jinj.check_then_dump_json([string_value])[0]
    elif string_type == 'XML':
        safe_value = jinj.pretty_print_xml_tostring(string_value).decode()

    else:
        safe_value = string_value
    return safe_value


def is_in_db(filename, db):
    cur = db.execute("select filename from templates where filename='{0}'".format(filename))
    results = cur.fetchall()
    if len(results) == 0:
        return False
    return True


def return_template_exc(exception):
    if isinstance(exception, TypeError):
        return 'Your template could not be found in the database!'
    elif isinstance(e, TemplateSyntaxError) or isinstance(e, UndefinedError):
        return 'Jinja is not happy! There was an error in your template! \nDescription: %s' % e.args
    else:
        return 'Unexpected error! {0}'.format(e.args)


# Notes
# http://flask.pocoo.org/docs/0.11/patterns/wtforms/
# http://flask.pocoo.org/docs/0.11/tutorial/templates/#tutorial-templates
# http://www.jakowicz.com/flask-apache-wsgi/

if __name__ == "__main__":
    app.run()