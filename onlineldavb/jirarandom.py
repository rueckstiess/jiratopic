f = open('../cs.txt', 'r')

def get_next_jira_ticket():
    global f

    while True:
        for line in f:
            line = line.strip()
            yield line

        f.close()
        f = open('../cs.txt', 'r')


gen = get_next_jira_ticket()

def get_jira_batch(batchsize):
    full_texts = []

    for i in range(batchsize):
        full_texts.append( next(gen) )

    return full_texts


if __name__ == '__main__':
    print get_jira_batch(20000)
