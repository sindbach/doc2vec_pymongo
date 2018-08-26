#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests

API_KEY = os.environ.get("OMDB_API")
OMDB_URL = "http://www.omdbapi.com/?i=tt%s&plot=full&r=json&apikey=%s"

def main():
    fdata = open("./data/extra_data.json", 'w')
    flink = open("./ml-latest-small/links.csv", 'r')
    for line in flink:
        if line.startswith("movieId"):
            continue
        mid, imdb_id, _ = line.strip().split(",")
        resp = requests.get(OMDB_URL % (imdb_id, API_KEY))
        print(imdb_id)
        print(resp.text)
        resp_json = json.loads(resp.text)
        if "Error" in resp_json:
            print("Encountered an error.")
            break
        json.dump(resp_json, fdata)
        fdata.write("\n")
    flink.close()
    fdata.close()

if __name__ == "__main__":
    main()
