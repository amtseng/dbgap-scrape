### Scraper for dbGaP
---------
#### Scraper `run_update.sh` usage
```
usage: sh run_update.sh <email>
```
- Scrapes all the studies from dbGaP, and updates the result in a stored "database" file
- Computes the differential update (any new or updated studies), and sends an email containing this update to the provided email address

#### Scraper `main.py` usage
- The `main.py` file allows a slightly lower-level invocation of the scraper.

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

`INFILE`
- Specifies an existing JSON file containing the results of scraping dbGaP
- This should almost certainly be the outfile of a previous execution of this program
- If this file is not specified, it is interpreted as an empty set (no existing information)

`OUTFILE`
- Specifies the file to write the JSON object containing the results of scraping dbGaP
- This file will contain all the information scraped from this execution
- If this file is not specified, the results of this newest scrape will not be saved anywhere (nor will it be written to `stdout`)

`UPDATEFILE`
- Specifies the file in which to write the new and updated studies
- Studies with no sequence data of interest at all are ignored
- The output is in human-readable format, split into sections:
    - New studies: completely new top-level studies
    - Updated studies: top-level studies that were in the `INFILE`, but have been updated somehow
- If this argument is not provided, the diff is still calculated, but written to `stdout` instead

**Example invocations**

`python main.py -o data/studies.json -u diff.txt`
- Scrapes all information down, without any knowledge of previous scrapes
- `diff.txt` will contain all scraped studies with some sequences of interest
`python main.py -i data/studies.json -o data/studies.json -u diff.txt`
- If this program has previously been run with the previous results stored at `data/studies.json`, this will scrape dbGaP again and overwrite it with the newest data
- Before overwriting, the diff is computed and written to `diff.txt`

#### Functions of interest
`updater.export_study_table(input_json_path, output_table_path)`
- Writes the JSON of all dbGaP studies/substudies into a table

`scrape.Scraper._match_data_type(self, data_type)`
- For a type of sequencing data, determine whether or not to record it
- For now, this only looks for whole genome/exome sequences, but this may be tweaked manually

`scrape.Scraper._read_page(self, url, timeout=5, retries=3, verbose=False)`
- Performs the basic function of reading a page from a URL
- The default timeout (in seconds) may be changed, as well as the number of retries
- Retries are performed when the request times out, or a blank page is returned
- This default setting of a 5-second timeout and 3 retries is recommended

