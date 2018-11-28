# DLTN ContentDM IIIF Manifest Catalog Generator

## About

This generates a catalog.xml file for use in the [Digital Libary of Tennessee's XSL tranformations](https://github.com/DigitalLibraryofTennessee/DLTN_XSLT)

The catalog lists all records from a provider with a corresponding IIIF manifest. Our XSL transforms in Repox then read this file to determine when to create a link to a IIIF manifest should be created.

## Running

```python generate.py -p provider_name -m metadata_format```



