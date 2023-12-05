import zipfile
import json
import re
import sys

import math
from nltk import PorterStemmer
from bs4 import BeautifulSoup


def defaultInt():  # used for lambda functions within default dictionary
    return 0


class JSONZipReader:
    def __init__(self, zipFileName):
        self.zipFileName = zipFileName

    def getJSONFiles(self):
        openedZip = zipfile.ZipFile(self.zipFileName, 'r')
        subdirectories = openedZip.namelist()

        for file in subdirectories:
            # check if current file is directory or regular file
            subdirectoryInfo = openedZip.getinfo(file)
            if not subdirectoryInfo.is_dir():
                try:
                    subdirectoryContent = openedZip.read(file).decode(encoding="utf-8")
                    yield json.loads(subdirectoryContent)
                except json.decoder.JSONDecodeError as e:
                    print(f"Error in JSON: {file}: {e}")
        openedZip.close()



class HtmlContent:
    def __init__(self):
        self.unwantedTags = ['style', 'script', 'a', 'nav', 'link', 'img', 'br', 'meta', 'canvas']

    def getText(self, html_content):
        try:  # handling broken html
            soup = BeautifulSoup(html_content, "html.parser")
            for data in soup(self.unwantedTags):
                #  Citation: https://www.geeksforgeeks.org/how-to-remove-tags-using-beautifulsoup-in-python/
                data.decompose()  # directly removes tag and corresponding contents from html tree
            text = soup.getText()
            return text
        except Exception as e:
            print(e)


class Tokenizer:
    def tokenize(self, text):
        tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
        return tokens


class Stemmer:
    # CITATION: https://pythonprogramming.net/stemming-nltk-tutorial/ (HOW TO USE PORTER STEMMING)
    def __init__(self):
        self.stemmer = PorterStemmer()

    def stem(self, tokenslist):
        #returns stemmed tokens list
        return [self.stemmer.stem(token) for token in tokenslist]


class Idf:
    def __init__(self, idfFilePath, totalDocuments):
        self.idfFilePath = idfFilePath
        self.totalDocuments = totalDocuments
        self.mapTermToIdf = {}

    def getIdf(self, term):
        if term not in self.mapTermToIdf:
            # creating file path to open. term[0] gives the first character of term which is the file that term belongs to
            with open(self.idfFilePath + term[0] + ".txt", "r", encoding='utf-8') as f:  # so that not all files are opened. only specific one with the passed term
                while True:
                    line = f.readline()
                    if line == '':  # end of file
                        break
                    line = line[:-1]  # removes new line character "\n"
                    splitArr = line.split(' ')
                    self.mapTermToIdf[splitArr[0]] = len(splitArr[1:]) # stored in memory for further computation

        return math.log(self.totalDocuments / float(self.mapTermToIdf[term]))


class SparseVector: # custom vector class to handle sparse vectors for memory
    # mapIndexValue(urlVector): {index, tf-idf}
    def __init__(self, mapIndexValue):
        self.mapIndexValue = mapIndexValue
        self.vectorMagnitude = self.getMagnitude()

    def dotProduct(self, v):
        # Citation: https://www.mathsisfun.com/algebra/vectors-dot-product.html    (formulas for dot product)
        commonIndices = set(self.mapIndexValue.keys()).intersection(set(v.mapIndexValue.keys())) # set intersection method
        sum = 0
        for index in commonIndices:
            sum += self.mapIndexValue[index] * v.mapIndexValue[index]
        return sum  # return 0 if no intersection

    def getMagnitude(self):
        magnitude = 0
        for value in self.mapIndexValue.values():
            magnitude += value * value
        return math.sqrt(magnitude)

    def cosineAngle(self, v):
        #Citation for formula: https://towardsdatascience.com/cosine-similarity-how-does-it-measure-the-similarity-maths-behind-and-usage-in-python-50ad30aad7db
        return float(self.dotProduct(v)) / (self.vectorMagnitude * v.vectorMagnitude)