from google.appengine.ext import vendor
vendor.add('lib')

import datetime, json, pytz, urllib2, webapp2
from google.appengine.api import users

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
    startDate = datetime.date(2013, 2, 14)
    now = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    ndays = (now - startDate).days

    photos = getPhotos(username, albumId, authKey)
    return list(reversed(photos[: ndays + 1]))

class EndingTodayJson(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')

        username = 'brian.sargent.nj'
        albumId = '5661873495373261201'
        authKey = 'Gv1sRgCP729Mbsh7XdNg'

        self.response.write(json.dumps(endingToday(username, albumId, authKey)))

app = webapp2.WSGIApplication([
    ('/endingToday.json', EndingTodayJson)
], debug=True)

