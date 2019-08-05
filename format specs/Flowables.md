## Flowables Input File Format

Flowable input files are the form of CSV data with the following fields.

 Field | Type | Required |  Note |
----------- |  ---- | ---------| -----  |
 Flowable | string | Y | the flowable name |
 CAS No | string | N | CAS number |
 Formula | string | N | chemical formula |
 Synonyms | string | N | flow synonyms |
 Unit | string | Y  | the reference unit. uses olca units |
 External Reference | string | N | description or link to reference for conversion values |
 Flowable Preferred | int | Y | 1 for preferred, 0 for non-preferred |