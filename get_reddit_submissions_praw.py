import praw
import csv
import pathlib
import pandas as pd
import time
import pprint

cwd_path = pathlib.Path.cwd()
# Create a new folder to write any files related to Reddit explanations.
reddit_explanations = cwd_path/"reddit_explanations"
reddit_explanations.mkdir(exist_ok=True)

# Intialize a Reddit instance with connection information.
reddit = praw.Reddit(client_id='eYrlPlQuuPYIB2yWhBuTGQ', client_secret='UuIq-4gB8H3PqgEwPbjHvpLLvYz7pQ', user_agent='Removal Explanations')

# Create a file called comments_file.csv to write the comments on all subreddits over 1 week.
submissions_with_comments_file = reddit_explanations/"submissions_with_comments.csv"
submissions_with_comments_file.touch()

comments = pd.read_csv(reddit_explanations/"comments.csv")
#print(comments.head())


# assume you have a praw.Reddit instance bound to variable `reddit`
#submission = reddit.submission("39zje0")
#print(submission.title)  # to make it non-lazy
#pprint.pprint(vars(submission))


sub_author_list = []
sub_title_list = []
sub_reddit_url_list = []
sub_score_list = []
sub_created_utc_list = []
sub_selftext_list = []
for i in range(len(comments)):
    link_id = comments.loc[i, "link_id"]
    #print(f"The link_id is: {link_id}")
    id = link_id[3:]
    #print(f"The id is: {id}")
    try:
        submission =reddit.submission(id)
        print(f"The result of submission title: {submission.title}")
        #print(f"The result of submission author_fullname: {submission.author_fullname}")
        #print(f"The result of submission created_utc: {submission.created_utc}")
        #print(f"The result of submission id: {submission.url}")
        sub_author_list.append(submission.author_fullname)
        sub_title_list.append(submission.title)
        sub_reddit_url_list.append(submission.url)
        sub_score_list.append(submission.score)
        sub_created_utc_list.append(submission.created_utc)
        sub_selftext_list.append(submission.selftext)
    except:
        sub_author_list.append("Not found")
        sub_title_list.append("Not found")
        sub_reddit_url_list.append("Not found")
        sub_score_list.append("Not found")
        sub_created_utc_list.append("Not found")
        sub_selftext_list.append("Not found")
        print("Could not get submission from Reddit")
    time.sleep(5)
    
comments['submission_author'] = sub_author_list
comments['submission_title'] = sub_title_list
comments['submission_reddit_url'] = sub_reddit_url_list
comments['submission_score'] = sub_score_list
comments['submission_created_utc'] = sub_created_utc_list
comments['submission_selftext'] = sub_selftext_list

header = ["id", "author_fullname", "distinguished", "score", "link_id", "subreddit", "permalink", 'body', 'author', 'created_utc', 'submission_author', 'submission_title', 'submission_reddit_url','submission_score','submission_created_utc','submission_selftext']
# Check the initial shape of the DataFrame
print(f"Old Shape: {comments.shape}")
# Delete rows where case numbers are zero
# This deletion is completed by "selecting" rows where case numbers are non zero
comments = comments.loc[comments["submission_title"] != "Not found"]
print(f"Shape: {comments.shape}")
comments.to_csv(submissions_with_comments_file, columns=header)

    



