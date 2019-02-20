# ADSAffil

Affiliation augmentation for augment_pipeline.  The pipeline relies on a set
of predefined affiliation strings and affiliation data to assign canonical
affiliations to affiliation metadata; it uses the results of both human-
curated affiliation data and those derived from machine learning.

## Queues

There are two queues:

* augment-affiliation: take a record's affiliation and (try to) augment it

* output-record: send the results of augmentation to master-pipeline via msg

## Interactive operation

### Maintenance: Creating pickle files

The pickle file contains two dicts: affil_dict, the dictionary of curated
affiliation strings and their IDs; and canon_dict, the dictionary of canonical
IDs, abbreviations, and parent-child relationships.

To generate the pickle file from the command line, run the pipeline with:
```
run.py -mp
```
assuming the file paths and names in config.py are the locations for all of
these files.

---

### Maintenance: Send a test record for debugging purposes

To send a single record through the augmentation pipeline to master, run the
pipeline with:
```
run.py -d
```
This assumes that config.PICKLE_FILE already exists.  If the pipeline is
successful, the record in master_pipeline.records for 2002ApJ...576..963T
should have been augmented with the affiliation A00928 (Yale University
Astronomy Department) for all three authors.


---

### Production: Augment a list of records in a JSON file (e.g. exported by Solr)

To augment a set of records in file FILEPATH, run the pipeline with:
```
run.py -f FILEPATH
```

---

## Maintainer

Matthew Templeton, ADS
