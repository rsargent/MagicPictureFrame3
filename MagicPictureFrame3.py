from google.appengine.ext import vendor
from google.appengine.api import mail
vendor.add('lib')

import datetime, json, pytz, urllib2, webapp2
from google.appengine.api import users

startDate = datetime.date(2016, 8, 9)
username = 'brian.sargent.nj'
albumId = '6166497731584716881'
authKey = 'Gv1sRgCIeFvff2vZ3hRw'

#albumId = '5661873495373261201'
#authKey = 'Gv1sRgCP729Mbsh7XdNg'

def getPhotos(username, albumid, authkey):
    startIndex = 1

    photos = []

    while True:
        url = (
            ('https://picasaweb.google.com/data/feed/api/user/%s/albumid/%s' +
             '?kind=photo&authkey=%s&alt=json&sort=published&imgmax=1600&start-index=%d') % 
               (username, albumid, authkey, startIndex))

        response = json.loads(urllib2.urlopen(url).read())

        feed = response['feed']
        totalResults = feed['openSearch$totalResults']['$t']
        entries = feed['entry']
        print 'Fetched %d entries starting at %d' % (len(entries), startIndex)

        for entry in entries:
            photos.append(entry['media$group']['media$content'][0]['url'])
    
        if startIndex + len(entries) - 1 >= totalResults:
            break
    
        if len(entries) == 0:
            break
        
        startIndex += len(entries)

    return photos


def endingToday(username, albumId, authKey):
    now = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    ndays = (now - startDate).days

    photos = getPhotos(username, albumId, authKey)
    number_of_days_left = len(photos) - (ndays + 1)
    if number_of_days_left <= 10:
        mail.send_mail(sender='Randy Sargent <randy.sargent@gmail.com>',
                   to='Randy Sargent <randy.sargent@gmail.com>, Brian Sargent <brian.sargent.nj@gmail.com>',
                   subject="Magic Picture Frame down to %d pictures" % number_of_days_left,
                   body="""Dear Brian and Randy,

Someone just visited the Magic Picture Frame and I noticed you only have %d pictures left...

Love,
The Magic Picture Frame Server
""" % number_of_days_left )

    return list(reversed(photos[: ndays + 1]))

def startingToday(username, albumId, authKey):
    now = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    ndays = (now - startDate).days

    photos = getPhotos(username, albumId, authKey)
    return list(photos[ndays :])

class EndingTodayJson(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')


        self.response.write(json.dumps(endingToday(username, albumId, authKey)))

class Peek(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        self.response.write('<html><head></head><body>Peek:<br>\n')
        day = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        for photo in startingToday(username, albumId, authKey):
            self.response.write('%s: <img width=100 src="%s"><br>' % (day, photo))
            day += datetime.timedelta(days=1)
        self.response.write('</body></html>\n')

app = webapp2.WSGIApplication([
    ('/endingToday.json', EndingTodayJson),
    ('/peek', Peek)
], debug=True)

