import json
import argparse
import os
import sys

def get_data(key, data):
  if data is None:
    return None
  if key in data:
    return data[key]
  else:
    return None

def get_publication_type(input_data):
  source_type	= get_data("prism:aggregationType", input_data)
  document_type = get_data("subtypeDescription", input_data)
  
  if source_type is None:
    return None
  if document_type is None:
    return None

  source_type	= source_type.lower()
  document_type = document_type.lower()

  if source_type == "journal" and document_type == "article":
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "conference paper":
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "review":
    return {"id": 22, "ref_value": "ISREF", "label": "Forskningsöversiktsartikel (Review article)"}
  elif source_type == "journal" and document_type == "editorial":
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "journal" and document_type == "letter":
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "journal" and document_type == "note":
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "journal" and document_type == "short survey":
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "book" and document_type == "book chapter":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "conference proceeding" and document_type == "conference paper":
    return {"id": 2, "ref_value": "ISREF", "label": "Paper i proceeding"}
  elif source_type == "book series" and document_type == "book chapter":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book" and document_type == "book":
    return {"id": 9, "ref_value": "NOTREF", "label": "Bok"}
  elif source_type == "book series" and document_type == "book":
    return {"id": 9, "ref_value": "NOTREF", "label": "Bok"}
  elif source_type == "book" and document_type == "editorial":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "conference proceeding" and document_type == "editorial":
    return {"id": 1, "ref_value": "NOTREF", "label": "Konferensbidrag (offentliggjort, men ej förlagsutgivet)"}
  elif source_type == "conference proceeding" and document_type == "book chapter":
    return {"id": 2, "ref_value": "ISREF", "label": "Paper i proceeding"}
  elif source_type == "book series" and document_type == "conference paper":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "article":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "review":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "note":
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  else:
    return None

def get_year(date):
  # Assumeing yyyy-mm-dd format
  return date[:4]

def format_issn(issn):
  if issn is None:
    return None
  if len(issn) == 9 and issn[5] == "-":
    return issn
  issn = issn.replace("(ISSN)", "")
  issn = issn.strip()
  if len(issn) == 8:
    return issn[:4] + "-" + issn[4:]
  return issn

def get_scopus_id(input_data):
  return get_data("dc:identifier", input_data).replace("SCOPUS_ID:", "")

def get_isbn(input_data):
  if input_data is None:
    return None
  return input_data[0]['$']

def format_keywords(keywords):
  if keywords is None:
    return None
  else:
    return ", ".join(keywords.split(" | "))

def create_publication_identifier_entry(code, value):
  return {"identifier_code": code,  "identifier_value": value}

def create_publication_identifiers(input_data):
  identifiers = []
  # scopus
  scopus_value = get_scopus_id(input_data)
  identifiers.append(create_publication_identifier_entry("scopus-id", scopus_value))
  # doi
  doi_value = get_data("prism:doi", input_data)
  if doi_value is not None:
    identifiers.append(create_publication_identifier_entry("doi", doi_value))
  # pubmed
  pubmed_value = get_data("prism:pubmed-id", input_data)
  if pubmed_value is not None:
    identifiers.append(create_publication_identifier_entry("pubmed", pubmed_value))
  return identifiers

def get_publication_affiliations(input_data):
  affiliations = []
  for affiliation in input_data["affiliation"]:
    affiliations.append({"scopus-afid": get_data("afid", affiliation), "scopus-affilname": get_data("affilname", affiliation), "scopus-affiliation-city": get_data("affiliation-city", affiliation), "scopus-affiliation-country": get_data("affiliation-country", affiliation)})
  return affiliations

def get_person_affiliations(input_data, publication_affiliations):
  person_affiliations = []
  for publication_affiliation in publication_affiliations:
    #print(publication_affiliation)
    for afid in input_data:
      #print(get_data("$", afid))
      if get_data("$", afid) == publication_affiliation["scopus-afid"]:
        person_affiliations.append(publication_affiliation)
  return person_affiliations

