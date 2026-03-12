# -*- coding: utf-8 -*-
"""
migrate_to_mongo.py
Lancer UNE SEULE FOIS : python migrate_to_mongo.py
"""
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError

MONGO_URI       = "mongodb://localhost:27017"
DB_NAME         = "senegal_finance"
COLLECTION_NAME = "banques"
EXCEL_PATH      = r"C:\Users\user\Documents\Data Ingenieur2\Projet_banque\Data\BASE_SENEGAL2_COMPLETE.xlsx"

def load_excel(path):
    print(f"Lecture de {path}...")
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip()
    rename_map = {}
    for c in df.columns:
        new = (c.replace("Û","U").replace("û","u").replace("Ô","O").replace("ô","o")
                .replace("É","E").replace("é","e").replace("È","E").replace("è","e")
                .replace("Î","I").replace("î","i").replace("Â","A").replace("â","a"))
        if new != c: rename_map[c] = new
    df.rename(columns=rename_map, inplace=True)

    df["ROE"]          = (df["RESULTAT.NET"]         / df["FONDS.PROPRE"]) * 100
    df["ROA"]          = (df["RESULTAT.NET"]         / df["BILAN"])        * 100
    df["LEVIER"]       =  df["BILAN"]                / df["FONDS.PROPRE"]
    df["RISQUE_PCT"]   = (df["COUT.DU.RISQUE"]       / df["BILAN"])        * 100
    df["RATIO_TRANSF"] = (df["EMPLOI"]               / df["BILAN"])        * 100
    df["PNB_BILAN"]    = (df["PRODUIT.NET.BANCAIRE"] / df["BILAN"])        * 100
    df["EMP_AG"]       =  df["EMPLOI"]   / df["AGENCE"]
    df["RES_AG"]       =  df["RESSOURCES"] / df["AGENCE"]
    df["EMP_EFF"]      =  df["EMPLOI"]   / df["EFFECTIF"]
    df["RES_EFF"]      =  df["RESSOURCES"] / df["EFFECTIF"]

    for y in df["ANNEE"].unique():
        m = df["ANNEE"] == y
        tot = df.loc[m, "BILAN"].sum()
        df.loc[m, "PART_MARCHE"] = (df.loc[m, "BILAN"] / tot) * 100

    def tcam5(b):
        d  = df[df["Sigle"] == b]
        v0 = d[d["ANNEE"] == 2015]["BILAN"].values
        v1 = d[d["ANNEE"] == 2020]["BILAN"].values
        return round(((v1[0]/v0[0])**(1/5)-1)*100, 1) if len(v0) and len(v1) and v0[0]>0 else None

    df["TCAM_BILAN"] = df["Sigle"].map({b: tcam5(b) for b in df["Sigle"].unique()})
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notna(df), None)
    print(f"OK : {len(df)} lignes — {df['Sigle'].nunique()} banques — {df['ANNEE'].nunique()} annees")
    return df

def migrate(df):
    print(f"\nConnexion a MongoDB local ({MONGO_URI})...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("Connexion reussie !")

    col = client[DB_NAME][COLLECTION_NAME]
    existing = col.count_documents({})
    if existing > 0:
        confirm = input(f"\n{existing} documents deja presents. Ecraser ? (oui/non) : ")
        if confirm.lower() != "oui":
            print("Migration annulee.")
            client.close()
            return
        col.delete_many({})
        print("Collection videe.")

    records = df.to_dict(orient="records")
    print(f"\nInsertion de {len(records)} documents...")
    try:
        result = col.insert_many(records, ordered=False)
        print(f"OK : {len(result.inserted_ids)} documents inseres dans '{DB_NAME}.{COLLECTION_NAME}'")
    except BulkWriteError as e:
        print(f"Partiel : {e.details['nInserted']} inseres, {len(e.details['writeErrors'])} erreurs")

    col.create_index([("Sigle", ASCENDING), ("ANNEE", ASCENDING)], unique=True)
    col.create_index("ANNEE")
    col.create_index("Sigle")
    col.create_index("Goupe_Bancaire")
    print("Index crees")

    print(f"\nResume : {col.count_documents({})} documents · {len(col.distinct('Sigle'))} banques · {sorted(col.distinct('ANNEE'))}")
    print(f"\nMigration terminee ! Base : '{DB_NAME}' · Collection : '{COLLECTION_NAME}'")
    client.close()

if __name__ == "__main__":
    df = load_excel(EXCEL_PATH)
    migrate(df)