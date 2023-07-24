from clusterDf import clusterDf
import re
import pandas as pd
import os
import json
from tqdm import tqdm
from openiti.helper.funcs import text_cleaner
import sys

def tag_ms(clusters, ms_section, safe_tags="###\s\|+\s|\n#\s|###\s\|+\s|PageV\d+P\d+|~~|\n|%~%", tags = None):
    """The function that handles tagging the clusters into an individual milestone
    and returns the tagged milestone"""
    # Only clean and tag out cluster if clusters exist                    
    if type(clusters) is not list:
        clusters = [clusters]
    if len(clusters) > 0:
        
        tagidxs_dict = []
        # If there are tags used to select the milestone -  For all tags log their index positions in the text, taking account for the cleaning operation
        if tags is not None:
            for each_tag in tags:
                tempsplits = re.split(each_tag, ms_section)
                
                for tidx, tempsplit in enumerate(tempsplits[:-1]):
                    indexpos = len(text_cleaner(" ".join(tempsplits[0:tidx+1])))
                    tagidxs_dict.append({"tag": each_tag, "index": indexpos, "tagged": False, "pos": 1000})
        
        # For all safe_tags log their index positions in the text, taking account for the cleaning operation
        
        # if len(safe_tags) > 1:    
        #     tag_regex = safe_tags[0]
        #     for safe_tag in safe_tags[1:]:
        #         tag_regex = tag_regex + "|" + safe_tag
        # else:
        #     tag_regex = safe_tags[:]
        splitter_tag = r"(" + safe_tags + ")"
        if len(re.findall(splitter_tag, ms_section)) > 0:
            tempsplits = re.split(splitter_tag, ms_section)
            for tidx, tempsplit in enumerate(tempsplits[:-1]):
                if not re.match(safe_tags, tempsplit):
                    indexpos = len(text_cleaner(" ".join(tempsplits[0:tidx+1])))
                    tagidxs_dict.append({"tag": tempsplits[tidx+1], "index": indexpos, "tagged": False, "pos": tidx})

                else:
                    continue
            
        # Convert the resulting dictionary into a df sort it by index (to facilitate mapping) and reconvert to dictionary    
        if len(tagidxs_dict) > 0:
            tagidxs_dict = pd.DataFrame(tagidxs_dict).sort_values(by = ["index", "pos"]).to_dict("records")    
        
        
        
        # Clean the milestone text ready for clusters mapping
        new_ms_text = text_cleaner(ms_section[:])
        
        # Create a mapping dictionary using the token offsets of the clusters - begin and end
        mapping_dict = []
        for cluster in clusters:
            
            
            mapping_dict.append({"cluster": cluster["cluster"], "type" : " @clb@" + str(cluster["size"]) + "@", "index" : cluster["begin"]})
            mapping_dict.append({"cluster": cluster["cluster"], "type" : " @cle@", "index" : cluster["end"]})
            
            
        # Convert the resulting dictionary into a df sort it by index (to facilitate mapping) and reconvert to dictionary      
        mapping_dict = pd.DataFrame(mapping_dict).sort_values(by = ["index"]).to_dict("records")    
        
        # offset is the cumulitive count of character insertions into the text - everytime a tag is added to the text the offset is incremented by the length of the tag (this stops drift)
        offset = 0
        # We keep track of number of tags inserted - so when there are no tags remaining we stop looping through the tag dictionary
        tagged_count = 0
        total_tags = len(tagidxs_dict)
        # For each cluster mapping insert a tag        
        for mapping in mapping_dict:
            reusetag = mapping["type"] + str(mapping["cluster"]) + "@ "
            index = mapping["index"]
            if tagged_count != total_tags:
                for tagidx in tagidxs_dict:
                    # If there is a tag in the tag dictionary that occurs prior to the cluster tag and it has not yet been tagged - insert the tag
                    if tagidx["index"] < index and tagidx["tagged"] is False:
                        new_ms_text = new_ms_text[: tagidx["index"] + offset] + tagidx["tag"] + new_ms_text[tagidx["index"] + offset :]
                        offset = offset + len(tagidx["tag"])
                        tagidx["tagged"] = True                                               
                        tagged_count = tagged_count + 1
            # Once any tags have been handled - insert the cluster tag
            new_ms_text = new_ms_text[: mapping["index"] + offset] + reusetag + new_ms_text[mapping["index"] + offset :]
            offset = offset + len(reusetag)
        # If there are any remaining untagged tags after all clusters have been tagged out - make sure these are tagged too (this handles any tags that appear after all of the cluster tags)
        if tagged_count != total_tags:
            for tagidx in tagidxs_dict:
                if tagidx["tagged"] is False:
                    new_ms_text = new_ms_text[: tagidx["index"] + offset] + tagidx["tag"] + new_ms_text[tagidx["index"] + offset :]
                    tagidx["tagged"] = True
                    offset = offset + len(tagidx["tag"])
        return new_ms_text
    else:
        return ms_section
   

