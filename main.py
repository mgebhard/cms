import webapp2
import jinja2
import urllib2
import os
import json
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

def RenderTemplate(template_name, values):
    template = jinja_environment.get_template(template_name)
    print template
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
    art_id = ndb.KeyProperty(kind=Art)
    annotator = ndb.UserProperty(required=True)
    text = ndb.StringProperty(required=True)
    date_posted = ndb.DateTimeProperty(required=True)
    anonymous = ndb.BooleanProperty(required=True)
    likes = ndb.IntegerProperty(required=False)
    x_cord = ndb.FloatProperty(required=True)
    y_cord = ndb.FloatProperty(required=True)
    width = ndb.FloatProperty(required=True)
    height = ndb.FloatProperty(required=True)
    center_x = ndb.FloatProperty(required=True)
    center_y = ndb.FloatProperty(required=True)

def dump_data():
     with open("data.json") as json_file:
         json_data = json.load(json_file)['results']['collection1']
     for d in json_data:
         src = d['image']['src']
         link = d['period']['href']
         title = d['title']
         artist = d['artist']
         ex = d['exhibit']
         info = d['desc']
         # text = d['period']['text']
         new_art = Art(src = src,
                         link = link,
                         title = title,
                         artist = artist,
                         exhibit = ex,
                         description = info)
         new_art.put()

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
        annotations = Annotation.query(Annotation.annotator==users.get_current_user()).order(Annotation.date_posted)

        art_keys = []
        if annotations:
            for note in annotations:
                if note.art_id not in art_keys:
                    art_keys.append(note.art_id)
                usr_annotation.append(note)

        self.response.out.write(RenderTemplate('home.html', {'annotationList': usr_annotation,
                                                             'artList': [key.get() for key in art_keys]}))


class ArtHandler(webapp2.RequestHandler):
    def get(self, art_id):
        art_id = int(art_id)
        art = Art.get_by_id(int(art_id))
        annotations = Annotation.query(Annotation.art_id==art.key).order(Annotation.date_posted)
        all_annotations = []
        if annotations:
            for note in annotations:
                all_annotations.append(note)

        template_values = {
                           'art_src': art.src,
                           'title': art.title,
                           'artist': art.artist,
                           'exhibit': art.exhibit,
                           'link': art.link,
                           'description': art.description,
                           'all_annotations': all_annotations,
                           'annotations_json': json.dumps([serializeAnno(x) for x in all_annotations]), #Needed for Javascript function to readd annotations
                           'user': users.get_current_user(),
                           'art_id': art_id
                           }

        self.response.out.write(RenderTemplate('picture.html' , template_values))

    def post(self, art_id):
        art = Art.get_by_id(int(art_id))
        data = json.loads(self.request.get('data'))
        print str(data['shapes'])
        shape_info = data['shapes'][0]['geometry']
        new_annotation = Annotation(art_id = art.key,
                                    annotator = users.get_current_user(),
                                    text = str(data['text']),
                                    date_posted = datetime.now(),
                                    anonymous = bool(data['anonymous']),
                                    likes = 0,
                                    x_cord = float(shape_info['x']),
                                    width = float(shape_info['width']),
                                    y_cord = float(shape_info['y']),
                                    height = float(shape_info['height']),
                                    center_x = float(data['center']['x']),
                                    center_y = float(data['center']['y'])
                                    )
        new_annotation.put()
        # self.redirect('/mfa/%s' % art_id)
        obj = {
            'success': True,
            'time_posted': new_annotation.date_posted.strftime('%m/%d/%Y - %H:%M')
        }
        self.response.set_status(200)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(obj))

def serializeAnno(anno):
    anno = anno.to_dict(exclude=['date_posted'])
    # don't need key property in front -end, just change to id
    # since json can't serialize keyproperties
    anno['art_id'] = anno['art_id'].id()
    anno['annotator'] = anno['annotator'].email()
    return anno

routes = [
    ('/', HomeHandler),
    ('/mfa/(.*)', ArtHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)
