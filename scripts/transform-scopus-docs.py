import json
import argparse
import os
import sys

def get_key(key, data):
  if key in input_data: 
    return input_data[key]
  else:
    return None

def get_publication_type_id(input_data):
  source_type	= get_key("prism:aggregationType", input_data).lower()
  document_type = get_key("subtypeDescription", input_data).lower()
  
  if source_type == "journal" and document_type == "article":
    return 5 # Artikel i vetenskaplig tidskrift
  elif source_type == "journal" and document_type == "conference paper":
    return 5 # Artikel i vetenskaplig tidskrift
  elif source_type == "journal" and document_type == "review":
    return 22 # Forskningsöversiktsartikel (Review article)
  elif source_type == "journal" and document_type == "editorial":
    return 40 # Inledande text i tidskrift
  elif source_type == "journal" and document_type == "letter":
    return 40 # Inledande text i tidskrift
  elif source_type == "journal" and document_type == "note":
    return 40 # Inledande text i tidskrift
  elif source_type == "journal" and document_type == "short survey":
    return 40 # Inledande text i tidskrift
  elif source_type == "book" and document_type == "book chapter":
    return 10 # Kapitel i bok
  elif source_type == "conference proceeding" and document_type == "conference paper":
    return 2 # Paper i proceeding
  elif source_type == "book series" and document_type == "book chapter":
    return 10 # Kapitel i bok
  elif source_type == "book" and document_type == "book":
    return 9 # Bok
  elif source_type == "book series" and document_type == "book":
    return 9 # Bok
  elif source_type == "book" and document_type == "editorial":
    return 10 # Kapitel i bok
  elif source_type == "conference proceeding" and document_type == "editorial":
    return 1 # Konferensbidrag (offentliggjort, men ej förlagsutgivet)
  elif source_type == "conference proceeding" and document_type == "book chapter":
    return 2 # Paper i proceeding
  elif source_type == "book series" and document_type == "conference paper":
    return 10 # Kapitel i bok
  elif source_type == "book series" and document_type == "article":
    return 10 # Kapitel i bok
  elif source_type == "book series" and document_type == "review":
    return 10 # Kapitel i bok
  elif source_type == "book series" and document_type == "note":
    return 10 # Kapitel i bok
  else:
    return None

def get_year(date):
  # Assumeing yyyy-mm-dd format
  return date[:4]

def get_scopus_id(input_data):
  return get_key("dc:identifier", input_data).replace("SCOPUS_ID:", "")

def format_keywords(keywords):
  if keywords is None:
    return None
  else:
    return ", ".join(keywords.split(" | "))

def create_identifier_entry(code, value):
  return {"identifier_code": code,  "identifier_value": value}

def create_identifiers(input_data):
  identifiers = []
  # scopus
  scopus_value = get_scopus_id(input_data)
  identifiers.append(create_identifier_entry("scopus-id", scopus_value))
  # doi
  doi_value = get_key("prism:doi", input_data)
  if doi_value is not None:
    identifiers.append(create_identifier_entry("doi", doi_value))
  # pubmed
  pubmed_value = get_key("prism:pubmed-id", input_data)
  if pubmed_value is not None:
    identifiers.append(create_identifier_entry("pubmed", pubmed_value))
  return identifiers

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

      publication_type_id = get_publication_type_id(input_data)
      if publication_type_id is None:
        print("No publication type mapping for scopus id: " + scopus_id)
        continue
      output_data = {"data": {}}
      output_data["data"]["id"] = "scopus_" + scopus_id
      output_data["data"]["publication_type_id"] = publication_type_id
      output_data["data"]["title"] = get_key("dc:title", input_data)
      output_data["data"]["pubyear"] = get_year(get_key("prism:coverDate", input_data))
      output_data["data"]["sourcetitle"] = get_key("prism:publicationName", input_data)
      output_data["data"]["issn"] = get_key("prism:issn", input_data)
      output_data["data"]["eissn"] = get_key("prism:eissn", input_data)
      output_data["data"]["sourcevolume"] = get_key("prism:volume", input_data)
      output_data["data"]["sourceissue"] = get_key("prism:issueIdentifier", input_data)
      output_data["data"]["sourcepages"] = get_key("prism:pageRange", input_data)
      output_data["data"]["articlenumber"] = get_key("article-number", input_data)
      output_data["data"]["abstract"] = get_key("dc:description", input_data)
      output_data["data"]["keywords"] = format_keywords(get_key("authkeywords", input_data))
      output_data["data"]["publication_identifiers"] = create_identifiers(input_data)

      output_data["data"]["source"] = "scopus"
      output_data["data"]["attended"] = False
      

      if not os.path.exists(f"{args.dest_base_path}"):
        os.makedirs(f"{args.dest_base_path}")
        print(f"{args.dest_base_path}" + " directory doesn't exist, create it")

      with open(f"{args.dest_base_path}/{scopus_id}-normalised.json", 'w') as output_file:
        json.dump(output_data, output_file)
