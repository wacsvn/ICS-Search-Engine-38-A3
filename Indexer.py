import heapq
import os
import pickle
from collections import defaultdict

from Commons import *


def defaultList():
    return list()


class TfIdfIndexer:
    def __init__(self):
        self.tfDumpPath = "./data/tmp/tf/"  # location of where to store tf dumps
        self.tfDumpFilePrefix = "tf_"
        self.tfFileIndex = 1

        self.idfDumpPath = "./data/tmp/idf/"  # location of where to store idf dumps(portion of idf computation, not fully IDF)
        self.idfFinalPath = "./data/idf/"     # stores all txt files containing idf values sorted alphabetically
        self.idfDumpFilePrefix = "idf_"
        self.idfFileIndex = 1

        # Citation: https://www.geeksforgeeks.org/create-a-directory-in-python/  for how to make a directory
        os.makedirs(self.tfDumpPath, exist_ok=True)
        os.makedirs(self.idfDumpPath, exist_ok=True)
        os.makedirs(self.idfFinalPath, exist_ok=True)

        self.vocab = {}  # list of all tokens from all documents that are indexed
        self.totalDocuments = 0

        self.mapUrlToTf = {}
        self.mapTokenToIdf = defaultdict(defaultList)

    def getVocabCount(self):
        return len(self.vocab)

    def getVocabIndex(self, term):
        return self.vocab[term]

    def getTotalDocuments(self):
        return self.totalDocuments

    def addTf(self, url, mapTokenFreq, tokenCount):
        self.totalDocuments += 1
        mapTokenToTf = {}

        for token in mapTokenFreq:
            self.mapTokenToIdf[token].append(url)  # need this for later computation of IDF(denominator)
            mapTokenToTf[token] = float(mapTokenFreq[token]) / tokenCount  # term frequency computation

            if token not in self.vocab:
                self.vocab[token] = len(self.vocab) #index keeps incrementing everytime new token is added to vocab list
        self.mapUrlToTf[url] = mapTokenToTf

    def getTfMaps(self):
        for tempFile in os.listdir(self.tfDumpPath):  # gives all term frequencies files within directory path
            with open(self.tfDumpPath + tempFile, "rb") as f:
                tempMap = pickle.load(f)
            yield tempMap

    def dumpTf(self):
        file = self.tfDumpPath + self.tfDumpFilePrefix + str(self.tfFileIndex) + ".pkl"
        with open(file, "wb") as f:
            pickle.dump(self.mapUrlToTf, f)  # offload data to disk
        self.tfFileIndex += 1  # naming files by number
        self.mapUrlToTf = {}   # free up memory

    def dumpIdf(self):
        file = self.idfDumpPath + self.idfDumpFilePrefix + str(self.idfFileIndex) + ".txt"
        with open(file, "w", encoding='utf-8') as f:
            for key in sorted(self.mapTokenToIdf.keys()):
                urlsAsString = " ".join(self.mapTokenToIdf[key])
                f.writelines([key + " " + urlsAsString + "\n"]) # ex format of writing "a:12\n"
        self.idfFileIndex += 1
        self.mapTokenToIdf = defaultdict(defaultList)

    #uci http://uci.edu http://informatics.uci.edu
    def readFrequencies(self, tempFile):
        f = open(tempFile, "r", encoding='utf-8')
        while True:
            line = f.readline()
            if line == '':  # end of file
                break

            line = line[:-1]  # delete new line char
            tempArr = line.split(' ')  # term is everything prior to ':', frequency is everything after ':'
            yield tempArr[0], tempArr[1:]  # returning term, frequency
        f.close()

    def mergeIdf(self):
        files = []
        for file in os.listdir(self.idfDumpPath):

            files.append(self.readFrequencies(self.idfDumpPath + file))

        # Citation: https://realpython.com/python-heapq-module/
        # Citation: https://www.geeksforgeeks.org/merge-two-sorted-arrays-python-using-heapq/#
        mergedIdfs = heapq.merge(*files)  # merging all idf files in list, merge returns an iterable

        currentFile = None
        currentTerm = None
        currentFrequency = None
        for term, frequency in mergedIdfs:
            if currentTerm is None:
                currentTerm = term
                currentFrequency = frequency
                currentFile = open(self.idfFinalPath + currentTerm[0] + ".txt", "w", encoding='utf-8')

            elif currentTerm == term:  # when same term exists in multiple files
                currentFrequency += frequency
            else:
                currentFile.writelines([currentTerm + " " + " ".join(currentFrequency) + "\n"])

                # check if the new term has the same starting alphabet as before(determining which file to offload to)
                if term[0] != currentTerm[0]:
                    # by here, done with previous alphabet and moving onto next
                    currentFile.close()
                    currentFile = open(self.idfFinalPath + term[0] + ".txt", "w", encoding='utf-8')

                currentTerm = term
                currentFrequency = frequency

        currentFile.writelines([currentTerm + " " + " ".join(currentFrequency) + "\n"])  # storing last (term,frequency) pair
        currentFile.close()