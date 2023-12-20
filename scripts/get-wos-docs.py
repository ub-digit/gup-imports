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
base_query = '(((AD=("UNIV GOTHENBURG" OR "GOTHENBURG UNIV" OR "SAHLGRENSKA ACAD" OR "UNIV GOTEBORG" OR "UNIV GOTHENBORG" OR "TJARNO MARINE BIOL LAB" OR "CTR EARTH SCI" OR "CHALMERS & GOTEBORG UNIV" OR "FAC ODONTOL" OR "INST CLIN NEUROSCI" OR "Sahlgrenska Univ Hosp & Acad") AND CI=("GOTHENBURG" OR "MOLNDAL" OR "FISKEBACKSKIL" OR "STROMSTAD"))))'


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--apikey", dest = "apikey", required = True)
parser.add_argument("-d", "--load-date", dest = "date", default = datetime.now().date().strftime('%Y-%m-%d'))
parser.add_argument("-v", "--view", dest = "view", default = "COMPLETE")
parser.add_argument("-c", "--count", dest = "count", default = 10)
parser.add_argument("-o", "--output", dest = "output", default = ".")
args = parser.parse_args()

print ("Date: " + args.date)

query = base_query
print("Query: " + query)

publishTimeSpan = args.date + "+" + args.date
params = {'usrQuery': query, 'databaseId': 'WOS', 'publishTimeSpan': publishTimeSpan, 'count': args.count}

start = 1
first = True

while (first or start <= total):
  params['firstRecord'] = start

  response = requests.get(base_url, params, headers={"X-ApiKey":args.apikey})
  content = response.content
  raw_json = json.loads(content)
  #print(raw_json)
  #sys.exit()

  total = int(raw_json['QueryResult']['RecordsFound'])
  print("total: " + str(total))
  if total is None or total == 0:
    print("No documents found")
    sys.exit()
  
  if first:
    print("Total number of hits " + str(total))
    if not os.path.exists(f"{args.output}/{args.date}"):
      os.makedirs(f"{args.output}/{args.date}")
      print(f"{args.output}/{args.date}" + " directory doesn't exist, create it")

  docs = raw_json['Data']['Records']['records']['REC']
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
