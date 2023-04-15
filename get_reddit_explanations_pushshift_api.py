#This code works!

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
from collections import defaultdict
import urllib
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

#pd.set_option('max_columns', None)
# Function to get all comments for a specific submission and find the keyword "removed" in the comment body.
# If one comment is found with the keyword, then return the comment. 
def mySubmissionHasExplanation(submission_id):
    #Convert submision id from base 36 to base 10 and build the url.
    submission_id_converted = int(submission_id,36)
    # First collect all root comments for the submission - endpoint not working
    url= "https://api.pushshift.io/reddit/comment/search/?q='was removed'|'has been removed'&link_id="+str(submission_id_converted)
    print(f"Url for the comments for each submission: {url}")
    try:
        print("In try")
        comments = requests.get(url)
        print("after requests.get")
        print(f"comments: {comments}")
        # dataframe of all comment_ids
        comments_df = pd.json_normalize(comments.json()['data'])
        length_comments_df = len(comments_df)
        print(f"The lenght of the comment_df: {length_comments_df}")
                
        for i in range (length_comments_df):
            comment_body = comments_df.loc[i, "body"]
            print(f"Comment body: {comment_body}")
            comment_author = comments_df.loc[i, "author"]
            comment_created_utc = comments_df.loc[i, "created_utc"]
            if ("removed" in comment_body): #or ("was removed" in body) or ("has been removed" in body):
                return comment_body, comment_author, comment_created_utc 
             
    except:
        print("The endpoint could not be reached.") 
    return "None", "None", "None"  
         
# Get current working directory    
cwd_path = pathlib.Path.cwd()

# Create a new folder to write any files related to reddit_explanations_covid_pushshift
reddit_explanations_pushshift = cwd_path/"reddit_explanations_covid_pushshift"
reddit_explanations_pushshift.mkdir(exist_ok=True)

submissions_file = reddit_explanations_pushshift/"submissions_file.csv"
# Create a file called removed_submissions.csv to write all removed submissions from July 1st to August 31st.
removed_submissions_file = reddit_explanations_pushshift/"removed_submissions.csv"
# removed_submissions_comments_file = reddit_explanations_pushshift/"removed_submissions_comments.csv"

submissions_file.touch()
removed_submissions_file.touch()
# removed_submissions_comments_file.touch()

# List for all submissions id
submissions_id_list = []
comments_list = []
#keys_for_comments_dict = ["submission_id", "comment_body", "comment_author", "comment_created_utc"]
comments_dict = defaultdict(list)
# Get 500 submissions per day with the keywords covid or vaccine between the dates July 1st and August 31st
# Get a list of all the dates between July 1st and August 31st
num_days = 1
# Create base date
base = datetime(2022, 12, 29)
date_list = []
submissions_df = pd.DataFrame()
# Create a list of dates starting on July 1st
for x in range(num_days):
    date_list.append(base + timedelta(days=x))
        
# Loop through date_list and get begin and end datetimes for each day in utc. Create url to call pushshift api and 
# get 500 removed submissions by moderator for each day and add to submissions dataframe.    
for dt in date_list:
    begintime_date = datetime.combine(dt, time.min)
    begintime_date = datetime.combine(dt, time.min)# time.min will give me 12:00 am
    print("begintime_date",begintime_date)
    endtime_date = datetime.combine(dt, time.max) # time.max will give me 11:59 pm
    begintime_date_utc = begintime_date.timestamp()
    print("begintime_date_utc",begintime_date_utc)
    endtime_date_utc = endtime_date.timestamp()
    url = "https://api.pushshift.io/reddit/search/submission/?" #This is the pushshift endpoint for getting the submissions.
    params = {"since": int(begintime_date_utc), "until": int(endtime_date_utc), "size": "200", "removed_by_category": "moderator"}
    url = url + urllib.parse.urlencode(params) # Forming the url
    print(url)
    try:
        data= requests.get(url)
        # Add the submissions received from Reddit to a temporary dataframe and add to submissions dataframe.
        # Keep adding to submissions_df each time you loop.
        temp_submissions_df = pd.json_normalize(data.json()['data'])
        #submissions_df = submissions_df.append(temp_submissions_df, ignore_index=True)
        submissions_df = pd.concat([submissions_df,temp_submissions_df])        
    except:
        print("The endpoint could not be reached.")
        
    t.sleep(10)
# Write all the submissions with at least 1 comment containing the keyword "removed" to a file
if not submissions_df.empty:
    submissions_df_with_comments = submissions_df[(submissions_df["num_comments"] > 0)]
    data_top = submissions_df_with_comments.head() 
    #print("data_top",data_top)
    list(submissions_df_with_comments.columns)
    #for col_name in submissions_df_with_comments.columns:
        #print(f"Column name: {col_name}")
    submissions_df_with_comments.to_csv(submissions_file)
    for i in range(len(submissions_df_with_comments)):
        try:
            submission_id = submissions_df_with_comments.iloc[i, 28]
            print(f"The submission_id is: {submission_id}")
            # For each submission, check if at least 1 comment contains the word "removed". If True, then add the 
            # submission_id to the submissions_id_list.
            comment_body, comment_author, comment_created_utc = mySubmissionHasExplanation(submission_id)
            print(f"Comment author: {comment_author}")
            print(f"Comment body: {comment_body}")    
            if comment_body == "None":
                print("This submission has no comments with the word 'removed'.")
            else:
                # Add submission with comment with the word "removed" to the submissions_id_list
                submissions_id_list.append(submission_id)
                #comments_list.extend([submission_id, comment_body, comment_author, comment_created_utc])
                
                comments_dict["submission_id"].append(submission_id)
                comments_dict["comment_body"].append(comment_body)
                comments_dict["comment_author"].append(comment_author)
                comments_dict["comment_created_utc"].append(comment_created_utc)
        except:
            print("Could not get submission_id.")
        t.sleep(7)
    if comments_dict:
        comments_dict_df = pd.DataFrame(comments_dict)
        print(comments_dict_df.shape)
        # Merge submissions_df_with_comments and comments_list_df with id as left key and submission_id as the right key
                                
        submissions_df_to_write = submissions_df_with_comments[submissions_df_with_comments["id"].isin(submissions_id_list)]
        print(submissions_df_to_write.shape)

        submissions_df_to_write_merged = pd.merge(submissions_df_to_write, comments_dict_df, left_on='id', right_on='submission_id')

        header = ["id", "url", "selftext", "author_fullname", "created_utc", "score", "subreddit", "permalink", 'comment_body', 'comment_author', 'comment_created_utc']
        submissions_df_to_write_merged.to_csv(removed_submissions_file, index=False, columns=header)




    # Sources:

    # https://levelup.gitconnected.com/easily-obtain-reddit-data-with-python-8ce0c576540f

    # https://reddit-api.readthedocs.io/en/latest/#searching-submissions

    # https://github.com/pushshift/api