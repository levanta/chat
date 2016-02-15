import os 
import tornado.web
import sys

class BgHandler(tornado.web.RequestHandler):
    def get(self):
		directory = sys.path[0]+'/static/bg'
		files = os.listdir(directory)
		bgobj = []
		for i in files:
			bgobj.append(i)

		self.render("getbg.html", bg=bgobj)