def create_person_identifier_entry(type, value):
  return {"type": type,  "value": value}

def create_person_identifiers(input_data):
  identifiers = []
  # orcid
  orcid_value = get_data("orcid", input_data)
  #print(orcid_value)
  if orcid_value is not None:
    identifiers.append(create_person_identifier_entry("orcid", orcid_value))
  # scopus-auth-id
  authid_value = get_data("authid", input_data)
  if authid_value is not None:
    identifiers.append(create_person_identifier_entry("scopus-auth-id", authid_value))
  return identifiers

def create_authors(input_data):
  publication_affiliations = get_publication_affiliations(input_data)
  authors = []
  for author in get_data("author", input_data):
    affid = get_data("afid", author)
    person_affiliations = []
    if affid is not None:
      person_affiliations = get_person_affiliations(affid, publication_affiliations)
    person = {}
    person["position"] = get_data("@seq", author)
    person["last_name"] = get_data("surname", author)
    person["first_name"] = get_data("given-name", author)
    person["identifiers"] = create_person_identifiers(author)

    authors.append({"affiliations": person_affiliations, "person": [person]})
  return authors

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source-dir", dest = "source_path", required = True)
parser.add_argument("-d", "--dest-base-dir", dest = "dest_base_path", required = True)
args = parser.parse_args()

if not os.path.isdir(args.source_path):
  print("No directory: " + args.source_path) 
  sys.exit()

for file_name in os.listdir(args.source_path):
  with open(os.path.join(args.source_path, file_name)) as input_file:
      input_data = json.load(input_file)
      scopus_id = get_scopus_id(input_data)

      publication_type = get_publication_type(input_data)
      if publication_type is None:
        print("No publication type mapping for scopus id: " + scopus_id)
        continue
      output_data = {"data": {}}
      output_data["data"]["id"] = "scopus_" + scopus_id
      output_data["data"]["publication_type_id"] = publication_type["id"]
      output_data["data"]["publication_type_label"] = publication_type["label"]
      output_data["data"]["ref_value"] = publication_type["ref_value"]
      output_data["data"]["title"] = get_data("dc:title", input_data)
      output_data["data"]["pubyear"] = get_year(get_data("prism:coverDate", input_data))
      output_data["data"]["sourcetitle"] = get_data("prism:publicationName", input_data)
      output_data["data"]["issn"] = format_issn(get_data("prism:issn", input_data))
      output_data["data"]["eissn"] = format_issn(get_data("prism:eIssn", input_data))
      output_data["data"]["isbn"] = get_isbn(get_data("prism:isbn", input_data))
      output_data["data"]["sourcevolume"] = get_data("prism:volume", input_data)
      output_data["data"]["sourceissue"] = get_data("prism:issueIdentifier", input_data)
      output_data["data"]["sourcepages"] = get_data("prism:pageRange", input_data)
      output_data["data"]["article_number"] = get_data("article-number", input_data)
      output_data["data"]["abstract"] = get_data("dc:description", input_data)
      output_data["data"]["keywords"] = format_keywords(get_data("authkeywords", input_data))
      output_data["data"]["publication_identifiers"] = create_publication_identifiers(input_data)
      output_data["data"]["authors"] = create_authors(input_data)
      output_data["data"]["created_at"] = get_data("orig-load-date", input_data)
      output_data["data"]["updated_at"] = get_data("orig-load-date", input_data)

      output_data["data"]["source"] = "scopus"
      

      if not os.path.exists(f"{args.dest_base_path}"):
        os.makedirs(f"{args.dest_base_path}")
        print(f"{args.dest_base_path}" + " directory doesn't exist, create it")

      with open(f"{args.dest_base_path}/{scopus_id}-normalised.json", 'w') as output_file:
        json.dump(output_data, output_file)
