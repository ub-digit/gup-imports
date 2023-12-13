from datetime import datetime
from elasticsearch import Elasticsearch
import sys
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", dest = "dir_path", required = True)
parser.add_argument("-e", "--elastic-url", dest = "elastic_url", default = "http://elasticsearch:9200")
parser.add_argument("-i", "--index-name", dest = "index_name", default = "main")
args = parser.parse_args()
#print(args)
es = Elasticsearch(args.elastic_url)

if not os.path.isdir(args.dir_path):
  print("No directory: " + args.dir_path) 
  sys.exit()

for file_name in os.listdir(args.dir_path):
  with open(os.path.join(args.dir_path, file_name)) as json_file:
    json_content = json.load(json_file)
  print(json_content)
  id = json_content["UID"]
  doc = {'type': 'WOS','wos': json_content}
  resp = es.index(index = args.index_name, id = id, document = doc)
  print(resp['result'])
