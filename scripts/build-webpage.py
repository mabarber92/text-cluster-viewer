from create_cluster_jsons import create_cluster_jsons
import os
import re
import shutil
import pandas as pd

def build_webpage(cluster_path, meta_path, main_book_uri, corpus_base_path, output_path, pri_only_corpus=False, ms_per_json = 5, start_ms = 1, end_ms = None, list_ms=None, page_title=None, viewer_template_folder = "../templates/"):

    # Create output directory
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    print("Created directory")

    # Move the template into the new directory - give it a title
    viewer_template = os.path.join(viewer_template_folder, "viewer_template.html")
    with open(viewer_template) as f:
        html = f.read()
    
    if page_title is None:
        page_title = main_book_uri
    
    html = re.sub(r"@page_title@", page_title, html)

    html_path = os.path.join(output_path, "index.html")
    with open(html_path, "w") as f:
        f.write(html)
    
    assets_folder = os.path.join(viewer_template_folder, "assets")
    assets_dest = os.path.join(output_path, "assets")
    # if os.path.exists(assets_dest):
    #     os.remove(assets_dest)
    shutil.copytree(assets_folder, assets_dest)
    
    print("Created html page")

    # Run the json compiler in the same directory
    create_cluster_jsons(cluster_path, meta_path, main_book_uri, corpus_base_path, output_path, pri_only_corpus=pri_only_corpus, ms_per_json = ms_per_json, start_ms = start_ms, end_ms = end_ms, list_ms=list_ms)

    print("Success")

if __name__ == "__main__":
    corpus_base_path = "D:/OpenITI Corpus/corpus_2023_1_8/"
    meta_path = "D:/Corpus Stats/2023/OpenITI_metadata_2023-1-8.csv"
    cluster_path = "D:/Corpus Stats/2023/v8-clusters/minified_clusters_pre-1000AH_under500.csv"
    output_path = "../0845Maqrizi.Mawaciz.Fatimid-sections/"
    main_text = "0845Maqrizi.Mawaciz"
    title = "0845Maqrizi.Mawaciz.Fatimid-sections<br>Clusters-Version-2023.1.8"
    start_ms = 792
    end_ms = 1115

    # list_ms = pd.read_csv("./data_in/0845Maqrizi.Mawaciz.Shamela0011566-ara1.csv")["ms"].to_list()

    build_webpage(cluster_path, meta_path, main_text, corpus_base_path, output_path, page_title=title, start_ms = start_ms, end_ms = end_ms, ms_per_json = 10
    )



