from collections import defaultdict
import time

from Commons import *


class Search:

    def __init__(self, mapUrlToVector, vocabList):
        self.mapUrlToVector = mapUrlToVector
        self.vocabList = vocabList
        self.idf = Idf("./data/idf/", len(mapUrlToVector))  # get idfs from disk

        self.tokenizer = Tokenizer()
        self.stemmer = Stemmer()

    def search(self, query):

        queryStartTime = time.time()
        queryTokens = self.tokenizer.tokenize(query)
        queryTokens = self.stemmer.stem(queryTokens)

        # Calculating tf-idf treating user query as a document
        queryTermFrequency = defaultdict(lambda: 0)
        for token in queryTokens:
            queryTermFrequency[token] += 1

        # override term frequency values
        for token in queryTermFrequency.keys():
            queryTermFrequency[token] = float(queryTermFrequency[token]) / len(queryTokens)

        # vectorize and calculate tf-idf of user query
        userQueryVectorMap = {}
        for token in queryTokens:
            if token not in self.vocabList:
                continue

            tfidfScore = queryTermFrequency[token] * self.idf.getIdf(token)
            indexOfToken = self.vocabList[token]
            userQueryVectorMap[indexOfToken] = tfidfScore
        userQueryVector = SparseVector(userQueryVectorMap)

        # --------------------
        # Apply cosine similarity to user query vector and document vectors
        # ---------------------
        # Citation - https://www.geeksforgeeks.org/how-to-calculate-cosine-similarity-in-python/
        cosineSimilarityList = []
        for index, url in enumerate(self.mapUrlToVector.keys()):
            #print("Calculating cosine ", index)
            cosineSimilarity = userQueryVector.cosineAngle(self.mapUrlToVector[url])
            cosineSimilarityList.append((url, cosineSimilarity))

        # citation: https://stackoverflow.com/questions/3121979/how-to-sort-a-list-tuple-of-lists-tuples-by-the-element-at-a-given-index
        sortedCosineSimilarityList = sorted(cosineSimilarityList, key=lambda data: data[1])
        queryEndTime = time.time()
        searchResult = ""

        tempCount = 0
        for url, cosine in reversed(sortedCosineSimilarityList):
            if cosine > 0:
                tempCount += 1
                searchResult += url + "\n"

        print("It took ", float(queryEndTime - queryStartTime) * 1000, "milliseconds")
        print("Result-set count:", tempCount)

        return searchResult