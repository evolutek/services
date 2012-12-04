#!/usr/bin/env python3
from twitter import *

from cellaserv.service import Service

from local_settings import OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, \
        CONSUMER_SECRET

class TweetService(Service):

    service_name = "twitter"

    def __init__(self):
        super().__init__()

        self.t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY,
            CONSUMER_SECRET))

    @Service.action
    def tweet(self, tweet):
        self.t.statuses.update(status=tweet)

def main():
    service = TweetService()
    service.run()

if __name__ == '__main__':
    main()
