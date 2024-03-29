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

import re
import flask
from flask import render_template
from flask.views import MethodView

from magic.decorators import view
from magic.models.url import Url

@view.view_details(url='/api/shorten/<path:url>')
class ShortenApiView(MethodView):
    """
    Basic index view for the site
    """

    def get(self, url):
        """
        Performs the request shorten action from the GET url parameter
        """

        valid = self.validate_url(url)
        if not valid:
            return flask.Response()

        model = Url(url)
        model.save()

        return flask.Response(model.code)

    def validate_url(self, url):
        """
        Validates the url. If its not valid returns False
        """

        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url)

@view.view_details(url='/<path:code>')
class ResolveView(MethodView):
    """
    Basic index view for the site
    """

    def get(self, code):
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