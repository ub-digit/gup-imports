import requests
import sys
import os
import argparse
from datetime import datetime
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch
from lxml import etree


def get_identifiers(root):
    # Get all identifier elements from the xml and return a list of their text values
    identifiers = []

    # Get the identifier elements with type "isi", "type" "doi", "type" "scopus", "type" "pubmed"
    for identifier in root.findall(".//{http://www.loc.gov/mods/v3}identifier"):
        identifier_type = identifier.get("type")
        if identifier_type == "isi":
            identifiers.append("isi-id:" + identifier.text)
        elif identifier_type == "doi":
            identifiers.append("doi:" + identifier.text)
        elif identifier_type == "scopus":
            identifiers.append("scopus-id:" + identifier.text)
        elif identifier_type == "pubmed":
            identifiers.append("pubmed:" + identifier.text)

    return identifiers

def check_already_exists(identifiers, api_key):
    base_url = 'https://gup-admin.ub.gu.se/index-manager/publications/check_identifiers/'
    params = {'identifiers': identifiers, 'api_key': api_key}
    try:
        response = requests.get(base_url, params)
        if response.status_code == 200:
            #JSON response example of response.content:
            # b'{"result":true,"status":"ok"}'
            result = response.json()
            if result["status"] == "ok":
                return result["result"]
            else:
                print("Error checking if document already exists: " + str(result))
                sys.exit()
        else:
        # If there is an error, print the error and interrupt the entire process
            print("Error checking if document already exists: " + str(response.status_code))
            sys.exit()
    except Exception as e:
        # If there is an error, print the error and interrupt the entire process
        print("Error checking if document already exists: " + str(e))
        sys.exit()


base_url = 'https://libris.kb.se/swepub/oaipmh/SWEPUB'

parser = argparse.ArgumentParser()
# Api key for Gup Admin
parser.add_argument("-a", "--apikey", dest = "apikey", required = True)
parser.add_argument("-d", "--date", dest = "date", default = datetime.now().date().strftime('%Y-%m-%d'))
parser.add_argument("-o", "--output", dest = "output", default = ".")
args = parser.parse_args()

params = {'metadataPrefix': 'swepub_mods','from': args.date, 'until': args.date, 'set': 'CTH_SWEPUB'}

print ("Date: " + args.date)
sickle = Sickle(base_url)
try:
    records = sickle.ListRecords(**params)
# If sickle.oaiexceptions.NoRecordsMatch exception is raised, print "No documents found" and exit
except NoRecordsMatch:
    print("No documents found")
    sys.exit()

affiliation_authority = "https://ror.org/040wg7k59" # CTH
affiliation_values = ["o6E7KL6_wZLdLD-YBOVgbA", "fufFiZUZuZmpRyw9dKjPGg"] # Department of Mathematical Sciences, Department of Computer Science and Engineering

if not os.path.exists(f"{args.output}/{args.date}"):
    os.makedirs(f"{args.output}/{args.date}")
    print(f"{args.output}/{args.date}" + " directory doesn't exist, create it")

identifier_prefix = "https://research.chalmers.se/publication/"
start_year = 2020
for record in records:
    xml = record.raw
    root = etree.fromstring(xml)
    
    # Check if affiliation authority attribute has the same value as affiliation_authority and valueURI attribute is in affiliation_values, if not ignore this document
    # It can be found in <record><metadata><mods><name type="personal">
    affiliation = root.find(".//{http://www.loc.gov/mods/v3}name[@type='personal']/{http://www.loc.gov/mods/v3}affiliation[@authority='" + affiliation_authority + "']")
    if affiliation is not None and affiliation.get("valueURI") in affiliation_values:
        # Get the identifier from the xml
        # The identifier can be found in <record><metadata><mods><identifier type="uri"> nd must not contain attribute invalid="yes"
        # Check that the value starts with the identifier_prefix and use the part after that as the file name
        uris = [
            el for el in root.findall(".//{http://www.loc.gov/mods/v3}identifier[@type='uri']")
            if el.get("invalid") != "yes"
        ]
        # assume that there is only one identifier element with type "uri" and without attribute invalid="yes", if there are more than one, print "Multiple valid identifier elements found, ignoring document" and ignore this document
        if len(uris) > 1:
            print("Multiple valid identifier elements found, ignoring document")
            continue
        identifier = uris[0] if uris else None

        if identifier is not None and identifier.text.startswith(identifier_prefix):
            cth_research_id = identifier.text.split(identifier_prefix)[1]
            # Based on the identifier, check if the document with the same identifier already exists in Gup Admin, if it does, ignore this document
            identifiers = get_identifiers(root)
            print("Identifiers for document with CTH Research ID " + cth_research_id + ": " + str(identifiers))
            # Check only if identifiers list is not empty, if it is empty, ignore the check and save the document anyway
            if identifiers and check_already_exists(identifiers, args.apikey):
                print("Document with identifier " + cth_research_id + " already exists in Gup Admin, ignoring")
                continue
            # Check if the publication date is before 2020, if it is ignore this document
            # The date can be found in <record><metadata><mods><originInfo><dateIssued>
            date_issued = root.find(".//{http://www.loc.gov/mods/v3}originInfo/{http://www.loc.gov/mods/v3}dateIssued")
            if date_issued is not None and int(date_issued.text.split("-")[0]) < start_year:
                print("Document with identifier " + cth_research_id + " has a publication date before " + str(start_year) + ", ignoring")
                continue
            # Save the document as an xml file with the name of the identifier in the output directory
            with open(f"{args.output}/{args.date}/{cth_research_id}.xml", 'wb') as output_file:
                output_file.write(etree.tostring(root))
            print("Document with identifier " + cth_research_id + " saved")
