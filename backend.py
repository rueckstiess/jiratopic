import tornado.ioloop
import tornado.web
import pymongo
import numpy as n
import json

from datetime import datetime, timedelta


def group_by_weeks(coll, start_date, end_date, normalize=True):
    # compute first Monday >= start_date
    if start_date.weekday() > 0:
        start_date += timedelta(days=(7 - start_date.weekday()))

    # compute last Sunday <= end_date
    if end_date.weekday() < 6:
        end_date -= timedelta(days=(end_date.weekday() + 1))

    i = start_date

    while i < end_date:
        j = i + timedelta(days=6)
        query = {'fields.created': {'$gte': i, '$lte': j}, 'topic_scores': {'$exists': True}}

        try:
            mat = n.matrix([d['topic_scores'] for d in coll.find(query, ['topic_scores'])])
            rowsum = mat.sum(axis=1)
            #norm = mat / rowsum.reshape(rowsum.shape[0], 1) / mat.shape[0]
            norm = mat / rowsum.reshape(rowsum.shape[0], 1)

            if normalize:
                norm /= mat.shape[0]

            yield {
                'start_date': i.isoformat(),
                'end_date': j.isoformat(),
                'topics': norm.sum(axis=0).tolist()[0],
                'num_issues': mat.shape[0]
            }
        except:
            pass

        i += timedelta(days=7)


class TopicsScoresHandler(tornado.web.RequestHandler):
    def initialize(self, connection, database, collection):
        self.coll = connection[database][collection]

    def get(self):
        start_date = datetime.strptime(self.get_argument('s'), '%Y%m%d')
        end_date = datetime.strptime(self.get_argument('e'), '%Y%m%d')
        end_date += timedelta(days=1) - timedelta(microseconds=1)
        normalize = self.get_argument('n', "true")
        self.set_header('Content-type', 'application/json')
        self.write(json.dumps([w for w in group_by_weeks(self.coll, start_date, end_date, normalize == "true")]))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r"/topics", TopicsScoresHandler, {
            'connection': pymongo.MongoClient('localhost:27017'),
            'database': 'jira',
            'collection': 'issues'})],
        debug=True, static_path="static",
        static_url_prefix="/static/",
        static_hash_cache=False,
        template_path='templates')
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
