### Scraper for dbGaP
---------

#### Usage
```
usage: main.py [-h] [-i INFILE] [-o OUTFILE] [-u UPDATEFILE] [-v]

Scrape dbGaP for whole exome or whole genome sequences, and update according
to existing info.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input file containing existing study info JSON
                        (optional).
  -o OUTFILE, --outfile OUTFILE
                        Output file to write newly fetched info JSON
                        (optional).
  -u UPDATEFILE, --updatefile UPDATEFILE
                        File to write the update diff to (in human-readable
                        format). If not provided, writes to stdout.
  -v, --verbose         If set, print out (to stdout) scraping updates.
```

#### Functions of interest
```
updater.export_study_table(input_json_path, output_table_path)
    Writes the JSON of all dbGaP studies/substudies into a table

scrape.Scraper._match_data_type(self, data_type)
    For a type of sequencing data, determine whether or not to record it.
    For now, this only looks for whole genome/exome sequences, but this may
    be tweaked manually.
```
