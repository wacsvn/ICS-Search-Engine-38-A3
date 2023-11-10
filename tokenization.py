import re
from bs4 import BeautifulSoup
from collections import defaultdict


class DataStorage:
    # Citation -> (https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/#)
    def __init__(self):
        self.invertedIndex = defaultdict(lambda: list())  # key(token), value(list of documents that token appears on)
        self.totalWords = defaultdict(lambda: 0)  # key(url), value(# of tokens for that url)
        self.frequencyWordsInDocument = defaultdict(lambda: defaultdict(lambda: 0)) #key(url), value(dictionary where key is token and value is number of occurences of that token)

    def addTokens(self, url, tokens):
        innerDict = self.frequencyWordsInDocument[url]
        for token in tokens:
            self.invertedIndex[token].append(url)
            innerDict[token] += 1

        self.totalWords[url] = len(tokens)


    def printData(self):
        print(self.totalWords)

class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, text):
        return re.findall(r'[a-zA-Z0-9]+', text.lower())
