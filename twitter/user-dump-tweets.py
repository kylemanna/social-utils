#!/usr/bin/env python3

import tweepy
import json
import sys
import datetime
import argparse

def dump_tweets(api, screen_name):

    # Twitter only allows access to a users most recent 3240 tweets with this method
    tweets = []
    for t in tweepy.Cursor(api.user_timeline, count=200).items():
        tweets.append({'id':t.id, 'created_at':t.created_at, 'text':t.text})

    return tweets


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('screen_name')
    args = p.parse_args()

    """ Expect a json file of following format:
    {
      "consumer_key": "something",
      "consumer_secret": "something different",
      "access_key": "somenumber-something else",
      "access_secret": "something else secret like"
    }

    """
    with open('credentials.json', 'r') as fp:
        cred = json.load(fp)

    # Authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
    auth.set_access_token(cred['access_key'], cred['access_secret'])
    api = tweepy.API(auth)

    date_handler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime)
            or isinstance(obj, datetime.date)
            else None
            )

    print(json.dumps(dump_tweets(api, args.screen_name), default=date_handler))
