import json
from pkgutil import get_data
from lxml import etree
import argparse
import os
import sys


def get_publication_type(input_data):
  # Get the output type and content type from the xml elements:
  #<genre authority="kb.se" type="outputType" valueURI="https://id.kb.se/term/swepub/output/publication/journal-article">VALUE</genre>
  #<genre authority="svep" type="contentType" valueURI="https://id.kb.se/term/swepub/svep/ref">VALUE</genre>

  output_type = input_data.find(".//{http://www.loc.gov/mods/v3}genre[@authority='kb.se'][@type='outputType']")
  content_type = input_data.find(".//{http://www.loc.gov/mods/v3}genre[@authority='svep'][@type='contentType']")
  print("Output type: " + output_type.text if output_type is not None else "None")
  print("Content type: " + content_type.text if content_type is not None else "None")
  if output_type is None or content_type is None:
    # This should not happen, but if it does, return None
    return None
  elif output_type.text == "conference/other":
    return {"id": 1, "ref_value": "NOTREF", "label": "Konferensbidrag (offentliggjort, men ej förlagsutgivet)"}
  elif output_type.text == "conference/paper":
    return {"id": 2, "ref_value": "ISREF", "label": "Paper i proceeding"}
  elif output_type.text == "conference/poster":
    return {"id": 3, "ref_value": "NOTREF", "label": "Poster (konferens)"}
  elif output_type.text == "publication/journal-article":
    return {"id": 5, "ref_value": "ISREF", "label": "Artikel i vetenskaplig tidskrift"}
  elif output_type.text == "publication/magazine-article":
    return {"id": 7, "ref_value": "NOTREF", "label": "Artikel i övriga tidskrifter"}
  elif output_type.text == "publication/edited-book":
    if content_type.text == "ref":
      return {"id": 8, "ref_value": "ISREF", "label": "Samlingsverk (red.)"}
    else:
      return {"id": 8, "ref_value": "NOTREF", "label": "Samlingsverk (red.)"}
  elif output_type.text == "publication/book":
    if content_type.text == "ref":
      return {"id": 9, "ref_value": "ISREF", "label": "Bok"}
    else:
      return {"id": 9, "ref_value": "NOTREF", "label": "Bok"}
  elif output_type.text == "publication/book-chapter":
    if content_type.text == "ref":
      return {"id": 10, "ref_value": "ISREF", "label": "Kapitel i bok"}
    else:
      return {"id": 10, "ref_value": "NOTREF", "label": "Kapitel i bok"}
  elif output_type.text == "intellectual-property/patent":
    return {"id": 13, "ref_value": "NOTREF", "label": "Patent"}
  elif output_type.text == "publication/report":
    return {"id": 16, "ref_value": "NOTREF", "label": "Rapport"}
  elif output_type.text == "publication/doctoral-thesis":
    return {"id": 17, "ref_value": "NOTREF", "label": "Doktorsavhandling"}
  elif output_type.text == "publication/book-review":
    return {"id": 18, "ref_value": "NA", "label": "Bokrecension"}
  elif output_type.text == "publication/licentiate-thesis":
    return {"id": 19, "ref_value": "NOTREF", "label": "Licentiatavhandling"}
  elif output_type.text == "publication/other":
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}
  elif output_type.text == "publication/review-article":
    return {"id": 22, "ref_value": "ISREF", "label": "Forskningsöversiktsartikel (Review article)"}
  elif output_type.text == "publication/critical-edition":
    return {"id": 28, "ref_value": "NOTREF", "label": "Textkritisk utgåva"}
  elif output_type.text == "publication/editorial-letter":
    return {"id": 40, "ref_value": "NOTREF", "label": "Inledande text i tidskrift"}
  elif output_type.text == "publication/report-chapter":
    return {"id": 41, "ref_value": "NOTREF", "label": "Kapitel i rapport"}
  elif output_type.text == "publication/newspaper-article":
    return {"id": 42, "ref_value": "NA", "label": "Artikel i dagspress"}
  elif output_type.text == "publication/encyclopedia-entry":
    if content_type.text == "ref":
      return {"id": 43, "ref_value": "ISREF", "label": "Bidrag till encyklopedi"}
    else:
      return {"id": 43, "ref_value": "NOTREF", "label": "Bidrag till encyklopedi"}
  elif output_type.text == "publication/journal-issue":
    return {"id": 44, "ref_value": "NA", "label": "Special / temanummer av tidskrift (red.)"}
  elif output_type.text == "conference/proceeding":
    if content_type.text == "ref":
      return {"id": 45, "ref_value": "ISREF", "label": "Proceeding (red.)"}
    else:
      return {"id": 45, "ref_value": "NOTREF", "label": "Proceeding (red.)"}
  elif output_type.text == "publication/working-paper":
    return {"id": 47, "ref_value": "NA", "label": "Working paper"}
  else:
    return {"id": 21, "ref_value": "NA", "label": "Annan publikation"}

