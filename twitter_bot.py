"""
twitter_bot.py

Developer:  Bernie Zimmermann

This module enables retrieving daily COVID-19 numbers for a specific state
from The New York Times' COVID-19 data and automatically sharing a
summary of that information via a Twitter account.

Dependencies:

tweepy
http://docs.tweepy.org/en/latest/index.html
"""

from datetime import datetime
import logging
import os
import re
import sys
import traceback
from urllib import request

import tweepy

# general defines
FRIENDLY_DATE_FORMAT = "%A, %B %d, %Y"
SOURCE_DATE_FORMAT = "%Y-%m-%d"

# state defines
STATE_NAME = os.getenv("STATE_NAME")
FRIENDLY_STATE_NAME = os.getenv("FRIENDLY_STATE_NAME", STATE_NAME)

# Twitter defines
SEND_TWEET = os.getenv("SEND_TWEET")
TWEET_TEMPLATE_FULL = (
    "%s COVID-19 numbers for %s: %d new positive case(s) and %d new death(s). "
    "#coronavirus #covid19"
)
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")

# NYT COVID-19 data defines
NYT_STATE_DATA_URL = (
    "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
)
NYT_STATE_RECORD_PATTERN = fr"^.*,{STATE_NAME},.*$"
NYT_DATE_POSITION = 0
NYT_CASES_POSITION = 3
NYT_DEATHS_POSITION = 4

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    """The main function that does all the heavy lifting."""

    # log a message
    logger.info("Starting processing.")

    # prepare for an eventual status update
    status_update = None

    # log a message
    logger.debug("Making a request to %s", NYT_STATE_DATA_URL)

    # make a request to the API
    with request.urlopen(NYT_STATE_DATA_URL) as url:

        # get the response
        response = url.read().decode("utf-8")

        # find all matching state records in the response
        state_records = re.findall(NYT_STATE_RECORD_PATTERN, response, re.MULTILINE)

        # log a message
        logger.info("%d state record(s) found.", len(state_records))

        # if at least two state records were found in the response
        if len(state_records) >= 2:

            # split the most recent records into their individual data points
            latest_data = state_records[-1].split(",")
            prior_data = state_records[-2].split(",")

            # log a message
            logger.info(
                "The most recent state record is from %s and the second "
                "to last state record is %s.",
                latest_data[NYT_DATE_POSITION],
                prior_data[NYT_DATE_POSITION],
            )

            # convert the data source date to a datetime
            data_source_date = datetime.strptime(
                latest_data[NYT_DATE_POSITION], SOURCE_DATE_FORMAT
            )

            # convert the date to a friendly string
            friendly_date = data_source_date.strftime(FRIENDLY_DATE_FORMAT)

            # do the math to get the case and death counts
            cases = int(latest_data[NYT_CASES_POSITION]) - int(
                prior_data[NYT_CASES_POSITION]
            )
            deaths = int(latest_data[NYT_DEATHS_POSITION]) - int(
                prior_data[NYT_DEATHS_POSITION]
            )

            # generate the full status update using the full template
            status_update = TWEET_TEMPLATE_FULL % (
                FRIENDLY_STATE_NAME,
                friendly_date,
                cases,
                deaths,
            )

        # else if there is no meaninful data available
        else:

            # log a message
            logger.info(
                "The data source did not return meaningful data for the day, "
                "so no tweet will be sent."
            )

    # log a message
    logger.info("Status update: %s", status_update)

    # if a status update is ready and the tweet should be sent (i.e. not debugging)
    if status_update and SEND_TWEET == "True":

        # log a message
        logger.info("Connecting to the Twitter API.")

        # connect to the Twitter API
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        twitter_api = tweepy.API(auth)

        # post the status update to Twitter
        twitter_api.update_status(status_update)


def entry_point(event, context):
    """The entry-point that can be run as a Lambda function."""

    try:

        # run the main function
        main()

    # on any exception
    except Exception:

        # log the exception
        logger.critical("An exception occurred: %s.", traceback.format_exc())


# if running this module directly
if __name__ == "__main__":

    # execute the entry point with empty input
    entry_point([], [])
