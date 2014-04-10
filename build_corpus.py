import pymongo
import argparse
import re
import nltk

from nltk.corpus import stopwords

class CorpusBuilder(object):
    def __init__(self, hp, db, coll, query=None):
        self.conn = pymongo.MongoClient(hp)[db][coll]
        self.query = query   # TODO
        self.wl = nltk.WordNetLemmatizer()
        self.vocabulary = set()
        self.stop = set(stopwords.words('english'))

    def build(self):
        for d in self.conn.find({}, ['fields.description', 'fields.comment.comments']):
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
                clean = re.sub(r'\b([A-Za-z]+[!#-_\./:]+)+[A-Za-z]+\b', ' ', clean)
                clean = re.sub('[^A-Za-z ]', '', clean)
                clean = re.sub('\s+', ' ', clean)
                doc = []

                for w in clean.split():
                    word = self.wl.lemmatize(w.lower())
                    doc.append(word)
                    self.vocabulary.add(word)

                yield doc
            except:
                pass

    def dictionary(self):
        return self.vocabulary.difference(self.stop)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', metavar='HOSTNAME:PORT', default='localhost:27017',
                        help='hostname of MongoDB instance')
    parser.add_argument('-d', '--database', metavar='DATABASE', default='jira')
    parser.add_argument('-c', '--collection', metavar='COLLECTION', default='issues')
    parser.add_argument('-q', '--query', metavar='QUERY')
    parser.add_argument('-f', '--file', metavar='FILE')
    parser.add_argument('-v', '--vocabulary', metavar='FILE')
    args = parser.parse_args()

    cb = CorpusBuilder(args.server, args.database, args.collection)
    f = open(args.file, 'w')

    for i, t in enumerate(cb.build()):
        try:
            f.write("%s\n" % ' '.join(t))
            f.flush()
            print 'Done with doc %d' % (i + 1)
        except:
            pass

    f.close()

    f = open(args.vocabulary, 'w')

    for w in cb.dictionary():
        f.write('%s\n' % w)
        f.flush()

    f.close()
