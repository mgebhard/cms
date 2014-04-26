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

class Art(ndb.Model):
    src = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    artist = ndb.StringProperty(required=True)
    exhibit_name = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(required=False)
    desc = ndb.TextProperty(required=False)

class Annotations(ndb.Model):
    art_id = ndb.KeyProperty(Account)
    annotator = ndb.UserProperty(required=True)
    text = ndb.StringProperty(required=True)
    date_posted = ndb.DateTimeProperty(required=True)
    anonymous = ndb.BooleanProperty(required=True)
    likes = ndb.IntegerProperty(required=False)
    x_cord = ndb.FloatProperty(required=True)
    y_cord = ndb.FloatProperty(required=True)


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

        # If user exsists fetch their annotations
        usr_annotations = []
        annotations = Annotations.query(annotator==userData.key).fetch()
        # annotations = Annotations.query().filter(Annotations.annotator==userData.key)
        if annotations:
            for note in annotations:
                usr_annotations.append(note)

        self.response.out.write(RenderTemplate('home.html', {'annotationList': usr_annotations}))


class ArtHandler(webapp2.RequestHandler):
    def get_dates(self):
        blogs = Blog.query()
        for blog in blogs:
            every_date[blog.date.month].append(blog.date)
        for months in every_date.values():
            months.sort()
        return every_date

    def get(self, art_id):
        blog = Art.query().filter(
            annotations = Annotations.query(annotator==userData.key).date==blog_date).get()
        if blog:
            template_values = {'blog': blog,
                               'private': blog.private,
                               'every_date': self.get_dates()}
            template = 'blog.html' 
        else: 
            self.error(404)
            template_values = {}
            template = 'blog_error.html'

        self.response.out.write(RenderTemplate(template, template_values))
    
    def post(self, art_id):
        date = datetime.strptime(date, '%m.%d.%Y')
        blog = Blog.query().filter(Blog.date==date).get()
        if self.request.get('pwd') == 'cseMIT17':
            private = False
        else: 
            private = True
        template_values = {'blog': blog, 'private': private, 'every_date': self.get_dates()}
        self.response.out.write(RenderTemplate('blog.html', template_values))


routes = [
    ('/', HomeHandler),
    ('/mfa/(.*)', ArtHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)
