import requests
import json
import sys
import os
import argparse
from datetime import date, timedelta, datetime

#'https://api.elsevier.com/content/search/scopus?apiKey=xxxxxxxxx&httpAccept=application/json&date=&count=2&query=AF-ID(%22Goteborgs%20Universitet%22%2060016437)%20AND%20PUBYEAR%20%3E%202015'
#(AF-ID("Goteborgs Universitet" 60016437) OR AF-ID("Sahlgrenska Academy" 60027675) OR AF-ID("Goteborgs universitet Institutionen for biomedicin" 60079626) OR AF-ID("Tjarno Marine Biological Laboratory" 60055702) OR AF-ID("[No Affiliation ID found" 60008491) OR AF-ID("Goteborgs Universitet Institute of Clinical Sciences" 60004831) OR AF-ID("[No Affiliation ID found" 60010505) OR AF-ID("Hogskolan for Design och Konsthantverk" 60005288)) AND PUBYEAR > 2015
#AND LOAD-DATE AFT 20200101 AND LOAD-DATE BEF 20200201
base_url = 'https://api.elsevier.com/content/search/scopus'
base_query = '(AF-ID("Goteborgs Universitet" 60016437) OR AF-ID("Sahlgrenska Academy" 60027675) OR AF-ID("Goteborgs universitet Institutionen for biomedicin" 60079626) OR AF-ID("Tjarno Marine Biological Laboratory" 60055702) OR AF-ID("[No Affiliation ID found" 60008491) OR AF-ID("Goteborgs Universitet Institute of Clinical Sciences" 60004831) OR AF-ID("[No Affiliation ID found" 60010505) OR AF-ID("Hogskolan for Design och Konsthantverk" 60005288))'

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--apikey", dest = "apikey", required = True)
parser.add_argument("-d", "--load-date", dest = "date", default = datetime.now().date().strftime('%Y-%m-%d'))
parser.add_argument("-v", "--view", dest = "view", default = "COMPLETE")
parser.add_argument("-c", "--count", dest = "count", default = 10)
parser.add_argument("-o", "--output", dest = "output", default = ".")
args = parser.parse_args()

if args.view == "COMPLETE":
  fields = 'orig-load-date,load-date,description,link,title,author,creator,publicationName,url,issn,isbn,volume,issueIdentifier,pageRange,coverDate,coverDisplayDate,doi,affiliation,eid,identifier,citedby-count,,aggregationType,subtype,subtypeDescription,author-count,authkeywords,article-number,source-id,pubmed-id,fund-acr,fund-no,fund-sponsor,openaccess,openaccessFlag,freetoread,freetoreadLabel'

print ("Date: " + args.date)
date_object = datetime.strptime(args.date, '%Y-%m-%d').date()

timespan_query = "AND ORIG-LOAD-DATE AFT " + (date_object + timedelta(days=-1)).strftime('%Y%m%d') + " AND ORIG-LOAD-DATE BEF " + (date_object + timedelta(days=1)).strftime('%Y%m%d') # Only allow one day interval so far...

query = base_query + " " + timespan_query
print("Query: " + query)

params = {'apiKey': args.apikey, 'httpAccept': 'application/json', 'view': args.view, 'field': fields, 'count': args.count, 'query': query}

start = 0

first = True
while (first or start < total):
  params['start'] = start

  response = requests.get(base_url, params)
  content = response.content
  raw_json = json.loads(content)
  #print(raw_json)
  total = int(raw_json["search-results"]["opensearch:totalResults"])

  if total is None or total == 0:
    print("No documents found")
    sys.exit()
  
  if first:
    print("Total number of hits " + str(total))
    if not os.path.exists(f"{args.output}/{args.date}"):
      os.makedirs(f"{args.output}/{args.date}")
      print(f"{args.output}/{args.date}" + " directory doesn't exist, create it")

  start = int(raw_json["search-results"]["opensearch:startIndex"])
  items = int(raw_json["search-results"]["opensearch:itemsPerPage"])
  print("Saving documents from start index : " + str(start))


  docs = raw_json["search-results"]["entry"]
  for doc in docs:
    scopus_id = doc["dc:identifier"].split("SCOPUS_ID:",1)[1]
    print("Saving document with Scopus Id " + scopus_id)
    with open(f"{args.output}/{args.date}/{scopus_id}.json", "w") as f:
      json.dump(doc, f)
  start = start + args.count
  first = False
