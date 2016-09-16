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
import os
import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BlogHandler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

class Main_Handler(BlogHandler):
    def render_front(self, subject="", content="", error=""):
        posts =db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render('front.html' , subject= subject , content= content , error= error , posts= posts)

    def get(self):
        self.render_front()


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now = True)


class Add_Post(Main_Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(subject = subject , content = content)
            p.put()
            self.redirect("/blog")
        else:

            error = "We need both a subject and content"
            self.render_front(subject , content , error)


# class Newpost(BlogHandler):
#     def get(self):
#         self.render("newpost.html")

    # def post(self):
    #     subject = self.request.get('subject')
    #     content = self.request.get('content')


class ViewPostHandler(Main_Handler):
    def get(self, post_id):
        add_num = int(post_id)
        added_num = Post.get_by_id(add_num)

        if added_num:
            self.render("post.html", added_num = added_num)

        else:
            self.response.out.write("Error!")
            return








app = webapp2.WSGIApplication([
    ('/blog', Main_Handler),
    ('/newpost', Add_Post),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
    ], debug=True)
