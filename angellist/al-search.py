#!/usr/bin/env python3
'''
Angellist Web Search Scraper

Author: Kyle Manna

The goal of htis tool is to scrape the Angellist search results becaues the
Search API [1] only returns 20 results with no pagination at the time of
this writing (2015.09.06).

It's super hacky but works.  Pass in query arguments on the command line.  The
script will return a massive json array with all the results (de-paginated).

It's recommended to test the search query strings ahead of time using a web
browser @ https://angel.co/search?q=query1

Currently it's hardcoded to only search for people matching the queries.

Usage: ./al-search.py query1 query2

[1] https://angel.co/api/spec/search

'''

import json
import urllib.request
from pyquery import PyQuery as pq
import argparse

def search(query):
    result = []
    url = 'https://angel.co/search'
    values = {
            'page':0,
            'per_page':40,
            'skip_loading':'true',
            'include_ids':'',
            'q':query,
            'type':'people',
            }

    headers = { 'Accept': '*/*' }

    while True:
        values['page'] = values['page'] + 1
        full_url = url + '?' + urllib.parse.urlencode(values)
        req = urllib.request.Request(full_url, headers=headers, method='GET')

        with urllib.request.urlopen(req) as response:
            html_doc = json.loads(response.read().decode('utf-8'))['html']

        entries = pq(html_doc)('.result')
        if len(entries) == 0: break

        for entry in entries:
            obj = {}

            entry = pq(entry)

            title = entry('.title')
            a = title('a')
            obj['href'] = a.attr['href']
            obj['name'] = a.text()
            obj['slug'] = obj['href'].rsplit('/',1)[-1]

            obj['type'] = entry('.type').text().strip()
            
            obj['pic'] = entry('img').attr['src']
            
            bio = entry('.excerpt')
            if bio:
                obj['bio'] = bio.text().strip()[1:-2]

            result.append(obj)

    return result

if __name__ == '__main__':

    p = argparse.ArgumentParser()
    p.add_argument('query', nargs='+')
    args = p.parse_args()


    result = []

    for q in args.query:
        result.extend(search(q))

    print(json.dumps(result))
