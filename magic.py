"""
MIT License

Copyright (c) 2019 Jordan Maxwell
Written 10/15/2019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function

import sys
import os
import flask
import logging
import argparse

from hashlib import md5
from base64 import b64encode

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute

# Environmental inputs
DEBUG_MODE = os.environ.get('DEBUG-MODE', 'false') == 'true'
TABLE_NAME = os.environ.get('DYNAMO-TABLE', 'magic-urls')

# Flask app
app = flask.Flask(__name__)
app.config.update(DEBUG=DEBUG_MODE)

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

class Url(Model):
    """
    Primary DynamoDB Model for url storage
    """

    class Meta:
        table_name = TABLE_NAME

    class CodeIndex(GlobalSecondaryIndex):
        class Meta:
            read_capacity_units = 1
            write_capacity_units = 1
            projection = AllProjection()
        code = UnicodeAttribute(hash_key=True)

    url = UnicodeAttribute(hash_key=True)
    code = UnicodeAttribute()
    code_index = CodeIndex()

    def save(self, **kwargs):
        """
        Generates the shortened code before saving
        """

        self.code = b64encode(
            md5(self.url.encode('utf-8')).hexdigest()[-4:].encode('utf-8')
        ).decode('utf-8').replace('=', '').replace('/', '_')
        super(Url, self).save(**kwargs)

@app.route('/')
def index():
    """
    Provides the application index page
    """

    return flask.render_template("index.html")

@app.route('/shorten/<path:url>')
def shorten(url):
    """
    Performs the request shorten action
    """

    model = Url(url)
    model.save()

    return flask.Response(model.code)

@app.route('/<path:code>')
def resolve(code):
    """
    Resolves the shorten url request
    """

    abort = False
    try:
        model = Url.code_index.query(code).next()
    except AttributeError:
        model = Url.code_index.query(code).__next__()
    except StopIteration:
        flask.abort(404)
        abort = True
    except Exception:
        flask.abort(500)
        abort = True
    
    if not abort:
        return flask.redirect(model.url)

def init(self):
    """
    Called when the --init flag is passed in the command line
    """

    # Create the table if it does not exist
    if not Url.exists():
        logger.info("Creating dynamodb table %s..." % TABLE_NAME)
        Url.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)
    else:
        logger.info('Table %s already exists.' % TABLE_NAME)

    logger.info('Initialization complete')

def main():
    """
    Main entry point for the command line application
    """

    parser = argparse.ArgumentParser(description='MagicUrl serverless url shortener')
    parser.add_argument('-i', '--init', type=bool, help='Initializes the AWS services')
    args = parser.parse_args()

    if args.init:
        init()

    # Run the flask app
    app.run()

    return 0

if __name__ == "__main__":
    sys.exit(main())