import os 
import tornado.web

class BgHandler(tornado.web.RequestHandler):
    def get(self):
		directory = '/var/www/tornado-master/demos/facebook/static/bg'
		files = os.listdir(directory)
		bgobj = []
		for i in files:
			bgobj.append(i)

		self.render("getbg.html", bg=bgobj)