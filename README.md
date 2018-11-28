# DLTN ContentDM IIIF Manifest Catalog Generator

## About

This generates a catalog.xml file for use in the [Digital Libary of Tennessee's XSL tranformations](https://github.com/DigitalLibraryofTennessee/DLTN_XSLT)

The catalog lists all records from a provider with a corresponding IIIF manifest. Our XSL transforms in Repox then read this file to determine when to create a link to a IIIF manifest should be created.

## Installing with [Pipenv](https://pipenv.readthedocs.io/en/latest/)

1. git clone git@github.com:DigitalLibraryofTennessee/contentdm_catalog_manifest_generator.git
2. cd contentdm_catalog_manifest_generator
3. pipenv install Pipfile

## Running

Assuming you installed with pipenv:

```
pipenv shell
python generate.py -p provider_name -m metadata_format
```

## Sample Output

```xml
<catalog>
	<set id='tsla_p15138coll45'>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/p15138coll45/id/67'/>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/p15138coll45/id/66'/>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/p15138coll45/id/78'/>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/p15138coll45/id/79'/>
	</set>
	<set id='tfd'>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/tfd/id/25'/>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/tfd/id/22'/>
		<item id='http://cdm15138.contentdm.oclc.org/cdm/ref/collection/tfd/id/24'/>
	</set>
</catalog>
```