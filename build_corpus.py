import pymongo
import argparse
import re


class CorpusBuilder(object):
    def __init__(self, hp, db, coll, query=None):
        self.conn = pymongo.MongoClient(hp)[db][coll]
        self.query = query

    def build(self):
        for d in self.conn.find({}, ['fields.description', 'fields.comment.comments']):
            try:
                doc = "%s\n\n%s" % (d['fields']['description'],
                                    '\n\n'.join([c['body'] for c in d['fields']['comment']['comments']]))
                clean = doc.replace('\n', '').replace('\r', '')

                # remove JIRA formatting: {noformat}.*?{noformat}
                clean = re.sub('\{noformat\}.*?\{noformat\}', ' ', clean)

                # remove JIRA formatting: {code(:.*?)?}.*?{code}
                clean = re.sub('\{code(:.*?)?\}.*?\{code\}', ' ', clean)

                yield re.sub('\s{2, }', ' ', clean)
            except:
                pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', metavar='HOSTNAME:PORT', default='localhost:27017',
                        help='hostname of MongoDB instance')
    parser.add_argument('-d', '--database', metavar='DATABASE', default='jira')
    parser.add_argument('-c', '--collection', metavar='COLLECTION', default='issues')
    parser.add_argument('-q', '--query', metavar='QUERY')
    args = parser.parse_args()

    cb = CorpusBuilder(args.server, args.database, args.collection)

    for t in cb.build():
        try:
            print t
        except:
            pass
