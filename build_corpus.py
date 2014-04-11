import pymongo
import argparse
import corpus

from collections import defaultdict
from nltk.corpus import stopwords


class CorpusBuilder(object):
    def __init__(self, conn, query=None, lb=0):
        self.conn = conn

        if query:
            self.query = query
        else:
            self.query = {'fields.issuetype.name': {'$ne': "Tracking"}}

        self.vocabulary = defaultdict(int)
        self.stop = set(stopwords.words('english'))
        self.lb = lb

    def build(self):
        for d in self.conn.find(self.query, ['key', 'fields.description', 'fields.comment.comments']):
            try:
                doc = corpus.CorpusDocument("%s\n\n%s" % (
                    d['fields']['description'],
                    '\n\n'.join([c['body'] for c in d['fields']['comment']['comments']])
                ))
                doc = doc.parse()

                for w in doc:
                    self.vocabulary[w] += 1

                yield {'key': d['key'], 'doc': doc}
            except:
                pass

    def dictionary(self):
        return [p[0] for p in self.vocabulary.items() if p[0] not in self.stop and p[1] > self.lb \
                                                         and len(p[0]) > 2 and len(p[0]) < 15]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', metavar='HOSTNAME:PORT', default='localhost:27017',
                        help='hostname of MongoDB instance')
    parser.add_argument('-d', '--database', metavar='DATABASE', default='jira')
    parser.add_argument('-c', '--collection', metavar='COLLECTION', default='issues')
    parser.add_argument('-q', '--query', metavar='QUERY')
    parser.add_argument('-f', '--file', metavar='FILE')
    parser.add_argument('-l', '--lowerbound', type=int, default=10, metavar='FILE')
    parser.add_argument('-v', '--vocabulary', metavar='FILE')
    args = parser.parse_args()

    conn = pymongo.MongoClient(args.server)[args.database][args.collection]
    cb = CorpusBuilder(conn, query=None, lb=args.lowerbound)
    f = open(args.file, 'w')

    for i, t in enumerate(cb.build()):
        try:
            f.write("%s\n" % ' '.join(t['doc']))
            print 'Done with doc %d: %s' % (i + 1, t['key'])
        except:
            pass

    f.close()

    f = open(args.vocabulary, 'w')

    for w in cb.dictionary():
        f.write('%s\n' % w)

    f.close()
