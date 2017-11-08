import argparse
from update import Updater

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape dbGaP for whole exome or whole genome sequences, and update according to existing info."
    )
    parser.add_argument("-i", "--infile", default=None, type=str,
        help="Input file containing existing study info JSON (optional)."
    )
    parser.add_argument("-o", "--outfile", default=None, type=str,
        help="Output file to write newly fetched info JSON (optional)."
    )
    parser.add_argument("-u", "--updatefile", default=None, type=str,
        help="File to write the update diff to (in human-readable format). If not provided, writes to stdout."
    )
    parser.add_argument("-v", "--verbose", action="store_true",
        help="If set, print out (to stdout) scraping updates."
    )

    args = parser.parse_args()

    upd = Updater(args.infile, args.outfile)

    if args.updatefile:
        # Write the update to a file
        with open(args.updatefile, "w") as fs:
            upd.update_studies(fs=fs, verbose=args.verbose)
    else:
        # Write the update to stdout
        upd.update_studies(verbose=args.verbose)
