import requests
import sys
import argparse
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", dest = "dir_path", required = True)
parser.add_argument("-a", "--only-articles", dest = "only_articles", default = False)
#parser.add_argument("-u", "--url", dest = "url", required = True)
#parser.add_argument("-a", "--api-key", dest = "api_key", required = True)

args = parser.parse_args()

if not os.path.isdir(args.dir_path):
  #print("No directory: " + args.dir_path) 
  sys.exit()

for file_name in os.listdir(args.dir_path):
  with open(os.path.join(args.dir_path, file_name)) as content:
    #print("Reading file " + file_name)
    json_data = json.load(content)
    # If only_articles is set to True and the document is not an article, i.e. publication_type_id not equals 5, 22, or 40, skip it
    if args.only_articles and json_data['data']['publication_type_id'] not in [5, 22, 40]:
      continue
    output = {}    
    for i in json_data['data']['publication_identifiers']:
      #print(i)
      
      if i['identifier_code'] == 'scopus-id':
        output['scopus-id'] = i['identifier_value'] 
        #print("scopus-id: " + i['identifier_value'])
      if i['identifier_code'] == 'doi':
        output['doi'] = i['identifier_value'] 
        #print("doi: " + i['identifier_value'])
      if i['identifier_code'] == 'isi-id':
        output['isi-id'] = i['identifier_value']
        #print("isi-id: " + i['identifier_value'])
      if i['identifier_code'] == 'pubmed':
        output['pubmed'] = i['identifier_value']
        #print("pubmed: " + i['identifier_value'])
    res = json.dumps(output)
    print(res)
