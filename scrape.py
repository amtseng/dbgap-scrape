from bs4 import BeautifulSoup
import urllib2, ssl
import util


PARENT_STUDY_LIST_URL = "ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/"
STUDY_DIRECTORY_URL_FORMAT = "ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/{0}/"
STUDY_PAGE_URL_FORMAT = "https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/molecular.cgi?study_id={0}"
SEARCH_PAGE_URL_FORMAT = "https://www.ncbi.nlm.nih.gov/gap/?term={0}"
   
    
class EmptyResponseException(Exception):
    pass


class Scraper:
    """
    Basic dbGaP scraping functionalities.
    Initialization:
        scr = Scraper()  # Use entire list of parent studies
        scr = Scraper(["phs1234567", "phs7654321"])  # Use this partial list
                                                     # of parent studies
    Methods:
        scr.get_parent_study_list(verbose=False)
        scr.get_all_full_parent_study_ids(verbose=False)
        scr.get_study_info(study_id, verbose=False)
    """

    def __init__(self, partial_study_ids=None):
        """
        If `partial_study_ids` is passed in, then methods like
        `get_parent_study_list` and `get_all_full_parent_study_ids` will only
        look through these study IDs.
        Note that this must be a list of strings, each of the form
        "phs1234567".
        """
        self.partial_study_ids = partial_study_ids

    def _read_page(self, url, timeout=5, retries=3, verbose=False):
        """
        Given a URL, returns the contents of the response.
        If the response is empty, retries the fetch `retries` number of times.
        Timeout for each try is `timeout`, default 5 seconds.
        metadata of each request.
        If `verbose` is set to True, print out the status of each request.
        """
        response = ""
        while not response and retries >= 0:
            try:
                response_obj = urllib2.urlopen(url, timeout=timeout)
                response = response_obj.read()
                if verbose:
                    print("---reponse received")
            except (urllib2.URLError, ssl.SSLError):
                if verbose:
                    print("---timeout") 
            finally:
                retries -= 1
        if not response:
            raise EmptyResponseException("{0} gave empty responses in all attempts".format(url))
        if verbose:
            print("---success: nonempty response")
        return response

    def get_parent_study_list(self, verbose=False):
        """
        From the FTP mirror `PARENT_STUDY_LIST_URL`, which lists all parent
        study numbers (e.g. "phs1234567").
        Returns a list of strings, each of which is a parent study ID.
        If `self.partial_study_ids` is set, return that instead.
        """
        if self.partial_study_ids:
            if verbose:
                print("Using existing list of parent study partial IDs")
            return self.partial_study_ids

        study_list_page = self._read_page(PARENT_STUDY_LIST_URL, verbose=verbose)
        study_list = [row.strip().split()[-1] for row in study_list_page.strip().split("\n")]
        # Remove first item, which is the table of contents
        return study_list[1:]
   
    
    def _search_for_full_study_id(self, study_id, verbose=False):
        """
        Perform a search for a partial study ID to find the full study ID.
        In the search results, check only the first result returned, and
        ensure it is a match to the provided `study_id`.
        If no results are returned, returns None. Otherwise, returns the
        full study ID.
        """
        url = SEARCH_PAGE_URL_FORMAT.format(study_id)
        page = self._read_page(url)
        soup = BeautifulSoup(page, "html.parser")

        table = soup.find("table")
        if not table:
            if verbose:
                print("No results for {0}".format(study_id))
            return None 

        record = table.find_all("tr")[0]  # First record only
        contents = record.span.contents
        if len(contents) == 2 and contents[0].string.split(".")[0] == study_id:
            full_study_id = contents[0].string + contents[1]
            if verbose:
                print("Found {0} --> {1}".format(study_id, full_study_id))
            return contents[0].string + contents[1]
        return None

    def _get_full_parent_study_id(self, study_id, verbose=False):
        """
        Given a parent study ID (e.g. "phs1234567"), finds the latest full
        study ID from the FTP mirror (e.g. "phs1234567.v8.p1") in terms of
        version number, and returns that fully-formatted ID.
        This may not be truly the most recent, but this function will at least
        try to find _some_ valid full study ID.
        """
        url = STUDY_DIRECTORY_URL_FORMAT.format(study_id)
        direc_list_page = self._read_page(url, verbose=verbose)
        directories = [row.strip().split()[-1] for row in direc_list_page.strip().split("\n")]
        best_id, best_version = None, 0
        for direc in directories:
            version = util.version_num(direc)
            if version is None:
                continue
            if version > best_version:
                best_id, best_version = direc, version

        if best_id is None:
            # Try searching for the study directly as a last resort
            best_id = self._search_for_full_study_id(study_id, verbose=verbose)

        return best_id

    def get_all_full_parent_study_ids(self, verbose=False):
        """
        Using the list of all parent study IDs, finds the list of all full
        study IDs for all parent studies. This function attempts to find the
        most recent full ID, but it is not guaranteed. It will find _some_
        valid full ID if possible. Returns a list of full parent study IDs,
        parallel to the list of partial parent study IDs found by
        `get_parent_study_list`.
        If any of the studies consistently return empty responses, skip them.
        """
        study_list = self.get_parent_study_list(verbose=verbose)
        full_study_list = []
        for study_id in study_list:
            try:
                full_study_id = self._get_full_parent_study_id(study_id, verbose=verbose)
                if verbose:
                    print("Full study ID {0} -> {1}".format(study_id, full_study_id))
                full_study_list.append(full_study_id)
            except EmptyResponseException:
                if verbose:
                    print("Error: Empty responses from {0}".format(study_id))
        return full_study_list
   
    def _fetch_study_page(self, study_id, verbose=False):
        """
        Given a fully-formatted `study_id` (e.g. "phs1234567.v8.p1"),
        fetches the study page denoted by `STUDY_PAGE_URL_FORMAT", and parses
        it. Returns the BeautifulSoup parser object for this page.
        """
        url = STUDY_PAGE_URL_FORMAT.format(study_id)
        content = self._read_page(url, verbose=verbose)
        soup = BeautifulSoup(content, "html.parser")
        return soup
   
    def _get_study_title(self, soup):
        """
        Given the parser object for a study's info page, returns the name of
        the study as a string.
        Returns None if the title could not be found.
        """
        span = soup.find("span", {"id": "study-name"})
        if not span:
            return None
        text = span.text
        return " ".join(text.split())
   
    def _match_data_type(self, data_type):
        """
        Given a sequencing data type, returns whether or not the data type is
        of interest. Looks for the phrases "whole exome" or "whole genome".
        This function may be tweaked to determine what kind of sequencing data
        is of interest.
        """
        data_type = data_type.lower()
        return "whole exome" in data_type or "whole genome" in data_type
   
    def _get_num_sequences(self, soup, study_id):
        """
        Given the parser object for a study's info page, and the fully-
        formatted study ID, finds the number of sequences of interest for the
        study. If `study_id` is not the lastest version of the study, then use
        the latest version instead.
        Returns a dictionary of dictionaries, mapping substudies to the number
        of sequences of each type of interest:
            phs1234567.v1.p1: {type1: 100},
            phs7654321.v8.p3: {type1: 200, type2: 300}
            ...
        """
        # Check this really is the latest version
        study_history_div = soup.find("div", {"id": "studyHistoryTable"})
        if study_history_div:
            study_history_table = study_history_div.find("table").contents
            # Other studies in history table are links: <td><a href=...>phs1234567.v8.p8</a></td>
            study_history = [item.td.a.string.strip() for item in study_history_table if item.name and item.td and item.td.a]
            newest_id = study_history[-1]
            if newest_id and util.version_num(newest_id) > util.version_num(study_id):
                return self._get_num_sequences(self._fetch_study_page(newest_id), newest_id)
    
        table = soup.find("tbody")
        seqs = {}

        if not table:
            return seqs
    
        for row in table.contents:
            if not row.name:
                # String, not a real row
                continue
            row_tokens = [item.string for item in row.contents if item.name and item.string]
            # study, data type, group1 samples, group1 subjects, group2 samples, group2 subjects, etc.
            study, data_type, data_nums = row_tokens[0], row_tokens[1], row_tokens[2:]
            if not self._match_data_type(data_type):
                continue
           
            num = sum(int(x) for x in data_nums[::2])
            try:
                seqs[study][data_type] = num
            except KeyError:
                seqs[study] = {data_type: num}

        return seqs

    def get_study_info(self, study_id, verbose=False):
        """
        Given a fully-formatted `study_id`, finds the name and number of
        sequences of interest for the most recent version of the study.
        Returns a multi-level dictionary with top-level keys: "name", "seqs".
            id:
                full: study_id
                part: study_id partial ID
                version: version number
            name: study_name
            seqs:
                phs1234567.v1.p1: {type1: 100},
                phs7654321.v8.p3: {type1: 200, type2: 300}
        Returns None if basic information like the title cannot be found.
        """
        soup = self._fetch_study_page(study_id, verbose=verbose)
        name = self._get_study_title(soup)
        if not name:
            return None
        seqs = self._get_num_sequences(soup, study_id)
        fields = util.study_id_fields(study_id)
        return {
            "id": {"full": study_id, "part": fields[0], "version": fields[1]},
            "name": name,
            "seqs": seqs
        }



if __name__ == "__main__":
    # Testing
    test_ids = ['phs000545', 'phs000007', 'phs000178', 'phs000401', 'phs000378', 'phs000123', 'phs000227', 'phs000184', 'phs000301', 'phs000342']
    verbose = False

    scr = Scraper(test_ids)

    full_study_list = scr.get_all_full_parent_study_ids(verbose=verbose)
    print(full_study_list)

    for study_id in full_study_list:
        if study_id is not None:
            print(scr.get_study_info(study_id, verbose=verbose))
