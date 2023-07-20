from load_all_cls import load_all_cls
import pandas as pd
import re

class clusterDf():
    def __init__ (self, cluster_path, meta_path, max_date = 1500, cluster_cap = None, drop_strings = True, columns = ["cluster", "size", "seq", "series", "begin", "end"]):
        self.cluster_df = load_all_cls(cluster_path, meta_path, drop_strings=drop_strings, columns = columns, drop_dates=False, max_date = max_date, cluster_cap = cluster_cap)
    
    def count_books(self):
        return len(self.cluster_df[cluster_df["series"]].drop_duplicates())

    def count_clusters(self):
        return len(self.cluster_df[cluster_df["cluster"]].drop_duplicates())
    
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


if __name__ == "__main__":
    
    clusters = "C:/Users/mathe/Documents/Kitab project/passim/clusters-2022/"
    meta = "E:/Corpus Stats/2021/OpenITI_metadata_2021-2-5_merged_wNoor.csv"
    cluster_df_obj = clusterDf(clusters, meta)
    print(cluster_df_obj.count_books())
    print(cluster_df_obj.count_clusters())
    print(cluster_df_obj.fetch_max_cluster())

    # stats = cluster_df_obj.fetch_top_reusers(uri="0845Maqrizi.Mawaciz", exclude_self_reuse=True, dir="anachron", csv_out = "0845Maqrizi.Mawaciz-reused-texts.csv")