#!/usr/bin/env python
# OnionFeedReader.py
# Written by Julian Leland
# May 22nd, 2013

# This program uses the Twitter API to read tweets from TheOnion.com's Twitter feed. It then picks the top 10 tweets (as determined by # of RTs), and coallates those tweets with their URLs into an email. Finally, it sends that email to a desired recipient.
 
# This logfile stores the last time that the program was run 
LOGFILE = 'prevTime.txt' # Update this at the end of the program
EMAIL = 'email.txt' # Clear and recreate this every time the program runs

import sys
import os
import time
import twitter # Allows us to access twitter
import smtplib # Allows us to send emails
from email.mime.text import MIMEText
os.chdir('DIRECTORY') # Change this to the directory where you want to store temp files

def main():

	api = twitter.Api(consumer_key='XXX', consumer_secret = 'XXX', access_token_key='XXX', access_token_secret='XXX') # Get this info from Twitter.
         
	tweetList = grabTweets(api)
	createEmail(tweetList)


###
def grabTweets(apiInput):
	# This function grabs all of The Onion's tweets since the previous period (or up to a maximum of 200 tweets). It then culls out the top 10 most retweeted tweets, and outputs them in a sub-list.
	# If we can get to the logfile, open it and read out the lastid (the last time we ran our script)
	if os.path.exists(LOGFILE):
		fp = open(LOGFILE)
		lastid = fp.read().strip()
		fp.close()
	
	if lastid == '':
		lastid = 0

	tweetObject = []
	tweetText = []
	tweetRTs = []
	tweetIDs = []
	tweetData = [tweetObject,tweetText,tweetRTs,tweetIDs]
	# Grab all tweets from the Onion's timeline, since time lastid, excluding retweets and replies (because those are boring).
	recentTweets = apiInput.GetUserTimeline(screen_name='TheOnion', since_id = lastid, include_rts = False, exclude_replies = True)
	numStatus = len(recentTweets)
	if numStatus == 0:
		print 'No new tweets'
		sys.exit()
	else:
		for i in range(numStatus):
			tweetData.insert(i,[recentTweets[i], recentTweets[i].text, recentTweets[i].retweet_count, recentTweets[i].id])
	
	# Sort the data in tweetData by tweetRTs.
	for bottom in range(numStatus - 1):
		minPosition = bottom
		for i in range(bottom + 1, numStatus):
			if tweetData[i][2] > tweetData[minPosition][2]:
				minPosition = i
			tweetData[bottom], tweetData[minPosition] = tweetData[minPosition], tweetData[bottom]
	
	fp = open(LOGFILE, 'w')
	for j in range(numStatus):
		if tweetData[j][3] > lastid:
			lastid = tweetData[j][3]
	fp.write(str(lastid))
	fp.close()
	
	tweetData = tweetData[0:10]
	
	return tweetData
###

###
def createEmail(tweetList):
# This function takes the top 10 tweets culled by GrabTweets, and formats them into a pretty email.
	if os.path.exists(EMAIL):
		fp = open(EMAIL, 'w')
		for j in range(len(tweetList)):
			fp.write('#%s: '%str(j+1))
			fp.write(str(tweetList[j][1].encode('utf-8')))
			fp.write('\n')
			fp.write('\n')
		fp.close()
	else:
		print 'Can\'t find email file'
		sys.exit
	
	# Open a plain text file for reading.  For this example, assume that
	# the text file contains only ASCII characters.
	
	fp = open(EMAIL, 'rb')
	# Create a text/plain message
	msg = MIMEText(fp.read())
	fp.close()

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'Top Tweets from America\'s most trusted news source - The Onion'
	msg['From'] = 'me'
#	msg['To'] = 'you'

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	# Swap out 'EMAILX' for your own addresses.
	
	server = smtplib.SMTP( "smtp.gmail.com", 587 ) # Currently set up for GMail, change as needed.
	server.starttls()
	server.login('XXX', 'XXX' )
	server.sendmail('EMAIL1', 'EMAIL2', msg.as_string())
	server.quit()

###

if __name__ == "__main__":
	main()