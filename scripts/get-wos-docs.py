import requests
import json
import sys
import os
import argparse
from datetime import date, timedelta, datetime

#'https://api.elsevier.com/content/search/scopus?apiKey=xxxxxxxxx&httpAccept=application/json&date=&count=2&query=AF-ID(%22Goteborgs%20Universitet%22%2060016437)%20AND%20PUBYEAR%20%3E%202015'
#(((AD=("UNIV GOTHENBURG" OR "GOTHENBURG UNIV" OR "SAHLGRENSKA ACAD" OR "UNIV GOTEBORG" OR "UNIV GOTHENBORG" OR "TJARNO MARINE BIOL LAB" OR "CTR EARTH SCI" OR "CHALMERS & GOTEBORG UNIV" OR "FAC ODONTOL" OR "INST CLIN NEUROSCI" OR "Sahlgrenska Univ Hosp & Acad") AND CI=("GOTHENBURG" OR "MOLNDAL" OR "FISKEBACKSKIL" OR "STROMSTAD")))) AND DT=(Article OR Proceedings Paper OR Review)
#AND LOAD-DATE AFT 20200101 AND LOAD-DATE BEF 20200201
base_url = 'https://wos-api.clarivate.com/api/wos'
#base_query = '(((AD=("UNIV GOTHENBURG" OR "GOTHENBURG UNIV" OR "SAHLGRENSKA ACAD" OR "UNIV GOTEBORG" OR "UNIV GOTHENBORG" OR "TJARNO MARINE BIOL LAB" OR "CTR EARTH SCI" OR "CHALMERS & GOTEBORG UNIV" OR "FAC ODONTOL" OR "INST CLIN NEUROSCI" OR "Sahlgrenska Univ Hosp & Acad") AND CI=("GOTHENBURG" OR "MOLNDAL" OR "FISKEBACKSKIL" OR "STROMSTAD")))) AND DT=(Article OR Proceedings Paper OR Review)'
base_query = '(((AD=("UNIV GOTHENBURG" OR "GOTHENBURG UNIV" OR "SAHLGRENSKA ACAD" OR "UNIV GOTEBORG" OR "UNIV GOTHENBORG" OR "TJARNO MARINE BIOL LAB" OR "CTR EARTH SCI" OR "CHALMERS & GOTEBORG UNIV" OR "FAC ODONTOL" OR "INST CLIN NEUROSCI" OR "Sahlgrenska Univ Hosp & Acad") AND CI=("GOTHENBURG" OR "MOLNDAL" OR "FISKEBACKSKIL" OR "STROMSTAD")))) AND DT=(Article OR Abstract of Published Item OR Art Exhibit Review OR Bibliography OR Biographical-Item OR Book OR Book Chapter OR Book Review OR Chronology OR Dance Performance Review OR Data Paper OR Database Review OR Discussion OR Early Access OR Editorial Material OR Excerpt OR Fiction, Creative Prose OR Film Review OR Hardware Review OR Item About an Individual OR Letter OR Meeting Abstract OR Meeting Summary OR Music Performance Review OR Music Score OR Music Score Review OR News Item OR Note OR Poetry OR Proceedings Paper OR Record Review OR Reprint OR Review OR Script OR Software Review OR TV Review, Radio Review OR TV Review, Radio Review, Video OR Theater Review)'


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--apikey", dest = "apikey", required = True)
parser.add_argument("-d", "--load-date", dest = "date", default = datetime.now().date().strftime('%Y-%m-%d'))
parser.add_argument("-v", "--view", dest = "view", default = "COMPLETE")
parser.add_argument("-c", "--count", dest = "count", default = 10)
parser.add_argument("-o", "--output", dest = "output", default = ".")
args = parser.parse_args()

#if args.view == "COMPLETE":
#  fields = 'orig-load-date,load-date,description,link,title,author,creator,publicationName,url,issn,isbn,volume,issueIdentifier,pageRange,coverDate,coverDisplayDate,doi,affiliation,eid,identifier,citedby-count,,aggregationType,subtype,subtypeDescription,author-count,authkeywords,article-number,source-id,pubmed-id,fund-acr,fund-no,fund-sponsor,openaccess,openaccessFlag,freetoread,freetoreadLabel'

print ("Date: " + args.date)
date_object = datetime.strptime(args.date, '%Y-%m-%d').date()

#timespan_query = "AND ORIG-LOAD-DATE AFT " + (date_object + timedelta(days=-1)).strftime('%Y%m%d') + " AND ORIG-LOAD-DATE BEF " + (date_object + timedelta(days=1)).strftime('%Y%m%d') # Only allow one day interval so far...

query = base_query # + " " + timespan_query
print("Query: " + query)
print("ApiKey: " + args.apikey)
print("BaseURL: " + base_url)

#params = {'apiKey': args.apikey, 'httpAccept': 'application/json', 'view': args.view, 'field': fields, 'count': args.count, 'query': query}
params = {'usrQuery': query, 'databaseId': 'WOS', 'count': 5, 'firstRecord': 1}

start = 0

first = True
while (first or start < total):
  #params['start'] = start

  response = requests.get(base_url, params, headers={"X-ApiKey":args.apikey})
  content = response.content
  raw_json = json.loads(content)
  #print(raw_json)
  #sys.exit()

  #total = int(raw_json["search-results"]["opensearch:totalResults"])
  #total = int(raw_json["metadata"]["total"])
  #total = int(raw_json['Data']['Records']['records']['QueryResult']['RecordsFound'])
  #total = 5
  total = int(len(raw_json['Data']['Records']['records']['REC']))

  if total is None or total == 0:
    print("No documents found")
    sys.exit()
  
  if first:
    print("Total number of hits " + str(total))
    if not os.path.exists(f"{args.output}/{args.date}"):
      os.makedirs(f"{args.output}/{args.date}")
      print(f"{args.output}/{args.date}" + " directory doesn't exist, create it")

  #start = int(raw_json["search-results"]["opensearch:startIndex"])
  #items = int(raw_json["search-results"]["opensearch:itemsPerPage"])
  #print("Saving documents from start index : " + str(start))

  #docs = raw_json["hits"]
  docs = raw_json['Data']['Records']['records']['REC']
  print(str(docs))
  for doc in docs:
    #wos_id = doc["dc:identifier"].split("SCOPUS_ID:",1)[1]
    wos_id = doc["UID"][5:999]
    print("uid:" + str(wos_id))
    print(str(doc))
    print("Saving document with WoS-id " + wos_id)
    print(f"{args.output}/{args.date}/{wos_id}.json")
    with open(f"{args.output}/{args.date}/{wos_id}.json", "w") as f:
      json.dump(doc, f)
  start = start + args.count
  first = False
