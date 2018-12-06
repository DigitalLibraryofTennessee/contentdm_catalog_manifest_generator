import argparse
from lxml import etree
import json
import xmltodict
import requests
import yaml
from tqdm import tqdm
import urllib3

config = yaml.load(open("sets.yml", "r"))


class ManifestGenerator:
    def __init__(self, url):
        self.url = self.convert_object_in_context(url)
        self.status_code = 400

    def convert_object_in_context(self, url):
        x = url.split("/")
        if x[3] != "digital":
            x = self.convert_old_url_formatting(url)
        try:
            return f"https://{x[2]}/digital/iiif/{x[5]}/{x[7]}/info.json"
        except IndexError:
            return "badrequest"
        except requests.exceptions.SSLError:
            return "badrequest"

    def fetch_manifest(self):
        if self.url != "badrequest":
            r = requests.get(self.url, verify=False)
            self.status_code = r.status_code
        else:
            self.status_code = 404
        return

    @staticmethod
    def convert_old_url_formatting(current_url):
        return current_url.replace("/cdm/ref/", "/digital/").replace("/cdm/singleitem/", "/digital/").split("/")


class OAIRequest:
    def __init__(self, endpoint, oai_set="p16877coll2", prefix="oai_dc"):
        self.oai_base = endpoint
        self.endpoint = self.set_endpoint(endpoint, oai_set, prefix)
        self.token = ""
        self.manifested_records = []
        self.metadata_prefix = prefix
        self.metadata_key = self.set_metadata_key(prefix)
        self.total_records = 0
        self.status = "In Progress"
        self.bad_records = 0
        self.good_records = 0
        self.set = oai_set

    @staticmethod
    def set_metadata_key(metadata_format):
        if metadata_format == "oai_dc":
            return "oai_dc:dc"
        elif metadata_format == "oai_qdc":
            return "oai_qdc:qualifieddc"

    @staticmethod
    def set_endpoint(our_endpoint, our_set, our_prefix):
        endpoint = f"{our_endpoint}?verb=ListRecords&metadataPrefix={our_prefix}"
        if our_set != "":
            endpoint = f"{endpoint}&set={our_set}"
        return endpoint

    @staticmethod
    def remove_bad_unicode(some_bytes):
        good_string = some_bytes.decode('utf-8')
        good_string = good_string.replace(u'\u000B', u'')
        good_string = good_string.replace(u'\u000C', u'')
        good_bytes = good_string.encode("utf-8")
        # Removed some old logging -- need to add this back in
        return good_bytes

    @staticmethod
    def remove_dots(an_object):
        for key in an_object.keys():
            new_key = key.replace(".", "DOT")
            if new_key != key:
                an_object[new_key] = an_object[key]
                del an_object[key]
        return an_object

    def read_list_records(self):
        r = requests.get(f"{self.endpoint}")
        clean = self.remove_bad_unicode(r.content)
        oai_document = etree.fromstring(clean)
        json_document = json.dumps(xmltodict.parse(clean))
        metadata_as_json = json.loads(json_document, object_hook=self.remove_dots)
        try:
            for record in metadata_as_json['OAI-PMH']['ListRecords']['record']:
                try:
                    if type(record["metadata"][self.metadata_key]["dc:identifier"]) is str:
                        x = ManifestGenerator(record["metadata"][self.metadata_key]["dc:identifier"])
                        self.total_records += 1
                        if x.status_code == 404:
                            self.bad_records += 1
                        elif x.status_code == 200:
                            self.good_records += 1
                            self.manifested_records.append(record["metadata"][self.metadata_key]["dc:identifier"])
                    elif type(record["metadata"][self.metadata_key]["dc:identifier"]) is list:
                        for identifier in record["metadata"][self.metadata_key]["dc:identifier"]:
                            if identifier.startswith("http"):
                                x = ManifestGenerator(identifier)
                                x.fetch_manifest()
                                if x.status_code == 404:
                                    self.bad_records += 1
                                elif x.status_code == 200:
                                    self.good_records += 1
                                    self.manifested_records.append(identifier)
                                else:
                                    print(x.status_code)
                                self.total_records += 1
                except KeyError as e:
                    self.write_error_to_log(f"{e}\n\t{record}\n")
        except KeyError as e:
            self.write_error_to_log(e)
        self.process_token(oai_document.findall('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken'))
        if self.status is not "Done":
            self.endpoint = f"{self.oai_base}?verb=ListRecords{self.token}"
            return self.read_list_records()
        else:
            return

    def log_success(self):
        with open("results.txt", "a") as logfile:
            logfile.write(f"SUCCESS: Reviewed {self.total_records} from {self.set}. \n")
            logfile.write(f"\tFound {self.good_records} records with manifests.\n")
            logfile.write(f"\tFound {self.bad_records} records without manifests.\n")
        return

    def process_token(self, token):
        if len(token) == 1:
            self.token = f'&resumptionToken={token[0].text}'
            return
        else:
            self.status = "Done"
            return

    @staticmethod
    def add_manifested_item_to_catalog(identifier):
        with open("catalog.xml", "a") as catalog:
            catalog.write(f"\t\t<item id='{identifier}'/>\n")
        return

    @staticmethod
    def write_error_to_log(message):
        with open("results.txt", "a") as logfile:
            logfile.write(f"ERROR: {message}\n")
        return


class RequestHandler:
    def __init__(self, endpoint, provider, metadata_format):
        self.metadata_format = metadata_format
        self.endpoint = endpoint
        self.provider = provider

    def make_muliple_oai_requests(self):
        with open("catalog.xml", "w") as catalog:
            catalog.write("<catalog>\n")
            for oai_set in tqdm(config[self.provider][self.metadata_format]):
                catalog.write(f"\t<set id='{oai_set}'>\n")
                x = OAIRequest(self.endpoint, oai_set, self.metadata_format)
                x.read_list_records()
                x.log_success()
                for record in x.manifested_records:
                    catalog.write(f"\t\t<item id='{record}'/>\n")
                catalog.write("\t</set>\n")
            catalog.write("</catalog>\n")
        return

    def make_single_oai_request(self, oai_set):
        with open("catalog.xml", "w") as catalog:
            catalog.write("<catalog>\n")
            catalog.write(f"\t<set id='{oai_set}'>\n")
            x = OAIRequest(self.endpoint, oai_set, self.metadata_format)
            x.read_list_records()
            x.log_success()
            for record in x.manifested_records:
                catalog.write(f"\t\t<item id='{record}'/>\n")
            catalog.write("\t</set>\n")
            catalog.write("</catalog>\n")
        return


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser(description='Generate Manifest from Object in Context')
    parser.add_argument("-p", "--provider", dest="provider", help="Specify provider", required=True)
    parser.add_argument("-m", "--metadata_format", dest="format", help="Specify metadata format", required=True)
    parser.add_argument("-o", "--operation", dest="operation", help="Specify multiple or single set request.  "
                                                                    "Multiple is default.",
                        required=False, default="multiple")
    parser.add_argument("-s", "--set", dest="set", help="If using single operation, use to specify set.",
                        required=False)
    args = parser.parse_args()
    if args.operation == "multiple":
        RequestHandler("https://dpla.lib.utk.edu/repox/OAIHandler", args.provider, args.format).make_muliple_oai_requests()
    elif args.operation == "single":
        RequestHandler("https://dpla.lib.utk.edu/repox/OAIHandler", args.provider,
                       args.format).make_single_oai_request(args.set)
    else:
        print("Operation not valid.\n")

