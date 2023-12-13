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

def get_publication_type(input_data):

  #print("Wos ID: " + str(wos_id))
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
        document_type = doctype
  #print("Document Type: " + document_type)
  if source_type is None:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}
  if document_type is None:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}

  source_type	= source_type.lower()
  document_type = document_type.lower()

  if source_type == "journal" and document_type == "article": 
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif source_type == "journal" and document_type == "review article": 
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
  output_data["data"]["sourcevolume"] = get_data('vol', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))
  output_data["data"]["sourceissue"] = get_data('issue', get_data('pub_info', get_data('summary', get_data('static_data', input_data))))
  output_data["data"]["sourcepages"] = get_data('content', get_data('page', get_data('pub_info', get_data('summary', get_data('static_data', input_data)))))
  return


def get_abstract(input_data):
  return(input_data['p'])

def format_keywords(keywords):
  if keywords is None:
    return None
  else:
    return ", ".join(keywords)

def create_publication_identifier_entry(code, value):
  return {"identifier_code": code,  "identifier_value": value}

def create_publication_identifiers(wos_id, input_data):
  identifiers = []
  identifiers.append(create_publication_identifier_entry('isi-id', wos_id))
  for id in input_data:
    if id['type'] == "doi":
      identifiers.append(create_publication_identifier_entry('doi', id['value']))
    elif id['type'] == "pmid":
      identifiers.append(create_publication_identifier_entry('pubmed', id['value']))
    elif id['type'] == "issn":
      output_data["data"]['issn'] = id['value']
    elif id['type'] == "eissn":
      output_data["data"]['eissn'] = id['value']
    elif id['type'] == "isbn":
      output_data["data"]['isbn'] = id['value']
    elif id['type'] == "art_no":
      output_data["data"]['art_no'] = id['value'].replace("ARTN ", "")

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
    person['position'] = individual['seq_no']
    person['first_name'] = individual['first_name']
    person['last_name'] = individual['last_name']
    authors.append({"person": person, "affiliation": affiliation })

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
    try:
      input_data = json.load(input_file)
      wos_id = get_wos_id(input_data)
      publication_type = get_publication_type(input_data)
      if publication_type is None:
        print("No publication type mapping for wos id: " + wos_id)
        continue
      output_data = {"data": {}}
      output_data["data"]["id"] = "WOS_" + wos_id
      output_data["data"]["publication_type_id"] = str(publication_type["id"])
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

    except TypeError:
      print("TypeError: " + wos_id)      # XMAGNN
      continue
