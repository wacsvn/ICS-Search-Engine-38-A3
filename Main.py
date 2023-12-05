import time
import pickle
import tkinter as tk
from collections import defaultdict

from Commons import *
from Indexer import TfIdfIndexer
from QuerySearch import Search

def main():
    reindex = True  # variable for purposes of demo whether to reindex or just demonstrate search(index already completed)
    vectorStorageFile = "./vector.pkl"

    tokenizer = Tokenizer()
    stemmer = Stemmer()
    htmlContent = HtmlContent()

    if reindex:
        startTime = time.time()
        jsonReader = JSONZipReader("developer.zip")

        tfidfIndexer = TfIdfIndexer()
        for index, jsonFile in enumerate(jsonReader.getJSONFiles()):
            url = jsonFile['url']
            print("Indexing Document: #", index, " tokens: ", tfidfIndexer.getVocabCount(), " URL: ", url)

            html = htmlContent.getText(jsonFile['content'])
            tokens = tokenizer.tokenize(html)
            tokens = stemmer.stem(tokens)
            tokenCount = len(tokens)

            mapTermToFrequency = defaultdict(defaultInt)
            for token in tokens: # iterate through stemmed tokens to find number of occurences per term in current JSON
                mapTermToFrequency[token] += 1

            # continue to next JSON if there are no tokens in current JSON
            if len(mapTermToFrequency) == 0:
                continue

            tfidfIndexer.addTf(url, mapTermToFrequency, tokenCount)
            if ((index + 1) % 10000) == 0: # Offload every 10000 documents. Because index starts at 0, must do index + 1
                tfidfIndexer.dumpTf()  # offload to disk

            if ((index + 1) % 10000) == 0:
                tfidfIndexer.dumpIdf()  # offload to disk

        tfidfIndexer.dumpTf()
        tfidfIndexer.dumpIdf()

        tfidfIndexer.mergeIdf()
        mapUrlToVector = {}  # vectorize documents and compute tf-idf
        idf = Idf(tfidfIndexer.idfFinalPath, tfidfIndexer.getTotalDocuments())
        for mapUrlToTf in tfidfIndexer.getTfMaps():
            for url in mapUrlToTf:
                urlVector = {}
                innerTfMap = mapUrlToTf[url]
                for term in innerTfMap:
                    tfidfScore = innerTfMap[term] * idf.getIdf(term)  # tf * idf
                    indexOfToken = tfidfIndexer.getVocabIndex(term)  # get index from vocabulary of all tokens
                    urlVector[indexOfToken] = tfidfScore
                mapUrlToVector[url] = SparseVector(urlVector)  # document vector

        with open(vectorStorageFile, "wb") as f:
            pickle.dump([mapUrlToVector, tfidfIndexer.vocab], f)  #offloading document vectors for purposes of not having to reindex everytime. Can simply load to search

        endTime = time.time()
        print("Indexing time :", 1000 * (float(endTime - startTime)), "milliseconds ")

    with open(vectorStorageFile, "rb") as f:  # loading all document vectors
        mapUrlToVector, vocab = pickle.load(f)
    totalDocuments = len(mapUrlToVector)
    print("Total Documents:", totalDocuments)
    idf = Idf("./data/idf/", totalDocuments)  # get idfs from disk

    searchObj = Search(mapUrlToVector, vocab)

    def searchString():
        queryString = searchEntry.get()
        searchResults = searchObj.search(queryString)

        results.config(state="normal")
        results.delete('1.0', tk.END)
        results.insert('1.0', searchResults)
        results.config(state="disabled")

    # Local GUI using tkinter
    # Citation: https://www.geeksforgeeks.org/python-gui-tkinter/
    # Citation: https://docs.python.org/3/library/tkinter.ttk.html#widget-states
    mainTk = tk.Tk()
    mainTk.geometry("1200x600")
    mainTk.title('Counting Seconds')

    searchFrame = tk.Frame(mainTk, borderwidth=10)
    searchFrame.pack()

    searchEntry = tk.Entry(searchFrame, width=75)
    searchEntry.grid(row=0, column=0)

    button = tk.Button(searchFrame, text='Search', width=25, command=searchString)
    button.grid(row=0, column=1)

    resultsLabel = tk.Label(searchFrame, width=25, text='Results ')
    resultsLabel.grid(row=1)

    results = tk.Text(searchFrame, width=100, height=20)
    results.grid(row=15)
    results.config(state="disabled")

    mainTk.mainloop()



if __name__ == "__main__":
    main()