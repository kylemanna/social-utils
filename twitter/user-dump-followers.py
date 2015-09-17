#!/usr/bin/env python3

import tweepy
import json
import sys
import datetime
import argparse

def dump_followers(api):

    followers = []
    for u in tweepy.Cursor(api.followers, count=200).items():
        followers.append({
            'id':u.id,
            'screen_name':u.screen_name,
            'url':u.url,
            'location':u.location,
            'followers_count':u.followers_count
            })

    return followers

def dump_friends(api):

    friends = []
    for u in tweepy.Cursor(api.friends, count=200).items():
        friends.append({
            'id':u.id,
            'screen_name':u.screen_name,
            'name':u.name,
            'url':u.url,
            'location':u.location,
            'followers_count':u.followers_count,
            'friends_count':u.friends_count,
            'statuses_count':u.statuses_count
            })

    return friends


if __name__ == '__main__':
    p = argparse.ArgumentParser()
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

    #print(json.dumps(dump_followers(api), default=date_handler))
    print(json.dumps(dump_friends(api), default=date_handler))
