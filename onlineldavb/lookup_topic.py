import sys, os, re, random, math, urllib2, time, cPickle
import numpy

import onlineldavb

def main():

    # The number of documents to analyze each iteration
    batchsize = 64
    
    # The total number of documents in the CS project
    D = 14617

    vocab = str.split(file(sys.argv[1]).read())
    init_lambda = numpy.loadtxt(sys.argv[2])

    K = init_lambda.shape[1]

    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7, init_lambda)


    for k in range(0, len(testlambda)):
        lambdak = list(testlambda[k, :])
        lambdak = lambdak / sum(lambdak)
        temp = zip(lambdak, range(0, len(lambdak)))
        temp = sorted(temp, key = lambda x: x[0], reverse=True)
        print 'topic %d:' % (k)
        # feel free to change the "53" here to whatever fits your screen nicely.
        for i in range(0, 20):
            print '%20s  \t---\t  %.4f' % (vocab[temp[i][1]], temp[i][0])
        print

if __name__ == '__main__':
    main()
