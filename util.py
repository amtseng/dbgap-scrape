import re
import json


def study_id_fields(study_id):
    """
    Extracts fields of fully-formatted study ID.
    Returns a triplet of the ID, version, and participant version, as a
    string, and two ints.
    e.g. "phs1234567.v8.p1" --> ("phs1234567", 8, 1)
    If `study_id` is not properly formatted, then return None.
    """
    regex = r"(phs\d+)\.v(\d+)\.p(\d+)"  # phs_______.v_.p_
    match = re.search(regex, study_id)
    if match:
        groups = match.groups()
        return (groups[0], int(groups[1]), int(groups[2]))
    else:
        return None


def version_num(study_id):
    """
    Subroutine to extract the version number from a fully-formatted study
    ID. e.g. "phs1234567.v8.p1" --> 8.
    Returns the version `int` if `study_id` is properly formatted.
    Otherwise returns None.
    """
    fields = study_id_fields(study_id)
    return fields[1] if fields else None


def import_json(file_path):
    """
    From `file_path`, imports a JSON object into Python.
    """
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data


def export_json(file_path, obj, pretty=True):
    """
    Export JSON object `obj` to `file_path`. If `pretty` is set (by default
    it is), pretty-print `obj` to `file_path`, with proper indentation of 2
    spaces per level.
    """
    if pretty:
        json_str = json.dumps(obj, indent=2)
    else:
        json_str = json.dumps(obj)
    with open(file_path, "w") as json_file:
        json_file.write(json_str)
