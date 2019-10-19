"""
MIT License

Copyright (c) 2019 Jordan Maxwell
Written 10/19/2019

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

import logging

# Load modules
from magic.util import modules
modules = modules.find_scripts_in_module(__file__)
logging.debug('Loading models modules: %s' % str(modules))
for module in modules:
    logging.debug('Loading module: %s' % module)
    __import__('magic.models.%s' % module, locals(), globals())

from magic.decorators import model
from flask import current_app, g

def create_tables(**kwargs):
    """
    Creates all the available tables
    """

    model_book = model.model_book
    models = model_book.models
    for model_info in models:
        model_cls = model_info.model_cls
        logging.info('Creating model: %s' % model_cls.__name__)
        if not model_cls.exists():
            model_cls.create_table(wait=True)

@current_app.before_first_request
def before_first_request(*args, **kwargs):
    """
    Called before the first flask request. Automatically creates the dynamodb 
    tables if required
    """

    config = current_app.config
    if config.get('DYNAMO_CREATE_TABLES', False):
        logging.info('Creating dynamo tables on first request.')
        create_tables()

def load_models():
    """
    Loads all available models
    """

    logging.info('Loading models')