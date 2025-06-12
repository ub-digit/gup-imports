import requests
import json
import sys
import os
import argparse
from datetime import date, timedelta, datetime

def get_affiliations(affiliations):
  # Make sure affiliations is a list
  if not isinstance(affiliations, list):
    affiliations = [affiliations]
  # Loop through all affiliations and create a list of affiliations
  all_affiliations = []
  for affiliation in affiliations:
    affiliation_dict = {}
    affiliation_dict["@_fa"] = "true" # Always true? (Not used)
    affiliation_dict["$"] = affiliation["@id"]
    all_affiliations.append(affiliation_dict)
  return all_affiliations

def get_full_info(scopus_id, api_key):
  # Use the Abstract API to get all authors and affiliations
  base_url = 'https://api.elsevier.com/content/abstract/scopus_id/'
  params = {'apiKey': api_key, 'httpAccept': 'application/json', 'view': 'FULL'}
  response = requests.get(base_url + scopus_id, params)
  content = response.content
  raw_json = json.loads(content)
  authors = raw_json["abstracts-retrieval-response"]["authors"]["author"]
  # Loop through all authors and create a new list of authors
  all_authors = []
  for author in authors:
    author_dict = {}
    author_dict["@_fa"] = author["@_fa"]
    author_dict["@seq"] = author["@seq"]
    author_dict["author-url"] = author["author-url"]
    author_dict["authid"] = author["@auid"]
    author_dict["authname"] = author["ce:indexed-name"]
    author_dict["surname"] = author["ce:surname"]
    # Check if the author has a given name
    if "ce:given-name" in author:
      author_dict["given-name"] = author["ce:given-name"]
    # Check if the author has initials
    if "ce:initials" in author:
      author_dict["initials"] = author["ce:initials"]
    # Check if the author has an affiliation
    if "affiliation" in author:
      author_dict["afid"] = get_affiliations(author["affiliation"])
    all_authors.append(author_dict)

  # Loop through all affiliations and create a new list of affiliations
  all_affiliations = []
  affiliations = raw_json["abstracts-retrieval-response"]["affiliation"]
  for affiliation in affiliations:
    affiliation_dict = {}
    affiliation_dict["@_fa"] = "true" # Always true? (Not used)
    affiliation_dict["affiliation-url"] = affiliation["@href"]
    affiliation_dict["afid"] = affiliation["@id"]
    affiliation_dict["affilname"] = affiliation["affilname"]
    affiliation_dict["affiliation-city"] = affiliation["affiliation-city"]
    affiliation_dict["affiliation-country"] = affiliation["affiliation-country"]
    all_affiliations.append(affiliation_dict)

  # To get the orcid for the author, if any, we need to search in another part of the response
  author_group = raw_json["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["author-group"]
  # This is a list of two objects, one with the key "affiliation" and one with the key "author".
  # The "affiliation" object can be ignored.
  # The "author" object is a list of authors, where the orcid can be found
  # If the author has an orcid, it will be in the "@orcid" key
  # If an ordid is found it will be added to the corresponding author in the all_authors list
  for author in author_group:
    if "author" in author:
      for author_info in author["author"]:
        for author in all_authors:
          if author_info["@seq"] == author["@seq"]:
            if "@orcid" in author_info:
              author["orcid"] = author_info["@orcid"]

  return {"authors": all_authors, "affiliations": all_affiliations}

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
    # Special handling for authors, check if total number of authors is more than 100
    # If key "@total" exists in doc["author-count"], check that the value is greater than 100, otherwise check that the value of "$" key is equal to 100
    if "@total" in doc["author-count"] and int(doc["author-count"]["@total"]) > 100 or doc["author-count"]["$"] == "100":
      print("More than 100 authors for document with Scopus Id " + scopus_id)
      full_info = get_full_info(scopus_id, args.apikey)
      all_authors = full_info["authors"]
      all_affiliations = full_info["affiliations"]
      # Rename the author and affiliation keys to author_org and affiliation_org
      doc["author_org"] = doc["author"]
      doc["affiliation_org"] = doc["affiliation"]
      # Replace the authors and affiliations with the full info
      doc["author"] = all_authors
      doc["affiliation"] = all_affiliations
    print("Saving document with Scopus Id " + scopus_id)
    with open(f"{args.output}/{args.date}/{scopus_id}.json", "w") as f:
      json.dump(doc, f)
  start = start + args.count
  first = False
