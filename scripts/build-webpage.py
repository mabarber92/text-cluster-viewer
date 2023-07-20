from create_cluster_jsons import create_cluster_jsons
import os
import re
import shutil

def build_webpage(cluster_path, meta_path, main_book_uri, corpus_base_path, output_path, ms_per_json = 5, start_ms = 1, end_ms = None, page_title=None, viewer_template_folder = "../templates/"):

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
    shutil.copytree(assets_folder, assets_dest)
    
    print("Created html page")

    # Run the json compiler in the same directory
    create_cluster_jsons(cluster_path, meta_path, main_book_uri, corpus_base_path, output_path, ms_per_json = ms_per_json, start_ms = start_ms, end_ms = end_ms)

    print("Success")

if __name__ == "__main__":
    corpus_base_path = "D:/OpenITI Corpus/corpus_10_21/"
    meta_path = "D:/Corpus Stats/2021/OpenITI_metadata_2021-2-5.csv"
    cluster_path = "D:/Corpus Stats/2021/Cluster data/Oct_2021/parquet"
    output_path = "../Maqrizi.ItticazHunafa-fitna/"
    main_text = "0845Maqrizi.ItticazHunafa"
    title = "0845Maqrizi.ItticazHunafa-fitna-ms<br>Clusters-Version-2021.2.5"

    build_webpage(cluster_path, meta_path, main_text, corpus_base_path, output_path, start_ms=360, end_ms=394, page_title=title)



