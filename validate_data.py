"""

useage:

python valiadate.py -s "Lamprey_data_HU-2023.accdb"
python valiadate.py -s "Lamprey_data_HU-2023.xlxs"

"""

import argparse
import sys
import time
from pathlib import Path

from rich import print as rprint

from db_utils import get_fish_accdb, get_gear_accdb, validate
from xlsx_utils import get_xlsx_data
from schemas import BioData, Gear

start_time = time.perf_counter()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--src_file", help="data source file. Either accdb or xlsx")
args = parser.parse_args()

if args.src_file:
    SRC = args.src_file
else:
    sys.exit("a 'src_file' must be provided using the '-s' argument")

allowed_extensions = {".xlsx", ".accdb"}

file_path = Path(SRC)

if file_path.suffix.lower() not in allowed_extensions:
    sys.exit("'src_file' must be a valid MSAccess or MSExcel file.")

if not file_path.is_file():
    msg = f"Unable to find {file_path}.\n Please verify that the file exists."
    sys.exit(msg)

print(f"Validating data in: {file_path.name}")

if SRC.endswith("xlsx"):
    gear_in = get_xlsx_data(SRC, "Gear")
else:
    gear_in = get_gear_accdb(SRC)

gear = validate(gear_in, Gear)

print(f"{len(gear.get('data'))} gear records successfully validated")

gear_errors = gear["errors"]
print(f"{len(gear_errors)} records with at least one error")
if gear_errors:
    print("For Example")
    for item in gear_errors[:5]:
        rprint(item)


if SRC.endswith("xlsx"):
    fish_in = get_xlsx_data(SRC, "Biodata")
else:
    fish_in = get_fish_accdb(SRC)
fish = validate(fish_in, BioData)

print(f"{len(fish['data'])} fish records successfully validated")

fish_errors = fish["errors"]

print(f"{len(fish_errors)} records with at least one error")
if fish_errors:
    print("For Example")
    for item in fish_errors[:5]:
        rprint(item)


end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
