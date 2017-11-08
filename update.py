import util
from scrape import Scraper
import sys

class Updater:
    """
    Updater for scraped information from dbGaP.
    Initialization:
        # Read from infile, write to outfile
        # Use entire list of parent studies from dbGaP
        upd = Updater("infile.json", "outfile.json")
    
        # No infile to read from, do not write output to outfile
        # Use this partial list of parent studies
        upd = Updater(["phs1234567", "phs7654321"])
    Methods:
        upd.update_studies(fs=None, verbose=False)
    """

    def __init__(self, infile, outfile, partial_study_ids=None):
        """
        `infile` is the path to the file in which the old study info is.
        This may be None if there is no such file. `outfile` is the path to
        the file to save the new study info. If `outfile` is None, then the
        results are not saved. If `infile` and `outfile` are the same, then
        the new information will overwrite the old.
        If `partial_study_ids` is passed in, only look at those studies.
        """
        self.infile = infile
        self.outfile = outfile
        self.partial_study_ids = partial_study_ids

    def _fetch_newest_studies(self, verbose=False):
        """
        Constructs a Scraper and downloads all the info in all available
        parent studies, or all studies in `self.partial_study_ids` if
        provided.
        Returns a list of dictionaries.
        """
        scr = Scraper(partial_study_ids=self.partial_study_ids)
        full_study_list = scr.get_all_full_parent_study_ids(verbose=verbose)

        if verbose:
            print("Fetching info for {0} parent studies".format(len(full_study_list)))
   
        study_info = []
        for study_id in full_study_list:
            if study_id is not None:
                info = scr.get_study_info(study_id, verbose=verbose)
                if info:
                    study_info.append(info)
                    if verbose:
                        print("Info fetched for {0}".format(study_id))
                else:
                    if verbose:
                        print("No info found for {0}".format(study_id))
            else:
                if verbose:
                    print("No info found for a study")
        return study_info

    def _compare_study_info(self, old_info, new_info):
        """
        Given two lists of study info (two lists of dictionaries), compares
        the contents and returns the differences in `new_info`.
        The following dictionary is returned:
            new: [{...}, {...}]
            updates: [{...}, {...}]
        """
        old_info_by_id = {d["id"]["part"]: d for d in old_info}
        new_info_by_id = {d["id"]["part"]: d for d in new_info}

        # IDs in new, but not old
        new_ids = set(new_info_by_id.keys()) - set(old_info_by_id.keys())
        new_studies = [new_info_by_id[new_id] for new_id in new_ids]

        # IDs that are in both new and old, but new version is higher
        update_ids = [s_id for s_id in new_info_by_id if
                (s_id in old_info_by_id) and (new_info_by_id[s_id]["id"]["version"] > old_info_by_id[s_id]["id"]["version"])]
        update_studies = [new_info_by_id[update_id] for update_id in update_ids]

        return {
            "new": new_studies,
            "updates": update_studies
        }

    def _print_updates(self, updates, fs=None):
        """
        Given a dictionary of updates, as `compare_study_info` would return,
        prints out the updates in a human-readable manner.
        By default prints to stdout, but if another file stream is passed in
        as `fs`, then write to that file stream instead.
        """
        if not fs:
            fs = sys.stdout

        def write_info(info):
            name = info["name"].encode("ascii", "ignore")
            fs.write("{0}: {1}\n".format(info["id"]["full"], name))
            for seq in info["seqs"]:
                seq_nums = ", ".join(["{0} {1}".format(num, seq_type) for seq_type, num in info["seqs"][seq].iteritems()])
                fs.write("\t{0}: {1}\n".format(seq, seq_nums))

        fs.write("New studies\n")
        fs.write("----------------------------------------\n")
        for info in updates["new"]:
            if info["seqs"]:
                # Only care about new studies with sequences of interest
                write_info(info)

        fs.write("\n")

        fs.write("Updated studies\n")
        fs.write("----------------------------------------\n")
        for info in updates["updates"]:
            write_info(info)

    def update_studies(self, fs=None, verbose=False):
        """
        Updates the studies, based on `self.infile` and
        `self.partial_study_ids`. If `self.outfile` was given, write the study
        information there.
        Writes the difference of the update to `fs`, an open file stream. By
        default this is stdout.
        Note that if `self.infile` was not provided, this is treated as
        everything in this update being new.
        """
        old_info = util.import_json(self.infile) if self.infile else {}

        new_info = self._fetch_newest_studies(verbose=verbose)
        if self.outfile:
            util.export_json(self.outfile, new_info)

        updates = self._compare_study_info(old_info, new_info)
        self._print_updates(updates, fs=fs)

                
if __name__ == "__main__":
    # Testing
    test_ids = ['phs000545', 'phs000007', 'phs000178', 'phs000401', 'phs000378', 'phs000123', 'phs000227', 'phs000184', 'phs000301', 'phs000342']
    
    upd = Updater(None, "outfile.json", test_ids)
    upd.update_studies(verbose=True)
