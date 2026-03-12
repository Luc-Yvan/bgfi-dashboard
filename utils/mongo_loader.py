# -*- coding: utf-8 -*-
"""
utils/mongo_loader.py
─────────────────────
Priorité : MongoDB local → fallback Excel automatique
"""
import os
import pandas as pd
import numpy as np

MONGO_URI       = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME         = "senegal_finance"
COLLECTION_NAME = "banques"

EXCEL_CANDIDATES = [
    r"C:\Users\user\Documents\Data Ingenieur2\Projet_banque\Data\BASE_SENEGAL2_COMPLETE.xlsx",
    os.path.join(os.getcwd(), "Data", "BASE_SENEGAL2_COMPLETE.xlsx"),
]

def _load_from_mongo():
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    col = client[DB_NAME][COLLECTION_NAME]
    records = list(col.find({}, {"_id": 0}))
    client.close()
    if not records:
        raise ValueError("Collection MongoDB vide")
    df = pd.DataFrame(records)
    print(f"[MongoDB] {len(df)} lignes chargees")
    return df

def _load_from_excel():
    path = next((p for p in EXCEL_CANDIDATES if os.path.exists(p)), None)
    if not path:
        raise FileNotFoundError("BASE_SENEGAL2.xlsx introuvable")
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip()
    rename_map = {}
    for c in df.columns:
        new = (c.replace("Û","U").replace("û","u").replace("Ô","O").replace("ô","o")
                .replace("É","E").replace("é","e").replace("È","E").replace("è","e")
                .replace("Î","I").replace("î","i").replace("Â","A").replace("â","a"))
        if new != c: rename_map[c] = new
    df.rename(columns=rename_map, inplace=True)
    print(f"[Excel fallback] {len(df)} lignes chargees")
    return df

def _compute_ratios(df):
    if "ROE" not in df.columns:
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
    if "PART_MARCHE" not in df.columns:
        for y in df["ANNEE"].unique():
            m = df["ANNEE"] == y
            tot = df.loc[m, "BILAN"].sum()
            df.loc[m, "PART_MARCHE"] = (df.loc[m, "BILAN"] / tot) * 100
    if "TCAM_BILAN" not in df.columns:
        def tcam5(b):
            d  = df[df["Sigle"] == b]
            v0 = d[d["ANNEE"] == 2015]["BILAN"].values
            v1 = d[d["ANNEE"] == 2020]["BILAN"].values
            return round(((v1[0]/v0[0])**(1/5)-1)*100, 1) if len(v0) and len(v1) and v0[0]>0 else np.nan
        df["TCAM_BILAN"] = df["Sigle"].map({b: tcam5(b) for b in df["Sigle"].unique()})
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df

def load_data():
    """MongoDB local en priorité, Excel en fallback automatique."""
    df = None
    source = None
    try:
        df = _load_from_mongo()
        source = "mongodb"
    except Exception as e:
        print(f"MongoDB indisponible ({type(e).__name__}) -> fallback Excel")
    if df is None:
        try:
            df = _load_from_excel()
            source = "excel"
        except Exception as e:
            print(f"Excel introuvable : {e}")
            return pd.DataFrame()
    df = _compute_ratios(df)
    print(f"Source : {source} — {df['Sigle'].nunique()} banques · {sorted(df['ANNEE'].unique().tolist())}")
    return df