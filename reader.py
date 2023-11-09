import zipfile
import json

# open zip
zip_file_path = 'developer.zip'
with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
    # each folder is a subdomain containing webpages
    subdomains = zip_file.namelist()

    # extract JSONs from each subdomain folder
    for subdomain in subdomains:
        with zip_file.open(subdomain) as subdomain_file:
            subdomain_data = subdomain_file.read()
            try:
                # load each page into json_data for processing
                json_data = json.loads(subdomain_data.decode('utf-8'))
                # call process method here to scrape and get info and whatnot
                # process_json(json_data)
            except json.decoder.JSONDecodeError as e:
                print(f"Error in JSON: {subdomain}: {e}")

# function to process JSON data from a file
def process_json(json_data):
    # scraper code goes here
    pass
    # for debugging
    # print(json_data)


# close zip
zip_file.close()
