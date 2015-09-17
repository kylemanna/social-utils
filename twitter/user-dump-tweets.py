#!/usr/bin/env python3

import tweepy
import json
import sys
import datetime
import argparse

def dump_tweets(api, screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    alltweets = []

    # Make initial request for most recent tweets (200 is the maximum allowed)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    # Save most recent tweets
    alltweets.extend(new_tweets)

    # Save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # Keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        #print("getting tweets before {}".format(oldest), file=sys.stderr)

        # All subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        # Save most recent tweets
        alltweets.extend(new_tweets)

        # Update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("Downloaded {:4} tweets".format(len(alltweets)), file=sys.stderr)

    return [{'id':tweet.id_str, 'created_at':tweet.created_at, 'text':tweet.text} for tweet in alltweets]

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
