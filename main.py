import webapp2
import jinja2
import urllib2
import os
from google.appengine.ext import ndb
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

def RenderTemplate(template_name, values):
    template = jinja_environment.get_template(template_name)
    return template.render(values)

def getUser(usr):
    return Account.query().filter(Account.user==usr).get()

class Account(ndb.Model):
    user = ndb.UserProperty(required=True)
    
class ArtEvent(ndb.Model):
    src = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    artist = ndb.StringProperty(required=True)
    date = ndb.StringProperty(required=True)

    #Not sure what annotorious returns
    annotator = ndb.KeyProperty(Account)

class HomeHandler(webapp2.RequestHandler):
    def get(self):
        # check to see if the user is a new user
        current_user = users.get_current_user()
        userData = getUser(current_user)

        # Create new user if not found in the db
        if not userData:
            userData = Account(user=current_user)
            userData.put()
            self.response.out.write(RenderTemplate('home.html', {}))

        # Fetch their annotations
        usr_annotations = []
        new_photos = ImageEvent.query().filter(ImageEvent.receiver==userData.key)
        if new_photos:
            for photo_instance in new_photos:
                photo_objects.append(photo_instance)

        self.response.out.write(RenderTemplate('home.html', {'annotationList': usr_annotations}))


routes = [
    ('/', HomeHandler),
    ('/mfa/*', SendHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)
