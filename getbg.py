import os 
import tornado.web

class BgHandler(tornado.web.RequestHandler):
    def get(self):
		directory = os.path.join(os.path.dirname(__file__), "static/bg")
		files = os.listdir(directory)
		bgobj = []
		for i in files:
			bgobj.append(i)

		self.render("getbg.html", bg=bgobj)