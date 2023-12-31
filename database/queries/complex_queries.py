import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)

from database.db_manager import DBManager
from database.CRUD.read import *
from database.model import Trend, Tweet, User
import pandas as pd
import time
import json

def operation1():
    """
    1. AVERAGE SENTIMENT PER TREND
    For each trend, select all the tweets associated with the trend and show the
    sentiment obtained as the average of the sentiment of the selected tweets.
    """
    result = []
    # get all the trends
    trends = Trend.nodes.all()
    for trend in trends:
        # get all the tweets associated with the trend
        tweets = trend.tweets.all()
        # compute the average sentiment
        sum = 0
        for tweet in tweets:
            sum += tweet.sentiment
        avg = sum / len(tweets)
        result.append({"name": trend.name, "location": trend.location, "date": trend.date, "sentiment": avg})
    return result

def operation2():
    """
    2. SENTIMENT PERCENTAGES
    For each trend, select all the tweets that belong to it and for each value of sentiment that the tweet can assume,
    print the percentage of them that obtained that particular sentiment.
    """
    result = []
    # get all the trends
    trends = Trend.nodes.all()
    for trend in trends:
        # get all the tweets associated with the trend
        tweets = trend.tweets.all()
        # compute the percentages
        positive = 0
        negative = 0
        neutral = 0
        for tweet in tweets:
            if tweet.sentiment > 0.2:
                positive += 1
            elif tweet.sentiment < -0.2:
                negative += 1
            else:
                neutral += 1
        positive = int (positive / len(tweets) * 100)
        negative = int (negative / len(tweets) * 100)
        neutral = int (neutral / len(tweets) * 100)
        result.append({"name": trend.name, "location": trend.location, "date": trend.date, "positive": positive, "negative": negative, "neutral": neutral})
    return result

def operation3(trend):
    """
    3. TREND DIFFUSION DEGREE
    Given a certain trend, identify all the users who have published tweets that belong to it and based on their number of 
    followers identify how many people have been reached by the trend, as the sum of the number of followers (which is 
    clearly an approximation)
    """
    result = []
    # get all the tweets associated with the trend which have not the relationship "COMMENTED_ON"
    tweets = trend.tweets.all()
    
    all_tweets = []
    
    # also get the comments of the tweets
    for tweet in tweets:
        all_tweets.append(tweet)
        comments = tweet.comments_from.all()
        for comment in comments:
            all_tweets.append(comment)
            
    tweets = all_tweets
    
    # get all the users who wrote the tweets
    users = {}
    followers = 0
    for tweet in tweets:
        for user in tweet.user.all():
            users[user.id_mongo] = user.followers
            
    followers = sum(users.values())
            
    result.append({"name": trend.name, "location": trend.location, "date": trend.date, "followers": followers})
    return result

def operation4():
    """
    4. USER COHERENCE SCORE
    For each user, group the tweets he wrote by the trends in the trends array and, for each cluster, assign the user a coherence score, 
    average the scores obtained 
    """
    
    result = []

    user_score = {}

    # get all the users
    users = User.nodes.all()

    for user in users:

        # get all the tweets written by the user

        if user is None or user.tweets is None or len(user.tweets.all()) == 0:
            continue

        tweets = user.tweets.all()
        
        tweets_by_trend = {}
        
        for tweet in tweets:
            for trend in tweet.trends.all():
                if trend.name not in tweets_by_trend:
                    tweets_by_trend[trend.name] = []
                tweets_by_trend[trend.name].append(tweet)
                
        # compute the coherence score for each cluster
        scores = {}
        for trend in tweets_by_trend:
            tweets = tweets_by_trend[trend]
            # compute the average sentiment
            sum = 0
            for tweet in tweets:
                sum += tweet.sentiment
            avg = sum / len(tweets) if len(tweets) > 0 else 0
            scores[trend] = avg
           
        # compute the average of the scores
        sum = 0
        for score in scores.values():
            sum += score
        avg = sum / len(scores) if len(scores) > 0 else 0
        user_score[user.username] = avg  

    # normalize scores between 0 and 100
    min_score = min(user_score.values())
    max_score = max(user_score.values())
    
    for user in user_score:
        user_score[user] = (user_score[user] - min_score) / (max_score - min_score) * 100
        result.append({"username": user, "score": user_score[user]})
        
    return result

def operation5(user):
    """
    5. USER'S SENTIMENT PERCENTAGES
    Given a user, take the tweets he wrote and calculate the percentages of positive, negative and neutral sentiment tweets.
    """
    result = []
    # get all the tweets written by the user
    tweets = user.tweets.all()
    # compute the percentages
    positive = 0
    negative = 0
    neutral = 0
    for tweet in tweets:
        if tweet.sentiment > 0.2:
            positive += 1
        elif tweet.sentiment < -0.2:
            negative += 1
        else:
            neutral += 1
    positive = positive / len(tweets) * 100
    negative = negative / len(tweets) * 100
    neutral = neutral / len(tweets) * 100
    result.append({"username": user.username, "positive": positive, "negative": negative, "neutral": neutral})
    return result

