import zipfile
import json
from tokenization import Tokenizer
'''
Citations: (https://realpython.com/python-zipfile/) -> encoding + reading from zip file
'''

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


reader = JSONZipReader("NEWDEV.zip")
jsonList = reader.getJSONData()

index = 0
for file in jsonList:
    tokenizeObj = Tokenizer()
    tokenizeObj.tokenize(file['content'])
    print("Processed File #", index)
    index += 1

tokenizeObj.indexSize()







