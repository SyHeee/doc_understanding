import numpy as np
import pandas as pd 
# import torch.nn as nn
# import pytorch_lightning as pl
# import torch.nn.functional as F
# from torch.utils.data import Dataset, DataLoader
# import torch
from collections import Counter


def read_data(path, file=""):    
    if file == "behaviors":
        schema = ["impressionId","userId","timestamp","click_history","impressions"]
    elif file == "news":
        schema = ["itemId","category","subcategory","title","abstract","url","title_entities","abstract_entities"]
    else:
        return pd.read_csv(path, sep="\t",header=None)

    return pd.read_csv(path, sep="\t",names=schema)

if __name__=="__main__": 
    df_behaviors =  read_data("../Data/MINDsmall_train/behaviors.tsv", file="behaviors")
    df_news =  read_data("../Data/MINDsmall_train/news.tsv", file="news")
    
    # build counters for impression and click
    tmp = ' '.join(df_behaviors["impressions"].tolist()).split(' ')
    impression_counter = Counter([news[:-2] for news in tmp])
    click_counter = Counter([news[:-2] for news in tmp if news[-2:]=="-1"])
    
    df_impression = pd.merge(pd.DataFrame.from_dict({"itemId":impression_counter.keys(),\
        "impressions":impression_counter.values()}),\
            pd.DataFrame.from_dict({"itemId":click_counter.keys(),\
        "clicks":click_counter.values()}), on="itemId", how="left"
            )
    df_impression = df_impression.fillna(0)
    df_impression["isClick"] = 0
    df_impression.loc[(df_impression["impressions"]>1)&(df_impression["clicks"]/df_impression["impressions"]>0.05),"isClick"] = 1
    # df_impression["isClick"].value_counts()
    # 0    16439
    # 1     3849
    # Name: isClick, dtype: int64
    df_impression = pd.merge(df_impression, df_news[["itemId","category","subcategory","title","abstract"]], on="itemId", how="inner")
    df_impression.to_csv("../Data/parsed_train.csv",sep="\t",index=False)