import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """


    distribution = {}
    pageamt = len(corpus.keys())

    
    if len(corpus[page]) < 1:
        # choose random page if page has no links
        for i in corpus.keys():
            distribution[i] = 1 / pageamt

    else:
        # if page has links find distribution
        random = (1 - damping_factor) / pageamt
        random_ = damping_factor / pageamt

        for j in corpus.keys():
            if j not in corpus[page]:
                distribution[j] = random
            else:
                distribution[j] = random_ + random

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # prepare dictionary with number of samples == 0
    pages = corpus.copy()
    for i in pages:
        pages[i] = 0
    page = None

 
    for x in range(n):
        if page:
            # if a parent sample is available, choose using transition model
            dictionary = transition_model(corpus, page, damping_factor)
            dictionaryaslist = list(dictionary.keys())
            weightage = [dictionary[i] for i in dictionary]
            page = random.choices(dictionaryaslist, weightage, k = 1)[0]
        else:
            # starting with a page at random
            page = random.choice(list(corpus.keys()))

        # next sample
        pages[page] = pages[page] + 1

    # convert to a percentage!
    for j in pages:
        pages[j] = pages[j] / n

    return pages




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    new = {}
    prev = {}
    

    # "The function should begin by assigning each page a rank of 1 / N, where N is the total number of pages in the corpus."
    for i in corpus:
        prev[i] = 1 / len(corpus)

    # repeatedly calculate new rank values based on all of the current rank values, according to the PageRank formula in the “Background” section
    while 1 == 1:

        for j in corpus:
            value = 0
            for a in corpus:
                # if page contains link to j
                if j in corpus[a]:
                    value = value + (prev[a] / len(corpus[a]))

                # "A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself)."
                if len(corpus[a]) == 0:
                    value = value + (prev[a]) / len(corpus)


            value = value * damping_factor
            value = value + (1 - damping_factor) / len(corpus)

            new[j] = value
        # "This process should repeat until no PageRank value changes by more than 0.001 between the current rank values and the new rank values."
        bpoint = max([abs(new[b] - prev[b]) for b in prev])
        if bpoint < 0.001:
            break
        else:
            prev = new.copy()

    return prev



if __name__ == "__main__":
    main()