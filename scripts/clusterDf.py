from load_all_cls import load_all_cls
import pandas as pd
import re
import os

class clusterDf():
    def __init__ (self, cluster_path, meta_path, min_date=0, max_date = 1500, cluster_cap = 500, drop_strings = True, columns = ["uid", "gid", "cluster", "size", "seq", "series", "text", "begin", "end"]):
        self.cluster_df = load_all_cls(cluster_path, meta_path, drop_strings=drop_strings, columns = columns, drop_dates=False, max_date = max_date, min_date=min_date, cluster_cap = cluster_cap)
    
    def count_books(self):
        return len(self.cluster_df[self.cluster_df["series"]].drop_duplicates())

    def count_clusters(self):
        return len(self.cluster_df[self.cluster_df["cluster"]].drop_duplicates())
    
    def fetch_max_cluster(self):
        return self.cluster_df["size"].max()

    def fetch_top_reusers(self, uri, uri_field="book", by = "length", exclude_self_reuse = False, dir = "bi", csv_out=None):
        # Set up pre-requisites to be used by other funcs
        self.exclude_self_reuse = exclude_self_reuse
        
        # Find death date of author and determine whether to filter before or after
        if dir != "bi":
            uri_death_date = int(re.findall("\d+", uri)[0])
            print(uri_death_date)
            if dir == "anachron":
                df_in = self.cluster_df[self.cluster_df["date"] < uri_death_date]
            elif dir == "chron":
                df_in = self.cluster_df[self.cluster_df["date"] > uri_death_date]
        else:
            df_in = self.cluster_df
        
        # Send filtered df to the calcuate function
        stats_df = self.calculate_reuse_stats(uri, uri_field=uri_field, df_in = df_in) 

        # Sort and return df
        stats_df = stats_df.sort_values(by=by, ascending=False)

        if csv_out:
            stats_df.to_csv(csv_out, index=False)
        
        return stats_df

    # Use a URI to fetch a list of clusters
    def fetch_clusters_by_uri(self, uri, uri_field = "book"):
        return self.cluster_df[self.cluster_df[uri_field] == uri]["cluster"].to_list()
    
    # Concatenate the uris in a cluster set
    def calculate_reuse_stats(self, uri, uri_field="book", df_in = None):
        cluster_list = self.fetch_clusters_by_uri(uri, uri_field=uri_field)        
        
        if df_in is None:
            df_in = self.cluster_df
        
        df_in = df_in[df_in["cluster"].isin(cluster_list)]    
        print(df_in)
        if self.exclude_self_reuse:
            
            df_in["author"] = df_in["book"].str.split(".", expand=True)[0]
            uri_author = uri.split(".")[0]
            df_in = df_in[df_in["author"] != uri_author]
        
        uri_list = df_in["book"].drop_duplicates().to_list()
        if uri in uri_list:
            uri_list.remove(uri)
        stat_dicts = []
        for uri in uri_list:
            uri_df = df_in[df_in["book"] == uri]
            uri_df["length"] = uri_df["end"] - uri_df["begin"]
            stat_dicts.append({"uri": uri, "length": uri_df["length"].sum(), "instances": len(uri_df)})
        
        return pd.DataFrame(stat_dicts)

    def filter_by_author_list(self, author_list):
        print("Filtering clusters by authors: {}".format(author_list))
        author_df = self.cluster_df.copy()
        author_df["author"] = author_df["book"].str.split(".", expand=True)[0]        
        self.cluster_df = author_df[author_df["author"].isin(author_list)]
        self.cluster_df.drop(columns=["author"])
    
    def filter_by_book_list(self, book_list, exclude_listed_books=False):
        """If exclude_listed_books is true - it will return the only rows that do not match the book list"""
        if exclude_listed_books:
            print("Filtering clusters to exclude books: {}".format(book_list))
            self.cluster_df = self.cluster_df[~self.cluster_df["book"].isin(book_list)]
        else:
            print("Filtering clusters by books: {}".format(book_list))
            self.cluster_df = self.cluster_df[self.cluster_df["book"].isin(book_list)]

    def to_minified_csv(self, out_path, columns = ["cluster", "id", "seq", "begin", "end", "size"]):
        minified_csv = self.cluster_df[columns]
        minified_csv.to_csv(out_path)

if __name__ == "__main__":
    print(os.getcwd())
    clusters = "D:/Corpus Stats/2023/v7-clusters/out.json"
    meta = "D:/Corpus Stats/2023/OpenITI_metadata_2022-2-7_merged.csv"
    out_csv = "D:/Corpus Stats/2023/v7-clusters/minified_clusters_pre-1000AH_under500.csv"
    cluster_df_obj = clusterDf(clusters, meta, max_date = 1000, cluster_cap=500)
    cluster_df_obj.to_minified_csv(out_csv)
