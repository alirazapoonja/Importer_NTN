"""
Convert your Excel file into a SQLite database (run this once, and again
whenever your Excel data changes).

Usage:
    python import_data.py importers.xlsx
"""
import sqlite3
import sys

import pandas as pd

DB_FILE = "importers.db"


def find_column(columns, keywords):
    """Return the first column whose name contains any of the keywords."""
    for col in columns:
        name = str(col).strip().lower()
        if any(k in name for k in keywords):
            return col
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_data.py yourfile.xlsx")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Reading {path} ... (a 10 MB file may take a little while)")
    df = pd.read_excel(path, dtype=str)  # dtype=str keeps NTN leading zeros

    print("Columns found:", list(df.columns))

    name_col = find_column(df.columns, ["importer", "name"])
    ntn_col = find_column(df.columns, ["ntn", "tax", "national"])

    if name_col is None or ntn_col is None:
        print("\nCould not detect the columns automatically.")
        print("Edit NAME_COL and NTN_COL in this script with your exact column names.")
        sys.exit(1)

    print(f"Using name column: '{name_col}', NTN column: '{ntn_col}'")

    df = df[[name_col, ntn_col]].dropna(how="all")
    df.columns = ["name", "ntn"]
    df["name"] = df["name"].fillna("").str.strip()
    df["ntn"] = df["ntn"].fillna("").str.strip()
    df = df[df["name"] != ""]
    df["name_lc"] = df["name"].str.lower()

    conn = sqlite3.connect(DB_FILE)
    df.to_sql("importers", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_name_lc ON importers(name_lc)")
    conn.commit()
    conn.close()

    print(f"Done. {len(df)} importers saved to {DB_FILE}")


if __name__ == "__main__":
    main()
