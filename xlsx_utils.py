from openpyxl import load_workbook


def get_xlsx_data(xlsx_file, sheet_name):

    FIELDS_ROW = 2
    FIRST_DATA_ROW = 7

    # verify that the xlsx file exists and has a sheet named 'Gear' if
    # anything goes wrong, print a message that says:

    # "something has gone wrong.  Please verify that the submitted
    # file is a valid and current GLFC Lamprey Template."

    # Load the workbook and select the active sheet
    wb = load_workbook(xlsx_file)

    sheet = wb[sheet_name]
    fields = [x.value.strip() for x in sheet[FIELDS_ROW] if x.value]

    data = []

    # Iterate through all rows
    for row in sheet.iter_rows(values_only=True, min_row=FIRST_DATA_ROW):
        if row.count(None) != len(row):
            record = {k: v for k, v in zip(fields[1:], row[1:])}
            data.append(record)

    return data
