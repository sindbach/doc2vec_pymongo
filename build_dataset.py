# Source: src/build_dataset.py
# -*- coding: utf-8 -*-
import json
import requests

OMDB_URL = "http://www.omdbapi.com/?i=tt%s&plot=full&r=json"

fdata = open("./data/tagged_plots.json", 'wb')
flink = open("./data/links.csv", 'rb')
for line in flink:
    if line.startswith("movieId"):
        continue
    mid, imdb_id, _ = line.strip().split(",")
    resp = requests.get(OMDB_URL % (imdb_id))
    resp_json = json.loads(resp.text)
    json.dump(resp_json, fdata)
    fdata.write("\n")
flink.close()
fdata.close()


'''
mongoimport --db topics --collection movies --file ./data/tagged_plots.json
'''