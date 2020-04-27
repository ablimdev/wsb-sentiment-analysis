import praw
import reddit_credentials
from textblob import TextBlob
import numpy as np
import re



class RedditAuthenticator():
    def authenticate_reddit_app(self):
        return praw.Reddit(client_id=reddit_credentials.CLIENT_ID,
                           client_secret=reddit_credentials.CLIENT_SECRETS, user_agent=reddit_credentials.USER_AGENT)


class RedditClient():
    def __init__(self):
        self.r_authenticator = RedditAuthenticator()

    def get_top_comments_by_submission_url(self, url):
        """
        gets top comments by submission URL
        """
        reddit = self.r_authenticator.authenticate_reddit_app()
        submission = reddit.submission(url=url)

        comment_list = []

        submission.comments.replace_more(limit=0)
        for top_level_comment in submission.comments:
            comment_list.append(top_level_comment.body)

        return comment_list

    def get_all_comments_by_submission_url(self, url):
        """
        gets all comments by submission URL
        """
        reddit = self.r_authenticator.authenticate_reddit_app()
        submission = reddit.submission(url=url)

        comment_list = []

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            comment_list.append(comment.body)

        return comment_list

    def get_hottest_submission_url_by_subreddit(self, subreddit_name, key_phrase_list=''):
        """
        gets thread by subreddit name and optionally if it matches a keyword
        """
        try:
            reddit = self.r_authenticator.authenticate_reddit_app()
            sub_url = ''
            for submission in reddit.subreddit(subreddit_name).hot(limit=1):
                if any(x in submission.title for x in key_phrase_list):
                    sub_url = submission.url
                    break
        except BaseException as e:
            print("Error no submission found: %s" % str(e))

        return sub_url


class WsbAnalyzer():
    def clean_comment(self, comment):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", comment).split())

    def analyze_sentiment(self, comment):
        analysis = TextBlob(self.clean_comment(comment))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

if __name__ == '__main__':
    client = RedditClient()
    wsb_analyzer = WsbAnalyzer()

    key_phrase_list = ['What Are Your Moves', 'Daily Discussion Thread']
    subreddit_name = 'wallstreetbets'

    sub_url = client.get_hottest_submission_url_by_subreddit(
        subreddit_name, key_phrase_list)

    print("subURL from func: " + sub_url)
    comment_list = client.get_top_comments_by_submission_url(sub_url)

    arr = np.array([wsb_analyzer.analyze_sentiment(comment) for comment in comment_list])

    sentiment = {
        1: 0,
        0: 0,
        -1: 0
    }

    for item in arr:
        sentiment[item]+=1

    print(len(comment_list))
    print(sentiment)
