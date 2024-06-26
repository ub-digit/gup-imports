import json
import argparse
import os
import sys
from datetime import datetime

def get_data(key, data):
  if data is None:
    return None
  if key in data:
    return data[key]
  else:
    return None

def exclude_document(type):
  if type == "correction" or type == "correction, addition" or type == "retracted publication":
    return True
  else:
    return False

def get_publication_type(input_data):

  print("Wos ID: " + str(wos_id))
  source_type  = get_data('pubtype', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))
  #print("Source Type: " + source_type)
  document_type = ""
  doctypes = get_data('doctypes', get_data('summary', get_data('static_data', input_data)))
  count = get_data('count', doctypes)
  if count == 1:
    document_type = get_data('doctype', doctypes)
  else:
    for doctype in get_data('doctype', doctypes):
      if doctype != "Early Access":
        if document_type == "Article" and doctype == "Proceedings Paper":
          document_type = "Article"
        else:
          document_type = doctype
  #print("Document Type: " + document_type)
  if source_type is None:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}
  if document_type is None:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}

  source_type	= source_type.lower()
  document_type = document_type.lower()

  if exclude_document(document_type):
    return None

  if source_type == "journal" and document_type == "article": 
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "review (article)": 
    return {"id": 22, "ref_value": "ISREF", "label": "Forskningsöversiktsartikel (Review article)"}
  elif source_type == "journal" and document_type == "review":
    return {"id": 22, "ref_value": "ISREF", "label": "Forskningsöversiktsartikel (Review article)"}
  elif source_type == "journal" and document_type == "proceeding paper": 
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "editorial material": 
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "journal" and document_type == "data paper": 
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "letter": 
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "journal" and document_type == "book review": 
    return {"id": 18, "ref_value": "NA", "label": "Recension"}
  elif source_type == "journal" and document_type == "note": 
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif source_type == "book" and document_type == "book chapter": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "book chapter": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book" and document_type == "meeting abstract": 
    return {"id": 1, "ref_value": "NOTREF", "label": "Konferensbidrag (offentliggjort, men ej förlagsutgivet)"}
  elif source_type == "book series" and document_type == "meeting abstract": 
    return {"id": 1, "ref_value": "NOTREF", "label": "Konferensbidrag (offentliggjort, men ej förlagsutgivet)"}
  elif source_type == "journal" and document_type == "meeting abstract":
    return {"id": 1, "ref_value": "NOTREF", "label": "Konferensbidrag (offentliggjort, men ej förlagsutgivet)"}
  elif source_type == "book" and document_type == "editorial material": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "editorial material": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book" and document_type == "letter": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "letter": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book" and document_type == "note": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book series" and document_type == "note": 
    return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif source_type == "book" and document_type == "proceeding paper": 
    return {"id": 2, "ref_value": "ISREF", "label": "Paper i proceeding"}
  elif source_type == "book series" and document_type == "proceeding paper": 
    return {"id": 2, "ref_value": "ISREF", "label": "Paper i proceeding"}
  else:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}

def get_wos_id(input_data):
  return get_data("UID", input_data).replace("WOS:", "")

def get_title(input_data):
  for title in input_data:
    if title['type'] == "item":
      return title['content']

def get_published_in(input_data):
  titles = {}
  titles = get_data('title', get_data('titles', get_data('summary', get_data('static_data', input_data))))
  for title in titles:
      if get_data('type', title) == "source":
         output_data["data"]["sourcetitle"] = get_data('content', title)
  sourcevolume = get_data('vol', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))
  sourceissue = get_data('issue', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))
  if sourcevolume is not None:
    sourcevolume = str(sourcevolume)
  if sourceissue is not None:
    sourceissue = str(sourceissue)
  output_data["data"]["sourcevolume"] = sourcevolume
  output_data["data"]["sourceissue"] = sourceissue
  output_data["data"]["sourcepages"] = get_data('content', get_data('page', get_data('pub_info', get_data('summary', get_data('static_data', input_data)))))
  return


def get_abstract(input_data):
  if input_data is None or input_data.get('p') is None:
    print("No abstract for this document")
    return None
  else:
    count = get_data('count', input_data)
    if count == 1:
      return(input_data['p'])
    else:
      # return all elemtns in the list as a single string separated by a \n\n
      return "\n\n".join(input_data['p'])

def format_keywords(keywords):
  if keywords is None:
    return None
  else:
    # A keyword may be represented as an integer in the data
    keywords = [str(k) for k in keywords]
    return ", ".join(keywords)

def create_publication_identifier_entry(code, value):
  return {"identifier_code": code,  "identifier_value": value}