def get_data(key, data):
  if data is None:
    return None
  xpath = key.replace("mods:", "{http://www.loc.gov/mods/v3}")
  element = data.find(".//" + xpath)
  if element is not None:
    return element.text
  else:
    return None

def get_data_elements(key, data):
  if data is None:
    return None
  xpath = key.replace("mods:", "{http://www.loc.gov/mods/v3}")
  print("Getting data elements with xpath: " + xpath)
  elements = data.findall(".//" + xpath)
  if elements:
    return elements
  else:
    return None

def get_sourcepages(data):
  # Get the source pages from the extent xml element:
  extent = data.find(".//{http://www.loc.gov/mods/v3}part/{http://www.loc.gov/mods/v3}extent")
  if extent is None:
    return None
  start = extent.find(".//{http://www.loc.gov/mods/v3}start")
  end = extent.find(".//{http://www.loc.gov/mods/v3}end")
  if start is not None and end is not None:
    return start.text + "-" + end.text
  elif start is not None:
    return start.text
  else:
    return None

def get_related_item_info(data):
  # There can be multiple relatedItem elements with type "host".
  # Filter always out those with an element <genre>project</genre>
  # If there is an element <genre>event</genre> set pub_notes to <titleInfo><title></title></titleInfo> from that element
  # If there is and elenent without genre project or event, use that one to get the related item info
  sourcetitle = None
  issn = None
  eissn = None
  isbn = None
  sourcevolume = None
  sourceissue = None
  article_number = None
  sourcepages = None
  pub_notes = None

  related_items = data.findall(".//{http://www.loc.gov/mods/v3}relatedItem[@type='host']")
  for related_item in related_items:
    genre = related_item.find(".//{http://www.loc.gov/mods/v3}genre")
    if genre is not None and genre.text == "project":
      continue
    elif genre is not None and genre.text == "event":
      pub_notes = get_data("mods:titleInfo/mods:title", related_item)
    else:
      sourcetitle = get_data("mods:titleInfo/mods:title", related_item)
      issn = get_data("mods:identifier[@type='issn']", related_item)
      eissn = get_data("mods:identifier[@type='eissn']", related_item)
      isbn = get_isbn(related_item)
      sourcevolume = get_data("mods:part/mods:detail[@type='volume']/mods:number", related_item)
      sourceissue = get_data("mods:part/mods:detail[@type='issue']/mods:number", related_item)
      article_number = get_data("mods:part/mods:detail[@type='article-number']/mods:number", related_item)
      sourcepages = get_sourcepages(related_item)
  return {"sourcetitle": sourcetitle, "issn": issn, "eissn": eissn, "isbn": isbn, "sourcevolume": sourcevolume, "sourceissue": sourceissue, "article_number": article_number, "sourcepages": sourcepages, "pub_notes": pub_notes}

def format_keywords(data):
  if data is None:
    return None
  keywords = []
  for topic in data:
    keywords.append(topic.text)
  return ", ".join(keywords)

def create_publication_identifiers(data, cth_research_id):
  identifiers = []

  # Get the identifier elements with type "isi", "type" "doi", "type" "scopus", "type" "pubmed"
  for identifier in data.findall(".//{http://www.loc.gov/mods/v3}identifier"):
    identifier_type = identifier.get("type")
    if identifier_type == "isi":
      identifiers.append({"identifier_code": "isi-id",  "identifier_value": identifier.text})
    elif identifier_type == "doi":
      identifiers.append({"identifier_code": "doi",  "identifier_value": identifier.text})
    elif identifier_type == "scopus":
      identifiers.append({"identifier_code": "scopus-id",  "identifier_value": identifier.text})
    elif identifier_type == "pubmed":
      identifiers.append({"identifier_code": "pubmed",  "identifier_value": identifier.text})

  return identifiers

def get_isbn(data):
  isbn = data.find(".//{http://www.loc.gov/mods/v3}identifier[@type='isbn']")
  if isbn is not None:
    return isbn.text
  else:
    return None

