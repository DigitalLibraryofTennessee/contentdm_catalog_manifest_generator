import yaml
from repox.repox import Repox
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

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
        providers = repox.get_list_of_providers("TNDPLAr0")
        i = 1
        with open(self.filename, "w") as my_yaml:
            for provider in providers:
                sets = repox.get_list_of_sets_from_provider_by_format(provider)
                metadata_formats = set([oai_set["format"] for oai_set in sets if oai_set["format"]])
                our_provider = {i: {}}
                for mf in metadata_formats:
                    our_provider[i][mf] = []
                for oai_set in sets:
                    our_provider[i][oai_set["format"]].append(oai_set["name"])
                yaml.dump(our_provider, my_yaml, default_flow_style=False, Dumper=DLTNDumper)
                i += 1
        return


if __name__ == "__main__":
    x = YamlWriter("sets.yml")
    x.build()