def create_publication_identifiers(wos_id, input_data):
  identifiers = []
  identifiers.append(create_publication_identifier_entry('isi-id', wos_id))
  # If there are just 1 indentifier, it is not in a list
  if isinstance(input_data, dict):
    input_data = [input_data]
  for id in input_data:
    if id['type'] == "doi":
      identifiers.append(create_publication_identifier_entry('doi', id['value']))
    elif id['type'] == "pmid":
      identifiers.append(create_publication_identifier_entry('pubmed', id['value'].split(':')[-1]))
    elif id['type'] == "issn":
      output_data["data"]['issn'] = id['value']
    elif id['type'] == "eissn":
      output_data["data"]['eissn'] = id['value']
    elif id['type'] == "isbn":
      output_data["data"]['isbn'] = id['value']
    elif id['type'] == "art_no":
      output_data["data"]['article_number'] = id['value'].replace("ARTN ", "")

  return identifiers

def create_person_identifier_entry(type, value):
  return {"type": type,  "value": value}

def create_person_identifiers(input_data):
  identifiers = []
  # orcid
  orcid_id_value = get_data("orcid_id", input_data)
  if orcid_id_value is not None:
    identifiers.append(create_person_identifier_entry("orcid", orcid_id_value))
  # researcher-id
  researcher_id_value = get_data("r_id", input_data)
  if researcher_id_value is not None:
    identifiers.append(create_person_identifier_entry("wos-researcher-id", researcher_id_value))
  # daisng-id (internal id for the author in the WOS database)
  daisng_id_value = get_data("daisng_id", input_data)
  if daisng_id_value is not None:
    identifiers.append(create_person_identifier_entry("wos-daisng-id", str(daisng_id_value)))
  return identifiers

def create_authors(input_data):
  authors = []
  count = get_data('count', get_data('names', input_data))
  if count == 1:
    persons = [get_data('name', get_data('names', input_data))]
  else:
    persons = get_data('name', get_data('names', input_data))
  for individual in persons:
    person = {}
    affiliation = {}
    if (individual.get('first_name') is None) or (individual.get('last_name') is None):
      print("First or last name is missing for seq no " + str(individual['seq_no']) + " for this document, skipping this entry")
      continue
    person['position'] = individual['seq_no']
    person['first_name'] = individual['first_name']
    person['last_name'] = individual['last_name']
    person["identifiers"] = create_person_identifiers(individual)
    authors.append({"affiliation": [affiliation], "person": [person]})

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
    wos_id = get_wos_id(input_data)
    publication_type = get_publication_type(input_data)
    if publication_type is None:
      print("No publication type mapping for wos id: " + wos_id)
      continue
    output_data = {"data": {}}
    output_data["data"]["id"] = "WOS_" + wos_id
    output_data["data"]["publication_type_id"] = publication_type["id"]
    output_data["data"]["publication_type_label"] = publication_type["label"]
    output_data["data"]["ref_value"] = publication_type["ref_value"]
    output_data["data"]["title"] = get_title(get_data('title', get_data('titles', get_data('summary', get_data('static_data', input_data)))))
    output_data["data"]["pubyear"] = str(get_data('pubyear', get_data('pub_info', get_data('summary', get_data('static_data', input_data)))))

    get_published_in(input_data)

    first_publisher = ""
    publishers = get_data('names', get_data('publisher', get_data('publishers', get_data('summary', get_data('static_data', input_data)))))
    count = get_data('count', publishers)
    if count == 1:
      first_publisher = get_data('display_name', get_data('name', publishers))
    output_data["data"]["publisher"] = first_publisher

    output_data["data"]["keywords"] = format_keywords(get_data('keyword', get_data('keywords', get_data('fullrecord_metadata', get_data('static_data', input_data)))))
    output_data["data"]["language"] = get_data('content', get_data('language', get_data('languages', get_data('fullrecord_metadata', get_data('static_data', input_data)))))

    output_data["data"]["publication_identifiers"] = create_publication_identifiers(wos_id, get_data('identifier', get_data('identifiers', get_data('cluster_related', get_data('dynamic_data', input_data)))))

    if (get_data('has_abstract', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))) == "Y":
      output_data["data"]["abstract"] = get_abstract(get_data('abstract_text', get_data('abstract', get_data('abstracts', get_data('fullrecord_metadata', get_data('static_data', input_data))))))

    output_data["data"]["authors"] = create_authors(get_data('summary', get_data('static_data', input_data)))

    output_data["data"]["source"] = "wos"

    load_date = get_data('date_loaded', get_data('dates', input_data))
    load_date = datetime.strptime(load_date, '%Y-%m-%dT%H:%M:%S.%f')
    output_data["data"]["created_at"] = load_date.strftime('%Y-%m-%dT%H:%M:%S')
    output_data["data"]["updated_at"] = load_date.strftime('%Y-%m-%dT%H:%M:%S')


    if not os.path.exists(f"{args.dest_base_path}"):
      os.makedirs(f"{args.dest_base_path}")
      print(f"{args.dest_base_path}" + " directory doesn't exist, create it")

    with open(f"{args.dest_base_path}/{wos_id}-normalised.json", 'w') as output_file:
      json.dump(output_data, output_file)
