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

from hashlib import md5
from base64 import b64encode

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute

class Url(Model):
    """
    DynamoDB Model for url storage
    """

    class Meta:
        table_name = 'magic-urls'

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