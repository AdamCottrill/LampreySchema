import pyodbc

from collections import Counter


def duplicate_check(ids):
    # return any id values that appear more than once
    counts = Counter(ids)
    duplicates = [item for item, count in counts.items() if count > 1]
    return duplicates


def orphan_check(gear_ids, fish_gear_ids):
    # return any fis_ids, that don't have a gear
    return set(fish_gear_ids) - set(gear_ids)


def get_accdb_connection(accdb):
    """

    Arguments:
    - `accdb`: path to either a *.accdb or *.accdb file.

    """
    constring = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s"
    con = pyodbc.connect(constring % accdb)
    return con


def execute_select(accdb, stmt):

    con = get_accdb_connection(accdb)

    dat = []
    with con.cursor() as cursor:
        cursor.execute(stmt)
        rs = cursor.fetchall()
        colnames = [x[0] for x in cursor.description]
        for row in rs:
            row_dict = {k: v for k, v in zip(colnames, row)}
            dat.append(row_dict)
    return dat


def get_gear_accdb(accdb: str):

    sql = """
    SELECT LiftID,
    Lake,
    Agency,
    Location,
    Latitude,
    Longitude,
    MU,
    GRID,
    Year,
    Month,
    Day,
    SurveyType,
    SurveyDescription,
    Gear,
    Nights,
    [NetLength(km)],
    [Depth1(m)],
    [Depth2(m)],
    [AvgDepth(m)],
    [SurfaceTemp(C)],
    [BottomTemp(C)],
    [MinMesh(mm)],
    [MaxMesh(mm)],
    NetMaterial
    FROM Gear;
    """

    return execute_select(accdb, sql)


def get_fish_accdb(accdb: str):
    sql = """
        SELECT LIFTID,
         Lake,
         Agency,
         FISHID,
         [MeshSize(mm)],
         SpeciesName,
         SpeciesNumber,
         SpeciesAbbrev,
         [Length(mm)],
         [Weight(g)],
         [R/D],
         CWTAgency,
         Age,
         AgeStructure,
         SexAgency,
         MaturityAgency,
         FinClipAgency,
         [A1-A3],
         A1,
         A2,
         A3,
         A4,
         B1,
         B2,
         B3,
         B4,
         Comments
        FROM FISH;
    """
    return execute_select(accdb, sql)


def validate(data_in, schema):
    valid_records = []
    errors = []

    for row in data_in:
        try:
            record = schema(**row)
            if record:
                valid_records.append(record)
        except Exception as e:
            # validation error
            item = {"data": row, "error": e}
            errors.append(item)

    return {"data": valid_records, "errors": errors}