def create_authors(data):
  authors = []
  index = 1
  for name in data.findall(".//{http://www.loc.gov/mods/v3}name[@type='personal']"):
    author = {}
    position = str(index)
    first_name = name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='given']").text if name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='given']") is not None else None
    last_name = name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='family']").text if name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='family']") is not None else None
    year_of_birth = name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='date']").text if name.find(".//{http://www.loc.gov/mods/v3}namePart[@type='date']") is not None else None
    orcid = name.find(".//{http://www.loc.gov/mods/v3}nameIdentifier[@type='orcid']").text if name.find(".//{http://www.loc.gov/mods/v3}nameIdentifier[@type='orcid']") is not None else None
    cid = name.find(".//{http://www.loc.gov/mods/v3}nameIdentifier[@type='cth']").text if name.find(".//{http://www.loc.gov/mods/v3}nameIdentifier[@type='cth']") is not None else None
    person = {"position": position, "first_name": first_name, "last_name": last_name, "year_of_birth": year_of_birth}

    person["identifiers"] = []
    if orcid is not None:
      person["identifiers"].append({"type": "orcid", "value": orcid})
    if cid is not None:
      person["identifiers"].append({"type": "cid", "value": cid})
    author["person"] = [person]


    affiliations = []
    for affiliation in name.findall(".//{http://www.loc.gov/mods/v3}affiliation"):
      affiliations.append({"affiliation_name": affiliation.text, "affiliation_lang": affiliation.get("lang"), "affiliation_authority": affiliation.get("authority"), "affiliation_valueURI": affiliation.get("valueURI")})
    author["affiliations"] = affiliations
    authors.append(author)
    index += 1
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
    # The file is in xml format, read it and convert to json
    xml = input_file.read()
    data = etree.fromstring(xml)

    # Get the cth_researcher_id from the file name, which is in the format "cth_researcher_id.xml"
    cth_research_id = file_name.split(".xml")[0]

    publication_type = get_publication_type(data)
    if publication_type is None:
      print("No publication type mapping for swepub id: " + cth_research_id)
      continue

    output_data = {"data": {}}
    output_data["data"]["id"] = "chalmers_" + cth_research_id
    output_data["data"]["publication_type_id"] = publication_type["id"]
    output_data["data"]["publication_type_label"] = publication_type["label"]
    output_data["data"]["ref_value"] = publication_type["ref_value"]
    output_data["data"]["title"] = get_data("mods:titleInfo/mods:title", data)
    output_data["data"]["alt_title"] = get_data("mods:titleInfo/mods:subTitle", data)
    output_data["data"]["pubyear"] = get_data("mods:originInfo/mods:dateIssued", data)

    related_item_info = get_related_item_info(data)
    output_data["data"]["sourcetitle"] = related_item_info["sourcetitle"]
    output_data["data"]["issn"] = related_item_info["issn"]
    output_data["data"]["eissn"] = related_item_info["eissn"]
    output_data["data"]["isbn"] = related_item_info["isbn"]
    # If isbn is None from related item, try to get it from the identifier with type isbn in the main record
    if related_item_info["isbn"] is None:
      related_item_info["isbn"] = get_isbn(data)
    output_data["data"]["sourcevolume"] = related_item_info["sourcevolume"]
    output_data["data"]["sourceissue"] = related_item_info["sourceissue"]
    output_data["data"]["sourcepages"] = related_item_info["sourcepages"]
    output_data["data"]["article_number"] = related_item_info["article_number"]
    output_data["data"]["pub_notes"] = related_item_info["pub_notes"]
    output_data["data"]["abstract"] = get_data("mods:abstract", data)
    output_data["data"]["keywords"] = format_keywords(get_data_elements("mods:subject/mods:topic", data))
    output_data["data"]["publication_identifiers"] = create_publication_identifiers(data, cth_research_id)
    output_data["data"]["authors"] = create_authors(data)
    output_data["data"]["publisher"] = get_data("mods:originInfo/mods:agent", data)
    output_data["data"]["place"] = get_data("mods:originInfo/mods:place/mods:placeTerm", data)
    output_data["data"]["language"] = get_data("mods:language/mods:languageTerm[@type='code']", data)
    # Use datestamp from header as created_at and updated_at
    output_data["data"]["created_at"] = data.find(".//{http://www.openarchives.org/OAI/2.0/}header/{http://www.openarchives.org/OAI/2.0/}datestamp").text
    output_data["data"]["updated_at"] = data.find(".//{http://www.openarchives.org/OAI/2.0/}header/{http://www.openarchives.org/OAI/2.0/}datestamp").text

    output_data["data"]["source"] = "chalmers"


    if not os.path.exists(f"{args.dest_base_path}"):
      os.makedirs(f"{args.dest_base_path}")
      print(f"{args.dest_base_path}" + " directory doesn't exist, create it")

    with open(f"{args.dest_base_path}/{cth_research_id}-normalised.json", 'w') as output_file:
      json.dump(output_data, output_file)




