import nltk
import sys
import os
import math
import string


FILE_MATCHES = 1
SENTENCE_MATCHES = 1

# AI to answer queries

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # dictionary mapping txt file
    mapping = {}
    for fi in os.listdir(directory):
        with open(os.path.join(directory, fi)) as f:
            mapping[fi] = f.read()
    return mapping

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    #tokenize document in lowercase
    words = nltk.word_tokenize(document.lower())
    newdocument = []
    for w in words:
        # if not a stopword or punctuation
        if w not in nltk.corpus.stopwords.words("english") and w not in string.punctuation:
            newdocument.append(w)
    return newdocument

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    wordset = set()
    idfs = dict()
    numdoc = len(documents)
    for fi in documents:
        wordset.update(set(documents[fi]))

    for w in wordset:
        f = sum( w in documents[filename] for filename in documents ) 
        each = math.log(numdoc / f)
        idfs[word] = each

    return idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    matchedfiles = []

    for f in files:
        tfidf = 0

        for i in query:
            tfidf = tfidf + idfs[i] * files[f].count(i)

        matchedfiles.append((f, tfidf))
        # rank according to tfidf

    matchedfiles.sort(key=lambda x: x[1], reverse=True)


    return [x[0] for x in matchedfiles[:n]]
    


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentencelist = []
    
    for s in sentences:
        idf = 0
        wordcount = 0
        for word in query:
            if word in sentences[s]:
                wordcount = wordcount + 1
                idf = idf + idfs[word]
        density = float(wordcount) / len(sentences[s])
        sentencelist.append((s, idf, density))
    # rank by idf
    sentencelist.sort(key = lambda x: (x[1], x[2]), reverse = True)
    # return only n top sentences
    return [x[0] for x in sentencelist[:n]]


if __name__ == "__main__":
    main()