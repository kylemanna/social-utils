#!/usr/bin/env python3

import json
import tweepy
import argparse
import datetime
import sys
import time

def get_all_list_members(api, owner, slug):
    members = []

    for page in tweepy.Cursor(api.list_members, owner_screen_name=owner, slug=slug).items():
        #print(repr(page))
        members.append(page)

    return [{
        'screen_name':m.screen_name, 
        'followers_count':m.followers_count,
        'id':m.id,
        'following':m.following,
        } for m in members]

def set_followed_by(api, members):
    # Heavily rate limited: 180 requests / 15 min window
    for m in members:
        if 'followed_by' in m: continue
        (source, target) = api.show_friendship(target_id = m['id'])
        m['followed_by'] = source.followed_by

    return members

def auto_follow(api, name, members):
    #new_list = api.create_list('{}-{}'.format(name, int(time.time())), 'private')
    new_list = api.create_list(name, 'private')
    #new_list = api.get_list(owner_screen_name='2bluesc', slug='test')

    for sub in range(0, len(members), 100):
        chunk = members[sub:sub+100]

        params = {
                'list_id':new_list.id,
                'user_id':[m['id'] for m in chunk],
                'screen_name':[m['screen_name'] for m in chunk]
                }

        #print("params: {}".format(params))

        while True:
            # There appears to be a race between list creation and ability to
            # use it, "smart" poll a few times waiting.
            try:
                api.add_list_members(**params)
            except tweepy.error.TweepError as e:
                if e.response.status_code == 404:
                    print('List not created yet, waiting', file=sys.stderr)
                    time.sleep(1)
                    continue
                else:
                    raise
            break


    return {'result':'success'}

def unfollow(api, members):

    for m in members:
        api.destroy_friendship(user_id=m['id'])
    
    return {'result':'success'}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('cmd', help="['get', 'followed', 'auto_follow', 'auto_unfollow'")
    p.add_argument('args', nargs='*')
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
    
    result = {}

    if args.cmd == 'get':
        for name in args.args:
            (owner, slug) = name.split('/')
            result[name] = get_all_list_members(api, owner, slug)

    elif args.cmd == 'followed':
        lists = json.load(sys.stdin)
        for name, members in lists.items():
            result[name] = set_followed_by(api, members)

    elif args.cmd == 'auto_follow':
        lists = json.load(sys.stdin)
        for name, members in lists.items():
            result = auto_follow(api, name, members)
    
    elif args.cmd == 'unfollow':
        lists = json.load(sys.stdin)
        for name, members in lists.items():
            result = unfollow(api, members)

    else:
        print("unknown command \"{}\"".format(args.cmd), file=sys.stderr)
        sys.exit(1)

    
    date_handler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime)
            or isinstance(obj, datetime.date)
            else None
            )
    
    print(json.dumps(result, default=date_handler))