def create_corpus_paths(meta_df, openiti_corpus_base):
    meta_df["rel_path"] = openiti_corpus_base + meta_df["local_path"].str.split("/master/|\.\./", expand = True, regex=True)[1]
    return meta_df

def create_ms_slice(current_ms, zfill_count, text, ms_spread = [1,1]):
    slice_list = [int(current_ms) - 1 - ms_spread[0], int(current_ms) + ms_spread[1]]
    updated_slice = []
    for slice in slice_list:
        updated_slice.append(str(slice).zfill(zfill_count))

    regex = r"ms{}.*ms{}".format(updated_slice[0], updated_slice[1])

    slice = re.findall(regex, text, flags=re.DOTALL)
    if len(slice) == 0:        
        new_regex = r"ms{}.*".format(updated_slice[0])
        slice = re.findall(new_regex, text, flags=re.DOTALL)
        if len(slice) == 0:            
            new_regex = r"End#.*ms{}".format(updated_slice[1])
            slice = re.findall(new_regex, text, flags=re.DOTALL)
            if len(slice) == 0:
                print("function create_ms_slice : writing error")
                returned = "Corresponding MS not found"
            else:
                returned = slice[0]
        else:
            returned = slice[0]
    else:
        returned = slice[0]
    return returned

def mARkdown_to_html(text, mark_cls = True):
    # Wrap all headers with one header type    
    text = re.sub(r"###\s[$|]+(.*)\n", r"<h4 class=markdownHeader><mark class='markHead'>\1</mark></h4>", text)
    # Replace # with <br>
    text = re.sub(r"#\s", "<br>",text)
    # Add highlighting to milestone markers
    text = re.sub(r"(ms\d+)", r"<mark class='ms'>\1</mark>", text)
    # Add highlighting to page markers
    text = re.sub(r"(PageV\d+P\d+)", r"<mark class='pageno'> \1 </mark>", text)
    # Add highlighting to poetry markers
    text = re.sub(r"(%~%)", r"<mark class='poetryMark'> \1 </mark>", text)
    # If mark_cls is true - highlight the cluster markers
    if mark_cls:
        text = re.sub(r"(@clb@\d+@\d+@)", r"<mark class='clusterStart'>\1</mark>", text)
        text = re.sub(r"(@cle@\d?@?\d+@)", r"<mark class='clusterEnd'>\1</mark>", text)
    # return the text
    return text

