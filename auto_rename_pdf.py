import os
import re
import glob
import argparse
import pdfplumber
import pandas as pd
from pathlib import Path

def find_columns(df):
    for k, v in df.items():
        print(f"{k}: {v}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name_id",
        "-f",
        help="Excel which includes the correspondence between ID and name of students",
        type=str,
        default="",
    )
    parser.add_argument(
        "--cols",
        "-c",
        help="columns of [index, ID, name]",
        type=list,
        default=[0, 1, 2],
    )
    parser.add_argument(
        "--id_pattern", "-p", help="Pattern of students ID", type=str, default=""
    )
    parser.add_argument(
        "--in_current_dir",
        "-i",
        help="rename files in current directory or not",
        action="store_true",
    )
    args = parser.parse_args()

    files = glob.glob("*.pdf")
    if not args.in_current_dir:
        Path("renamed_files").mkdir(exist_ok=True)

    # the specific index of columns should be checked according to the given excel.
    if args.file_name_id != "":
        df = pd.read_excel(args.file_name_id)
        # find_columns(df)
        name_id = dict(
            zip(df[f"Unnamed: {args.cols[1]}"], df[f"Unnamed: {args.cols[2]}"])
        )
        num_name = dict(zip(df[f"Unnamed: {args.cols[1]}"], df[f"Unnamed: {args.cols[0]}"]))

    for f in files:
        pdf = pdfplumber.open(f)
        title = pdf.pages[0].extract_words()[0]["text"]
        contents = pdf.pages[0].extract_text()
        if args.id_pattern == "":
            matches = re.search("(PB|SA)[0-9]{8}", contents)
        else:
            matches = re.search(args.id_pattern, contents)
        ID = matches.group(0) if matches is not None else None
        if ID is None:
            print(f"{f} is not renamed.")
            continue
        if args.file_name_id != "":
            f_name = f"{str(num_name[str(ID)])}-{name_id[str(ID)]}-{str(ID)}-{title}.pdf"
        else:
            f_name = f"{str(num_name[str(ID)])}-{title}.pdf"
        if not args.in_current_dir:
            os.system(f"cp '{f}' 'renamed_files/{f_name}'")
        else:
            os.system(f"cp '{f}' '{f_name}'")
        # break
    print("successfully renamed files into renamed_files directory")


if __name__ == "__main__":
    main()
