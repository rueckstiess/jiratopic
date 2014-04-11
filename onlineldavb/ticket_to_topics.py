import pymongo
import argparse
import re
import nltk
import numpy
import onlineldavb
from collections import defaultdict

from nltk.corpus import stopwords

class TicketLoader(object):
    def __init__(self, hp, db, coll):
        self.conn = pymongo.MongoClient(hp)[db][coll]

        self.wl = nltk.WordNetLemmatizer()
        self.stop = set(stopwords.words('english'))

    def build(self):
        for d in self.conn.find({}, fields=['_id', 'key', 'fields.description', 'fields.comment.comments']):
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
                    
                yield {'_id': d['_id'], 'key': d['key'], 'doc': doc}
            except:
                yield ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', metavar='HOSTNAME:PORT', default='localhost:27017',
                        help='hostname of MongoDB instance')
    parser.add_argument('-d', '--database', metavar='DATABASE', default='jira')
    parser.add_argument('-c', '--collection', metavar='COLLECTION', default='issues')
    parser.add_argument('-v', '--vocabulary', action='store', default="../manual_vocab.txt", help='provide vocabulary file')
    parser.add_argument('-l', '--model', action='store', default="./lambda-79-30.dat", help='provide lambda model file')

    args = parser.parse_args()

    # The number of documents to analyze each iteration
    batchsize = 64
    
    # The total number of documents in the CS project
    D = 14617

    tl = TicketLoader(args.server, args.database, args.collection)
    
    vocab = str.split(file(args.vocabulary).read())
    init_lambda = numpy.loadtxt(args.model)
    K = init_lambda.shape[0]

    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7, init_lambda)

    for t in tl.build():
        try:
            doc_str = " ".join(t['doc']).encode("utf8")
            gamma, _ = olda.do_e_step( doc_str )
            gamma = list(gamma.flatten())
            print gamma
        except Exception as e: 
            print "skipped", 
            print e.message

 


