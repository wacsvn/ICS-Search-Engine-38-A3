import zipfile
import json
from tokenization import *
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
'''
Citations: 
1. (https://realpython.com/python-zipfile/) -> encoding + reading from zip file
2. (https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/#) -> calculating 
tf-idf
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

# merge JSONs into single corpus
reader = JSONZipReader("test.zip")      # if "test.zip", only first 2 folders of developer.zip
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


index = 0
for file in jsonList:
    tokenizeObj = Tokenizer()
    tokenizeObj.tokenize(file['content'])
    print("Processed File #", index)
    index += 1
tokenizeObj.indexSize()







