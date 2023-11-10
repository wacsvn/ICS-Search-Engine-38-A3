import zipfile
import json
import re
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from bs4 import BeautifulSoup


'''
Citations: (https://realpython.com/python-zipfile/) -> encoding + reading from zip file
'''

# inverted index to store key as token and value as posting (doc found in and tf-idf)
inv_index = defaultdict(dict)

class JSONZipReader:

    def __init__(self, zip_file):
        self.zip_file = zip_file

    def getJSONData(self):
        jsonList = []
        # open zip
        with zipfile.ZipFile(self.zip_file, 'r') as zip_file:
            # each folder is a subdomain containing webpages
            subdirectories = zip_file.namelist()

            # extract JSONs from each subdomain folder
            for file in subdirectories:
                subdirectoryInfo = zip_file.getinfo(file)
                if not subdirectoryInfo.is_dir():
                    try:
                        subdirectoryContent = zip_file.read(file).decode(encoding="utf-8")

                        # load each page into json_data for processing
                        json_data = json.loads(subdirectoryContent)
                        jsonList.append(json_data)
                        # call process method here to scrape and get info and whatnot
                            # process_json(json_data)
                    except json.decoder.JSONDecodeError as e:
                        print(f"Error in JSON: {file}: {e}")

        return jsonList


reader = JSONZipReader("test.zip")  # changed zip to be the name of the file downloaded from canvas
jsonList = reader.getJSONData()

"""
    TF-IDF CALCULATION:
        - uses jsonList to fit against vectorized TfIdf's
        - extracts resulting matrix and stores in inv_index in the format 
                                            (token, [(document it was found in), (tf_idf)]) 
        - citation: #2
"""

# create a list of texts for vectorization later
texts = [json_data['content'] for json_data in jsonList]

# print("beginning td-idf") # debug
# begin tf-df calculations
tfidf = TfidfVectorizer()
tfidfList = tfidf.fit_transform(texts)
print(f"td-idf type:  {type(tfidfList)}") # debug

# iterate tfidList matrix to ultimately store in inv_index
for row, col, value in zip(tfidfList.nonzero()[0], tfidfList.nonzero()[1], tfidfList.data):
    # get the document id, term id, and tf-idf score
    doc_id = row
    term_id = col
    tf_idf = value
    # get the term corresponding to the term id
    term = tfidf.get_feature_names_out()[term_id]
    # check if the term already exists in the inv_index dictionary
    if term not in inv_index:
        # create a new entry with an empty list as the value
        inv_index[term] = []
    # append a tuple of (document id, tf-idf score) to the "posting list"
    inv_index[term].append((doc_id, tf_idf))

print(inv_index)


class DataStorage:
    # Citation -> (https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/#)
    def __init__(self):
        self.invertedIndex = defaultdict(lambda: list())  # key(token), value(list of documents that token appears on)
        self.totalWords = defaultdict(lambda: 0)  # key(url), value(# of tokens for that url)
        self.frequencyWordsInDocument = defaultdict(lambda: defaultdict(lambda: 0))  # key(url), value(dictionary where key is token and value is number of occurences of that token)
        self.indexedFileCount = 0  # initialize counter for indexed files

    def addTokens(self, url, tokens):
        innerDict = self.frequencyWordsInDocument[url]
        for token in tokens:
            self.invertedIndex[token].append(url)
            innerDict[token] += 1

        self.totalWords[url] = len(tokens)
        self.indexedFileCount += 1

    def uniqueWordCount(self):
        uniqueWords = set(self.invertedIndex.keys())  # using set collection for uniqueness
        print(f"Number of unique words in the zip file: {len(uniqueWords)}")

    def indexSize(self):
        size = sys.getsizeof(self.invertedIndex)  # getsizeof returns the size of the object in bytes
        sizeKB = size / 1024  # turning the size into KB
        print(f"Size of the index on disk: {sizeKB:.2f} KB")  # rounded up to 2nd decimal place

    def printData(self):
        print(self.totalWords)

    def printIndexedFileCount(self):
        print(f"Total number of indexed files: {self.indexedFileCount}")


class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, text):
        return re.findall(r'[a-zA-Z0-9]+', text.lower())




index = 0
dataStorage = DataStorage()  # make a dataStorage object from the class to store tokens
for file in jsonList:
    tokenizeObj = Tokenizer()
    tokens = tokenizeObj.tokenize(file['content'])
    dataStorage.addTokens(f"file_{index}", tokens)  # adding tokens
    print("Processed File #", index)
    index += 1

dataStorage.indexSize()
dataStorage.printIndexedFileCount()
dataStorage.uniqueWordCount()





