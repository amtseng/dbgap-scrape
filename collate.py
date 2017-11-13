import numpy as np
import update


def get_fields(study_id):
    return study_id.split(".")


def import_scraped_studies(table_path):
    """
    Import scraped studies table (TSV), returns dictionary mapping study IDs
    to dictionaries for parent, WGS, WES, the sum of WGS and WES, consent
    groups, and name.
    Also prints out the list of studies that are both parents and substudies, as
    a sanity check (this should be an empty list)
    """
    d = open(table_path, "r")
    next(d)
    studies = {}
    for line in d:
        tokens = line.strip().split("\t")
        studies[tokens[0]] = {"par": tokens[1],
                              "wgs": tokens[2],
                              "wes": tokens[3],
                              "wgs+wes": tokens[4],
                              "cons": tokens[5],
                              "name": tokens[6]
                             }
    d.close()
   
    # Sanity check
    top_level_studies = [study for study in studies if studies[study]["par"] == "NA"]
    substudies = [study for study in studies if studies[study]["par"] != "NA"]
    print("Studies that are both parents and substudies:")
    print(np.intersect1d(top_level_studies, substudies))

    return studies


def import_requested_studies(list_path):
    """
    Import list of studies that have already been requested. This list must
    be a series of full study IDs or partial study IDs.
    Returns this list of full IDs, and a parallel list of partial IDs.
    Prints out number of unique studies in the list (top-level), based on
    partial ID.
    """
    h = open(list_path, "r")
    have = [line.strip() for line in h]
    h.close()
    
    have_unique = np.unique(have)
    have_partial = []
    have_partial = [get_fields(study_id)[0] for study_id in have_unique]

    print("Number of studies we have:")
    print(len(have_partial))

    return have_unique, have_partial


def export_studies_with_sequences(req_path, not_req_path, studies, req_studies):
    """
    Given the dictionary of studies `studies`, and a list of requested studies
    (partial IDs only), constructs a table of top-level studies with sequences
    that have already been requested, and a table that have NOT been
    requested. These tables are written to `req_path` and `not_req_path`,
    respectively.
    The columns are nearly identical to that of the original scraped studies
    table, but also with a URL to the study page.
    Note that the `study_id` column is now `top_level_study_id`, and there is
    no `parent_id` column.
    """
    top_level_studies = [study for study in studies if studies[study]["par"] == "NA"]

    y = open(req_path, "w")
    n = open(not_req_path, "w")
    col_names = "\t".join(["top_level_study", "wgs_num", "wes_num", "seq_total", "consent_groups", "name", "url"]) + "\n"
    y.write(col_names)
    n.write(col_names)

    for study in top_level_studies:
        wgs, wes = studies[study]["wgs"], studies[study]["wes"]
        both = str(int(wgs) + int(wes))
        cons = studies[study]["cons"]
        name = studies[study]["name"]
        url = "https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=" + study

        if both == "0":
            continue

        row = "\t".join([study, wgs, wes, both, cons, name, url]) + "\n"
        if get_fields(study)[0] in req_studies:
            y.write(row)
        else:
            n.write(row)

    y.close()
    n.close()
    

if __name__ == "__main__":
    study_json_path = "results/studies.json"  # Output JSON of a scraping run
    req_studies_path = "results/requested_studies.txt"  # List of all studies that have been requested already

    study_table_path = "results/dbgap_studies.tsv"  # Where to put table of all studies
    existing_studies_path = "results/existing_top_level_studies.tsv"  # Where to put table of all requested studies
    new_studies_path = "results/new_top_level_studies.tsv"  # Where to put table of new non-requested studies

    update.export_study_table(study_json_path, study_table_path)
    studies = import_scraped_studies(study_table_path)
    req_studies = import_requested_studies(req_studies_path)[1]
    export_studies_with_sequences(existing_studies_path, new_studies_path, studies, req_studies)








