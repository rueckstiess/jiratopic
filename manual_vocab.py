import re
import sys
import nltk

from nltk.corpus import stopwords
from collections import defaultdict


def main():
    wl = nltk.WordNetLemmatizer()
    dictionary = defaultdict(int)

    for l in sys.stdin:
        l = l.strip()
        l = re.sub('^\.\.', ' ', l)
        l = re.sub(':.*?:', ' ', l)
        l = re.sub('`.*?`', ' ', l)
        l = re.sub('[^A-Za-z ]', ' ', l)
        l = re.sub('\s{2,}', ' ', l)

        for w in l.split():
            word = wl.lemmatize(w.lower())
            dictionary[word] += 1

    stop = set(stopwords.words('english'))

    for w in sorted(set(dictionary.keys()).difference(stop)):
        if len(w) > 2 and len(w) < 15:
            print w

if __name__ == '__main__':
    main()
