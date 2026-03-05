import sys
import time
from pathlib import Path

from rich import print as rprint

from db_utils import get_fish_accdb, get_gear_accdb, validate
from schemas import BioData, Gear

start_time = time.perf_counter()

SRC_DB = "C:/Users/COTTRILLAD/Documents/1work/Python/LampreySchema/glis_GLFC_lamprey/Lamprey_data_HU-2023.accdb"

# SRC_DB = "C:/Users/COTTRILLAD/Documents/1work/R/sandbox/glis_glfc_lamprey/Lamprey_data_HU-1991.accdb"

p = Path(SRC_DB)

if not p.is_file():
    msg = f"Unable to find {p}.\n Please verify that the file exists."
    sys.exit(msg)


gear_raw = get_gear_accdb(SRC_DB)
gear = validate(gear_raw, Gear)


print(f"Valididating data in: {p.name}")

gear_raw = get_gear_accdb(SRC_DB)
gear = validate(gear_raw, Gear)

print(f"{len(gear.get('data'))} gear records successfully validated")

gear_errors = gear["errors"]
print(f"{len(gear_errors)} records with at least one error")
if gear_errors:
    print("For Example")
    for item in gear_errors[:5]:
        rprint(item)


fish_raw = get_fish_accdb(SRC_DB)
fish = validate(fish_raw, BioData)

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
