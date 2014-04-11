import sys, os, re, random, math, urllib2, time, cPickle
import numpy
import argparse
import onlineldavb
from operator import itemgetter


topics_30 = [
"NETWORKING / CONNECTIONS",
"HARDWARE / RESOURCES",
"DRIVERS",
"MMS",
"?1",
"JIRA",
"QUERY",
"REPLICATION",
"REPLICATION",
"STORAGE???",
"NETWORKING / SETUP / LIMITS",
"CHUNKS",
"NETWORKING / PROBLEMS",
"SHARDING / CONFIG SERVER",
"SHARDING / BALANCING",
"DIAGNOSIS",
"SHELL",
"AUTH/SECURITY",
"QUERY / DOCUMENTS",
"OPS / RESTART",
"STORAGE / OPS",
"STORAGE",
"CHUNKS",
"INDEXING",
"UPGRADING",
"INITIAL DIAGNOSIS",
"INDEXING / OPTIMIZATION",
"REPLICASET CONFIGURATION",
"BACKUPS",
"NETWORKING / DNS"
]

def main():

    # The number of documents to analyze each iteration
    batchsize = 64
    
    # The total number of documents in the CS project
    D = 14617

    # argparse arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--vocabulary', action='store', default="../manual_vocab.txt", help='provide vocabulary file')
    argparser.add_argument('-l', '--lambda', action='store', default="./lambda-79-30.dat", help='provide lambda parameter file')
    argparser.add_argument('-s', '--string', action='store', nargs='*', help='string to evaluate')
    args = vars(argparser.parse_args())

    vocab = str.split(file(args['vocabulary']).read())
    init_lambda = numpy.loadtxt(args['lambda'])
    K = init_lambda.shape[0]

    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7, init_lambda)
    gamma, _ = olda.do_e_step( args['string'] )
    gamma = gamma.flatten()
    sorted_ids = sorted ( [(i,g) for i,g in enumerate(gamma) if g > 1.0], key=itemgetter(1), reverse=True)
    scores = map(itemgetter(1), sorted_ids)
    topics = map(lambda x: topics_30[x[0]], sorted_ids)
    print ", ".join( map(lambda x: "%s (%.2f)" % (x[0], x[1]), zip (topics, scores)) )

if __name__ == '__main__':
    main()
