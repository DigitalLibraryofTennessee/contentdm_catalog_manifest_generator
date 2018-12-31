import requests
import json
import yaml
from repox.repox import Repox

settings = yaml.load(open("config.yml", "r"))


class DLTNDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(DLTNDumper, self).increase_indent(flow, False)


# Class Designed to Create a Yaml File with Metadata Formats and OAI Sets based on Repox
class YamlWriter:
    def __init__(self, filename):
        self.filename = filename

    def build(self):
        repox = Repox(settings["repox"], settings["username"], settings["password"])
        providers = repox.get_list_of_providers()
        i = 1
        with open(self.filename, "w") as my_yaml:
            for provider in providers:
                sets = repox.get_list_of_sets_from_provider(provider)
                metadata_formats = set([oai_set["format"] for oai_set in sets if oai_set["format"]])
                our_provider = {i: {}}
                for mf in metadata_formats:
                    our_provider[i][mf] = []
                for oai_set in sets:
                    our_provider[i][oai_set["format"]].append(oai_set["name"])
                yaml.dump(our_provider, my_yaml, default_flow_style=False, Dumper=DLTNDumper)
                i += 1
        return


# class RepoxRequest:
#     def __init__(self, username, password,  swagger_endpoint="https://dpla.lib.utk.edu/repox/rest"):
#         self.swagger_url = swagger_endpoint
#         self.username = username
#         self.password = password
#         self.connection = requests.get(swagger_endpoint, auth=(username, password))
#         self.headers = {'content-type': 'application/json'}
#
#     def get_aggregator(self, aggregator_id="TNDPLAr0"):
#         return requests.get(f"{self.swagger_url}/aggregators/{aggregator_id}",
#                             auth=(self.username, self.password)).content
#
#     def get_list_of_providers(self, aggregator_id="TNDPLAr0"):
#         r = requests.get(f"{self.swagger_url}/providers?aggregatorId={aggregator_id}",
#                          auth=(self.username, self.password))
#         parsed = json.loads(r.content)
#         return [provider["id"] for provider in parsed]
#
#     def get_providers_options(self):
#         return requests.get(f"{self.swagger_url}/providers/options", auth=(self.username, self.password)).content
#
#     def get_list_of_sets_by_provider(self, provider_id="KnoxPLr0"):
#         r = requests.get(f"{self.swagger_url}/datasets?providerId={provider_id}", auth=(self.username, self.password))
#         parsed = json.loads(r.content)
#         return [{"name": oai_set["dataSource"]["id"], "format": oai_set["dataSource"]["metadataFormat"]}
#                 for oai_set in parsed]


if __name__ == "__main__":
    x = YamlWriter("sets.yml")
    x.build()