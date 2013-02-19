#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

## Added:
import jinja2 
import os

from google.appengine.ext import ndb
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=
        jinja2.FileSystemLoader(os.path.dirname(__file__)))

#########   DATA STORE   ##########

class User(ndb.Model):
    account = ndb.UserProperty(required = True)

class BlogPost(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    owner = ndb.UserProperty(required=True)
    isPublic = ndb.StringProperty(required=True)

    def getMonthName(self):
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December']
        return months[self.date.month]

    def getFormattedTime(self):
        m = 'am' if (self.date.hour < 12) else 'pm'
        return str(self.date.hour % 12) + ':' + str(self.date.minute).zfill(2) + m

###################################


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('index.html')
        self.response.write(template.render(template_values))

class ExampleHandler(webapp2.RequestHandler):
    def get(self):
        currentUser = users.get_current_user()

        bpQuery = BlogPost.query()
        bpQuery = bpQuery.filter(ndb.OR(BlogPost.owner == currentUser, BlogPost.isPublic=="true"))
        bp = bpQuery.fetch()

        template_values = { 'blogPosts' : bp}
        template = jinja_environment.get_template('example.html')
        self.response.write(template.render(template_values))

    def post(self):
        currentUser = users.get_current_user()
        t = self.request.get('title')
        c = self.request.get('content')
        p = self.request.get('isPublic')

        foo = BlogPost(title=t, content=c, owner=currentUser, isPublic=p)
        foo.put()        

        self.redirect('example')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/example', ExampleHandler)
], debug=True)