def create_cluster_jsons(cluster_path, meta_path, main_book_uri, corpus_base_path, output_path, pri_only_corpus=False, drop_strings=False, ms_per_json = 5, start_ms = 1, end_ms = None):

    # If needed build output directory
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # Fetch the clusters
    cluster_df = clusterDf(cluster_path, meta_path, drop_strings=drop_strings, cluster_cap = 100, max_date=1000).cluster_df
    
    # Get a fitered df for the main text
    main_clusters_df = cluster_df[cluster_df["book"] == main_book_uri]

    # Create a path of texts for querying
    meta_df = pd.read_csv(meta_path, sep="\t")
    meta_df = meta_df[meta_df["status"] == "pri"]
    meta_df = create_corpus_paths(meta_df, corpus_base_path)

    # Open and store text
    if not pri_only_corpus:
        main_text_path = meta_df[meta_df["book"] == main_book_uri]["rel_path"].to_list()[0]
    else:
        text_uri = meta_df[meta_df["book"] == main_book_uri]["rel_path"].to_list()[0].split("/")[-1]
        main_text_path = os.path.join(corpus_base_path, text_uri)
    
    # If the path doesn't exist - try removing the extension
    if not os.path.exists(main_text_path):
        main_text_path = (".").join(main_text_path.split(".")[:-1])
        if not os.path.exists(main_text_path):
            print("Main text not found: {}".format(main_text_path))
            sys.exit()
    with open(main_text_path, encoding="utf-8-sig") as f:
        main_text = f.read()
    
        
    # Get the milestone count and z-fill for main text
    ms_list = re.findall(r"ms(\d+)", main_text)
    ms_count = len(ms_list)
    zfill_len_main = len(ms_list[0])


    # Create the main output list
    main_ms_list = []

    if end_ms is None:
        end_ms = ms_count


    # Loop through the milestones up to total number in book (slicing the output according to ms_per_json variable) and build the jsons by looking up the clusters in clusters_df
    # Need to add the mapping component to map in the clusters into the text
    print(start_ms)
    print(end_ms)

    for i in tqdm(range(start_ms, end_ms, ms_per_json)):
        cluster_json_path = "./{}_{}_clusters.json".format(i, i+ms_per_json)
        clusters_out = []
        for x in range(i, i+ms_per_json):
            
            filtered_clusters = main_clusters_df[main_clusters_df["seq"]==x].to_dict("records")

            # Get the ms_slice and format it in html to store in json
            ms_text = create_ms_slice(x, zfill_len_main, main_text, ms_spread=[0,0])
            ms_text = tag_ms(filtered_clusters, ms_text)
            ms_text = mARkdown_to_html(ms_text)

            # Loop through clusters and create that part of the output file
            clusters_for_ms = []
            # clusters_for_out = []
            for cluster in filtered_clusters:
                ms_list = cluster_df[cluster_df["cluster"] == cluster["cluster"]].sort_values(by=["book"]).to_dict("records")

                cluster_ms_text = []
                for cluster_ms in ms_list:
                    if not pri_only_corpus:
                        comp_text_path = meta_df[meta_df["book"] == cluster_ms["book"]]["rel_path"].to_list()[0]
                    else:
                        text_uri = meta_df[meta_df["book"] == cluster_ms["book"]]["rel_path"].to_list()[0].split("/")[-1]
                        comp_text_path = os.path.join(corpus_base_path, text_uri)
                    
                    use_markdown=True
                    # If the path doesn't exist - try removing the extension - if that fails use just the plain text from the cluster - if drop strings has been set to false
                    if not os.path.exists(comp_text_path):
                        comp_text_path = (".").join(comp_text_path.split(".")[:-1])
                        if not os.path.exists(comp_text_path):
                            print("Main text not found: {} ... using cluster text instead of markdown".format(comp_text_path))
                            use_markdown = False
                            if not drop_strings:
                                comp_ms_text = cluster_ms["text"]
                            else:
                                comp_ms_text = "Corresponding mARkdown not found"
                        
                    if use_markdown:
                        with open(comp_text_path, encoding='utf-8-sig') as f:
                            comp_text = f.read()
                        zfill_comp = len(re.findall(r"ms(\d+)", comp_text)[0])
                        comp_ms_text = create_ms_slice(cluster_ms["seq"], zfill_comp, comp_text, ms_spread=[0,0])
                        comp_ms_text = tag_ms(cluster_ms, comp_ms_text)
                        comp_ms_text = mARkdown_to_html(comp_ms_text)
                    
                    cluster_ms_text.append({"ms_id": cluster_ms["book"] + "-" + str(cluster_ms["seq"]), "text": comp_ms_text})
                
                clusters_out.append({"cl_id": cluster["cluster"], "texts": cluster_ms_text})
                clusters_for_ms.append({"cl_id": cluster["cluster"], "ms_count": len(ms_list)})
            
            ms_dict = {"ms": x, 
                        "text": ms_text,
                        "cls_count": len(filtered_clusters),
                        "cls": clusters_for_ms,
                        "cl_json": cluster_json_path
                        }
            
            main_ms_list.append(ms_dict)

            # clusters_dict = {"ms": x,
            #                 "cls": clusters_for_out}
            # clusters_out.append(clusters_dict)
        
        json_path = os.path.join(output_path, cluster_json_path)
        with open(json_path, "w", encoding="utf-8-sig") as f:
            f.write(json.dumps(clusters_out, indent=1))
    
    main_json_path = os.path.join(output_path, "index.json")
    with open(main_json_path, "w", encoding="utf-8-sig") as f:
            f.write(json.dumps(main_ms_list, indent=1))
                






