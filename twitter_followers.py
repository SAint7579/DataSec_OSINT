import time
import tweepy
twitter_consumer_key = VuQI7en91TTuQwBws8FDKt1nX
twitter_consumer_secret = iwBUIkkgUeBRjCMgu8Yd8e51w476n8odlorSWqBTdvrMWBRoFV
twitter_access_token = 1259607799127896064-QkmVJvUuY8GJzszJdNHYHALQUPDIuD
twitter_access_secret = 5wosy5sWq8OPR9TfQjVCUQyQojL1MpxTTIEukmzk7LujY


def get_twitter_followers(screenname):
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)

    api = tweepy.API(auth)

    ids = []
    for page in tweepy.Cursor(api.followers_ids, screen_name=screenname).pages():
        ids.extend(page)

    follower_list = []
    for i in ids:
        u = api.get_user(i)
        follower_list.append(u.name)
        
    return follower_list


def get_twitter_following(screenname):
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)

    api = tweepy.API(auth)

        ids = []
    for page in tweepy.Cursor(api.friends_ids, screen_name=screenname).pages():
        ids.extend(page)

    following_list = []
    for i in ids:
        u = api.get_user(i)
        following_list.append(u.name)

    return following_list


def get_twitter_user_tweets(screenname, count=10):
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)

    api = tweepy.API(auth)

    try:
        tweets = api.user_timeline(screen_name=screenname, count=count, tweet_mode='extended')
        tweet_list = []
        for tweet in tweets:
            tweet_list.append({
                'Tweet ID': tweet.id_str,
                'Text': tweet.full_text,
                'Created At': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Retweets Count': tweet.retweet_count,
                'Favorites Count': tweet.favorite_count
            })
        return tweet_list
    except tweepy.TweepError as e:
        return [{'Error': str(e)}]
