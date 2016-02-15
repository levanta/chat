import tornado.web
import logging
import uuid
import datetime

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def get_current_user(self):
        user_json = self.get_secure_cookie("fbdemo_user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    def on_message(self, message): 
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        user = self.get_current_user()
        time = datetime.datetime.now().strftime('%H:%M')
        user_id = user['id']
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            "avatar": user["picture"]["data"]["url"],
            "name": user["name"],
            "time" : time,
            "user_id" : user_id
            }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))

        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)