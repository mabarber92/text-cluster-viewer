# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:38:58 2022

@author: mathe
"""
import pandas as pd
import pyarrow.parquet as pq
import os
from tqdm import tqdm

def load_all_cls(parquet_path, meta_path, max_date = 900, cluster_cap = 500, columns = ["uid", "gid", "cluster", "size", "seq", "series", "text", "begin", "end"], drop_strings = False, drop_dates = True):
    
    meta_df = pd.read_csv(meta_path, sep="\t")[["id", "book", "date"]]

    all_cls = pd.DataFrame()
    if "size" not in columns:
        columns.append("size")
    if "series" not in columns:
        columns.append("series")
    print("Loading all clusters below: " + str(cluster_cap))
    print(parquet_path)
    for root, dirs, files in os.walk(parquet_path, topdown=False):
        for name in tqdm(files):
            if name.split(".")[-1] == "parquet":
                pq_path = os.path.join(root, name)
                if drop_strings:
                    if "text" in columns:
                        columns.remove("text")
                        
                data = pq.read_table(pq_path).to_pandas()[columns]

                if cluster_cap is not None:
                    data = data[data["size"] < cluster_cap]

                data["id"] = data["series"].str.split("-").str[0]
                data = pd.merge(data, meta_df, how = "inner", on ="id") 
                # Applying the date filter to output
                data = data[(data["date"] <= max_date)]
                if drop_dates:
                    data= data.drop(columns = ["date"])

                all_cls = pd.concat([all_cls, data])
    
    
    
    # Use metadata to filter according to requirements
    # Add book URI to make easier to read outputs
    


    print("New cluster data loaded...")

    
    
    return all_cls

