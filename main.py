import webapp2
import jinja2
import urllib2
import os
import json
from datetime import datetime
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

class Art(ndb.Model):
    src = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    artist = ndb.StringProperty(required=True)
    exhibit = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=False)
    link = ndb.StringProperty(required=True)

class Annotation(ndb.Model):
    art_id = ndb.KeyProperty(Account)
    annotator = ndb.UserProperty(required=True)
    text = ndb.StringProperty(required=True)
    date_posted = ndb.DateTimeProperty(required=True)
    anonymous = ndb.BooleanProperty(required=True)
    likes = ndb.IntegerProperty(required=False)
    x_cord = ndb.FloatProperty(required=True)
    y_cord = ndb.FloatProperty(required=True)

# def dump_data():
#     with open("data.json") as json_file:
#         json_data = json.load(json_file)['results']['collection1']
#     for d in json_data:
#         src = d['image']['src']
#         link = d['period']['href']
#         title = d['title']
#         artist = d['artist']
#         ex = d['exhibit']
#         info = d['desc']
#         # text = d['period']['text']
#         new_art = Art(src = src,
#                         link = link,
#                         title = title,
#                         artist = artist,
#                         exhibit = ex,
#                         description = info)
#         new_art.put()

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

        # If user exsists fetch their annotation
        usr_annotation = []
        annotations = Annotation.query(Annotation.annotator==users.get_current_user()).fetch()
        
        # annotations = Annotation.query().filter(Annotation.annotator==users.get_current_user())
        if annotations:
            for note in annotations:
                usr_annotation.append(note)

        self.response.out.write(RenderTemplate('home.html', {'annotationList': usr_annotation}))


class ArtHandler(webapp2.RequestHandler):
    def get(self, art_id):
        art_id = int(art_id)
        art = Art.get_by_id(int(art_id))
        annotations = Annotation.query(art_id==art_id).fetch()
        all_annotations = []
        if annotations:
            for note in annotations:
                all_annotations.append(note)
        
        template_values = {'art_src': art.src,
                           'title': art.title,
                           'artist': art.artist,
                           'exhibit': art.exhibit,
                           'link': art.link,
                           'description': art.description,
                           'all_annotations': all_annotations}

        self.response.out.write(RenderTemplate('picture.html' , template_values))
    
    def post(self, art_id):
        art = Art.get_by_id(int(art_id))
        new_annotation = Annotation(art_id = art, 
                                    annotator = users.get_current_user(), 
                                    text = str(self.request.get('text')),
                                    date_posted = datetime.now(),
                                    anonymous = bool(self.request.get('annoymous')),
                                    likes = 0,
                                    x_cord = float(self.request.get('x')),
                                    y_cord = float(self.request.get('y'))
                                    )
        new_annotation.put()
        self.redirect('/mfa/%s' % art_id)

routes = [
    ('/', HomeHandler),
    ('/mfa/(.*)', ArtHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)
