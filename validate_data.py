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

from db_utils import (
    get_fish_accdb,
    get_gear_accdb,
    validate,
    duplicate_check,
    orphan_check,
)
from xlsx_utils import get_xlsx_data, write_error_report
from schemas import BioData, Gear

start_time = time.perf_counter()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--src_file", help="data source file. Either accdb or xlsx")
parser.add_argument(
    "-v", "--verbose", help="print verbose output to console.", type=bool, default=False
)

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

# any errors will be written to a file named "<original_file>-report.xlsx"
new_name = file_path.name.replace(file_path.suffix, "-report.xlsx")
outfile = file_path.with_name(new_name)

print(f"Validating data in: {file_path.name}")

# read in our data:
if file_path.suffix == ".xlsx":
    gear_in = get_xlsx_data(SRC, "Gear")
    fish_in = get_xlsx_data(SRC, "Biodata")
else:
    gear_in = get_gear_accdb(SRC)
    fish_in = get_fish_accdb(SRC)


# validate our gear:
gear = validate(gear_in, Gear)

# check for duplicate ids:
lift_ids = [x.liftid for x in gear["data"]]
duplicate_liftids = duplicate_check(lift_ids)

print(f"{len(gear.get('data'))} gear records successfully validated")

if len(duplicate_liftids) == 0:
    print("No duplicate lift Ids found")
else:
    print(f"{len(duplicate_liftids)} duplicate lift ids found.")
    print("For Example:")
    for item in duplicate_liftids[:5]:
        rprint(item)


gear_errors = gear["errors"]
print(f"{len(gear_errors)} records with at least one validation error")
if gear_errors:
    print(f"Gear Errors written out to: {outfile}")
    write_error_report(gear_errors, outfile, "Gear_errors")
    if args.verbose:
        print("For Example")
        for item in gear_errors[:5]:
            rprint(item)


# validate our fish:
fish = validate(fish_in, BioData)

# check for duplicate ids:
fish_ids = [x.fishid for x in fish["data"]]
duplicate_fishids = duplicate_check(fish_ids)

if len(duplicate_fishids) == 0:
    print("No duplicate fish Ids found")
else:
    print(f"{len(duplicate_fishids)} duplicate fish ids found.")
    print("For Example:")
    for item in duplicate_fishids[:5]:
        rprint(item)


fish_lift_ids = [x.liftid for x in fish["data"]]
orphan_fish = orphan_check(lift_ids, fish_lift_ids)

if len(orphan_fish) == 0:
    print("No orphan fish found")
else:
    print(f"{len(orphan_fish)} orphan fish found.")
    print("For Example:")
    for item in list(orphan_fish)[:5]:
        rprint(item)


print(f"{len(fish['data'])} fish records successfully validated")
fish_errors = fish["errors"]
print(f"{len(fish_errors)} records with at least one validation error")
if fish_errors:
    print(f"BioData Errors written out to: {outfile}")
    write_error_report(fish_errors, outfile, "BioData_errors")
    if args.verbose:
        print("For Example")
        for item in fish_errors[:5]:
            rprint(item)


end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
