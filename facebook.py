#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket

from tornado.options import define, options
from chatsockethandler import ChatSocketHandler

define("port", default=8888, help="run on the given port", type=int)
define("facebook_api_key", "549740061875624", type=str)
define("facebook_secret", 'fe59f5b8b538d9176bf54b989e58874b', type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler2),
            (r"/test", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
            ui_modules={"Post": PostModule, "Post2": PostModule2, "Post3": PostModule3},
            debug=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)




class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("fbdemo_user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)


class MainHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        self.render("stream2.html", messages=ChatSocketHandler.cache)

class MainHandler2(BaseHandler):
    def get(self):
        self.render("stream.html")


class AuthLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/auth/login?next=" +
                  tornado.escape.url_escape(self.get_argument("next", "/")))
        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=self.settings["facebook_api_key"],
                client_secret=self.settings["facebook_secret"],
                code=self.get_argument("code"),
                callback=self._on_auth)
            return
        self.authorize_redirect(redirect_uri=my_url,
                                client_id=self.settings["facebook_api_key"],
                                extra_params={"scope": "email"})

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")
        self.set_secure_cookie("fbdemo_user", tornado.escape.json_encode(user))
        self.redirect(self.get_argument("next", "/"))


class AuthLogoutHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    def get(self):
        self.clear_cookie("fbdemo_user")
        self.redirect(self.get_argument("next", "/"))


class PostModule(tornado.web.UIModule):
    def render(self, post):
        return self.render_string("modules/post.html", post=post)

class PostModule2(tornado.web.UIModule):
    def render(self):
        return self.render_string("modules/post2.html")

class PostModule3(tornado.web.UIModule):
    def render(self):
        return self.render_string("modules/post3.html")

def main():
    tornado.options.parse_command_line()
    if not (options.facebook_api_key and options.facebook_secret):
        print("--facebook_api_key and --facebook_secret must be set")
        return
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    app = Application()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()