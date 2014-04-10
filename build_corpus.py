import pymongo
import argparse
import re
import nltk

from collections import defaultdict

from nltk.corpus import stopwords

class CorpusBuilder(object):
    def __init__(self, hp, db, coll, lb=0, query=None):
        self.conn = pymongo.MongoClient(hp)[db][coll]

        if query:
            self.query = query
        else:
            self.query = {'fields.issuetype.name': {'$ne': "Tracking"}}

        self.wl = nltk.WordNetLemmatizer()
        self.vocabulary = defaultdict(int)
        self.stop = set(stopwords.words('english'))
        self.lb = lb

    def build(self):
        for d in self.conn.find(query, ['key', 'fields.description', 'fields.comment.comments']):
            try:
                doc = "%s\n\n%s" % (d['fields']['description'],
                                    '\n\n'.join([c['body'] for c in d['fields']['comment']['comments']]))
                clean = doc.replace('\n', ' ').replace('\r', ' ')

                # remove JIRA formatting: {noformat}.*?{noformat}
                clean = re.sub('\{noformat\}.*?\{noformat\}', ' ', clean)

                # remove JIRA formatting: {code(:.*?)?}.*?{code}
                clean = re.sub('\{code(:.*?)?\}.*?\{code\}', ' ', clean)

                # remove anything in square brackets
                clean = re.sub('\[.*?\]', ' ', clean)

                clean = re.sub('\s', ' ', clean)
                clean = re.sub(r'\b([A-Za-z]*[-:/\._0-9]+)+[A-Za-z]*\b', ' ', clean)
                clean = re.sub('[^A-Za-z ]', '', clean)
                clean = re.sub('\s+', ' ', clean)
                doc = []

                for w in clean.split():
                    word = self.wl.lemmatize(w.lower())
                    doc.append(word)
                    self.vocabulary[word] += 1

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

    cb = CorpusBuilder(args.server, args.database, args.collection, args.lowerbound)
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
