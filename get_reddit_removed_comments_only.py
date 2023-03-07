from email.mime import base
import requests
import pandas as pd
import json
import pathlib
import csv
import calendar
import datetime
import time as t
from datetime import date, datetime, timedelta
from datetime import datetime, time, timezone
import time
from collections import defaultdict
import urllib

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Get current working directory    
cwd_path = pathlib.Path.cwd()

# Create a new folder to write any files related to reddit_explanations_pushshift
reddit_explanations = cwd_path/"reddit_explanations"
reddit_explanations.mkdir(exist_ok=True)

# Create a file called removed_submissions_comments_file to write all for December 2021.
removed_submissions_comments_file = reddit_explanations/"comments.csv"
removed_submissions_comments_file.touch()

base = date(2021, 12, 1)
print("base date", base)
today = date.today()
print("Today's date:", today)
diff_in_dates = today - base
days = diff_in_dates.days
print(days)
comments_df = pd.DataFrame()

#Loop for each day in Dec 2021 to get the comments with the word removed and and add to comments_df
for i in range(days, days-2, -1):
    after_days=i
    before_days=i-1
    after_days_str = str(after_days)+"d"
    before_days_str = str(before_days)+"d"
    #url = "https://api.pushshift.io/reddit/comment/search/?q=removed&"
    url = "https://api.pushshift.io/reddit/comment/search/?q='was removed'|'has been removed'&"
    params = { "distinguished": "moderator","after": after_days_str, "before": before_days_str, "size": "1000"}
    url = url + urllib.parse.urlencode(params) # Forming the url
    print(url)
    try:
        data= requests.get(url)
        # Add the comments received from Reddit to a temporary dataframe and add to comments_df dataframe.
        temp_comments_df = pd.json_normalize(data.json()['data'])
        # Keep adding to submissions_df each time you loop.
        comments_df = pd.concat([comments_df,temp_comments_df])
        #print(comments_df)
    except:
        print("The endpoint could not be reached.")


for col_name in comments_df.columns:
        print(f"Column name: {col_name}") 

header = ["id", "author_fullname", "distinguished", "score", "link_id", "subreddit", "permalink", 'body', 'author', 'created_utc']
comments_df.to_csv(removed_submissions_comments_file, columns=header)

#The submission details for each comment can be found using the following endpoint.
#https://api.pushshift.io/reddit/search/submission?q=*&id=r7go8l
#We need the submission author, submission title, link or text posted in the submission if any, and the Reddit URL for the submission
#submission author: "author_fullname"
#submission title: "title"
#Reddit URL for the submission: "url"

        
        