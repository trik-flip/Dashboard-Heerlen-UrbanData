import sqlite3 as sql
import os
import pandas as pd


# DATA_DIR = "gegevens/Algemeen/"
# DATA_DIR = "Dashboard-Code/data/Kerncijfers_wijken_en_buurten_2020_copy.csv"

DATA_DIR = "Dashboard-Code/data/"
ALL_FILE_NAMES = os.listdir(DATA_DIR)
file_names = [x for x in ALL_FILE_NAMES if x[-5:] not in ["y.csv", "p.csv"]]
pre_file_names = [x for x in ALL_FILE_NAMES if x[-7:] == "_pp.csv"]


def edit_first_line(firstline: str):
    replacers = ["Sociale zekerheid|Personen per soort uitkering",
                 "|Personenauto\'s"
                 ]
    for replacer in replacers:
        firstline = firstline.replace(replacer+";", replacer)
    return "Wijk|Buurt" + firstline.replace(";", ",")


def extention_name(filename):
    file = ".".join(filename.split(".")[:-1])
    ext = filename.split(".")[-1]
    return file, ext


def preprocess_files(file_names,
                     foldername=DATA_DIR):
    for in_filename in file_names:
        with open(foldername + in_filename) as in_file, open(
            foldername + extention_name(filename=in_filename)[0] +
                "_pp." + extention_name(filename=in_filename)[1], "w"
        ) as out_file:
            first_line = in_file.readline()
            first_line = edit_first_line(first_line)
            out_file.write(first_line)
            for line in in_file:
                out_file.write(line.replace(";", ","))


def create_column_string(my_table):
    column_string = ""
    for column in my_table.columns:
        if str(my_table[column].dtypes) == "int64":
            type = "int"
        elif str(my_table[column].dtypes) == "float64":
            type = "real"
        else:
            type = "text"

        column_string += "_".join([x for x in column.split(" ")]
                                  ) + " " + type + ", "
    column_string = reconstruct_string(column_string)
    return column_string[:-2]


def reconstruct_string(column_string, replacers=[]):
    replacers += [("|", "_"), ("/", "_"), ("-", "_"),
                  ("%", "proc"), (".", ""), ("'", ""),("+","_")]
    for x, y in replacers:
        column_string = column_string.replace(x, y)
    return column_string


def write_data(csv_data,
               table_name="example_table_2",
               database_file='UrbanData-test.db'):
    with sql.connect(database_file) as con:
        cur = con.cursor()
        cur.execute(
            f'CREATE TABLE {table_name} ({create_column_string(csv_data)})')
        for x in range(len(csv_data)):
            row = [value if type(value) != str else "\"" +
                   value + "\"" for value in csv_data.loc[x]]
            content = ",".join([str(x) for x in row])
            content = content.replace("nan", "NULL")
            cur.execute(
                f"INSERT INTO {table_name} VALUES ({content})")
        con.commit()


def write_data_to_database(pre_file_names, DATA_DIR=DATA_DIR):
    for file in pre_file_names:
        csv_data = pd.read_csv(DATA_DIR + file)
        write_data(csv_data, file[:-4])


if __name__ == "__main__":
    preprocess_files(file_names)
    write_data_to_database(pre_file_names)