def operation6():
    """
    6. ENGAGEMENT METRICS COMPUTATION
    For each trend, compute the average number of likes, shares and retweets that its posts have received
    """
    result = []
    # get all the trends
    trends = Trend.nodes.all()
    for trend in trends:
        # get all the tweets associated with the trend
        tweets = trend.tweets.all()
        # compute the average number of likes, shares and retweets
        sum_likes = 0
        sum_shares = 0
        sum_retweets = 0
        for tweet in tweets:
            sum_likes += tweet.likes
            sum_shares += tweet.shares
            sum_retweets += tweet.retweets
        avg_likes = sum_likes / len(tweets)
        avg_shares = sum_shares / len(tweets)
        avg_retweets = sum_retweets / len(tweets)
     
        result.append({"name": trend.name, "location": trend.location, "date": trend.date, "likes": avg_likes, "shares": avg_shares, "retweets": avg_retweets})
        
    return result
     
def operation7(trend):
    """
    7. DISCUSSIONS' DETECTION   
    Given a trend, for each tweet associated with it, check if its comments have given rise to a discussion by 
    identifying any discordant sentiments
    """
    result = []
    tweets = trend.tweets.all()
    for tweet in tweets:
        if tweet.sentiment > 0.2:
            sentiment = "positive"
        elif tweet.sentiment < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        # get all the comments of the tweet
        found = False
        for comment in tweet.comments_from.all():
            if comment.sentiment > 0.2:
                comment_sentiment = "positive"
            elif comment.sentiment < -0.2:
                comment_sentiment = "negative"
            else:
                comment_sentiment = "neutral"
            if comment_sentiment != sentiment:
                result.append({"tweet": tweet.text, "discussion": True})
                found = True
                break
        if not found:
            result.append({"tweet": tweet.text, "discussion": False})
    return result
            
PERFORMANCES = False
NUM_TESTS = 10

if __name__ == '__main__':
    # take port, name of the db, username and password from the command line
    if len(sys.argv) != 5:
        print("Usage: python create.py <port> <db_name> <username> <password>")
        sys.exit(1)
    
    db_manager = DBManager(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    
    user = get_user_by_username("@Ex_puppypaws")
    trend = get_trend_by_name_location_date("#Halloween", "Italy", "2023-11-01T16:29:31.292726")
    
    operations = [
        {
            "name": "AVERAGE SENTIMENT PER TREND",
            "function": operation1, 
            "requires": []
        },
        {
            "name": "SENTIMENT PERCENTAGES",
            "function": operation2,
            "requires": []
        },
        {
            "name": "TREND DIFFUSION DEGREE",
            "function": operation3,
            "requires": [trend]
        },
        {
            "name": "USER COHERENCE SCORE",
            "function": operation4,
            "requires": []
        },
        {
            "name": "USER'S SENTIMENT PERCENTAGES",
            "function": operation5,
            "requires": [user]
        },
        {
            "name": "ENGAGEMENT METRICS COMPUTATION",
            "function": operation6,
            "requires": []
        },
        {
            "name": "DISCUSSIONS' DETECTION",
            "function": operation7,
            "requires": [trend]
        }
    ]
    
    if not PERFORMANCES:

        for operation in operations:
            print(operation["name"])
            if len(operation["requires"]) == 0:
                print(json.dumps(operation["function"](), indent=4))
            else:
                print(json.dumps(operation["function"](*operation["requires"]), indent=4))
    
    else:
        
        perf = pd.DataFrame(columns=['operation', 'executionTime'])
        
        for n in range(NUM_TESTS):
            
            print("Test " + str(n + 1))
            
            for operation in operations:
                    
                print(operation["name"])
                
                start = time.time()
                
                if len(operation["requires"]) == 0:
                    operation["function"]()
                else:
                    operation["function"](*operation["requires"])
                    
                end = time.time()
                
                perf = perf._append({
                    'operation': operation["name"],
                    'executionTime': end - start
                }, ignore_index=True)
            
        # compute the mean of the execution times for each operation
        operations = perf['operation'].unique()
        mean_df = pd.DataFrame(columns=['operation', 'executionTime'])
        for operation in operations:
            mean = perf[perf['operation'] == operation]['executionTime'].mean()
            # replace the rows with the mean
            mean_df = mean_df._append({
                'operation': operation,
                'executionTime': mean
            }, ignore_index=True)
        mean_df.to_csv('performances/complex_queries_performances_GDB.csv', index=False)