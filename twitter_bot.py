"""
twitter_bot.py

Developer:  Bernie Zimmermann

This module enables retrieving daily COVID-19 data for a specific state
from The COVID Tracking Project's data API and automatically sharing a
summary of that information via a Twitter account.

Dependencies:

tweepy
http://docs.tweepy.org/en/latest/index.html
"""

from datetime import datetime, timedelta
import json
import logging
import os
import sys
import traceback
from urllib import request

import tweepy

# general defines
FRIENDLY_DATE_FORMAT = "%A, %B %d, %Y"

# state defines
STATE_ABBREVIATION = os.getenv("STATE_ABBREVIATION")
STATE_NAME = os.getenv("STATE_NAME")

# Twitter defines
SEND_TWEET = os.getenv("SEND_TWEET")
TWEET_TEMPLATE_FULL = (
    "%s COVID-19 numbers for %s: %d new positive case(s) out "
    "of %d test(s) (%.1f%%); %d new hospitalization(s); %d new death(s). "
    "#coronavirus #covid19"
)
TWEET_TEMPLATE_PARTIAL = (
    "%s COVID-19 numbers for %s: %d new positive case(s); %d "
    "new hospitalization(s); %d new death(s). #coronavirus #covid19"
)
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")

# COVID Tracking Project defines
CTP_DATE_FORMAT = "%m/%d/%Y %H:%M"
CTP_DEATH_INCREASE = "deathIncrease"
CTP_HOSPITALIZED_INCREASE = "hospitalizedIncrease"
CTP_LAST_UPDATE_ET = "lastUpdateEt"
CTP_POSITIVE_INCREASE = "positiveIncrease"
CTP_STATE_DATA_API_TEMPLATE = "https://covidtracking.com/api/v1/states/%s/current.json"
CTP_TEST_INCREASE = "totalTestResultsIncrease"

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

    # build the URL of the corresponding API request
    api_url = CTP_STATE_DATA_API_TEMPLATE % (STATE_ABBREVIATION)

    # log a message
    logger.debug("Making a request to %s", api_url)

    # make a request to the API
    with request.urlopen(api_url) as url:

        # get the response from the API as JSON
        response = json.loads(url.read().decode("utf-8"))

        # log a message
        logger.debug("The API response is %s", response)

        # retrieve the pertinent data
        deaths = response[CTP_DEATH_INCREASE]
        hospitalizations = response[CTP_HOSPITALIZED_INCREASE]
        last_updated = response[CTP_LAST_UPDATE_ET]
        positive_tests = response[CTP_POSITIVE_INCREASE]
        tests = response[CTP_TEST_INCREASE]

        # convert the last updated string to a datetime
        updated = datetime.strptime(last_updated, CTP_DATE_FORMAT)

        # subtract a day to get the as of date
        as_of = updated - timedelta(days=1)

        # convert the date to a friendly string
        friendly_date = as_of.strftime(FRIENDLY_DATE_FORMAT)

        # handle the case where deaths get adjusted and reflect a negative amount
        deaths = int(deaths)
        deaths = 0 if deaths < 0 else deaths

        # prepare for a status update
        status_update = None

        # if a larger number of tests was returned than positive tests
        if int(positive_tests) < int(tests):

            # generate the full status update using the full template
            status_update = TWEET_TEMPLATE_FULL % (
                STATE_NAME,
                friendly_date,
                int(positive_tests),
                int(tests),
                int(positive_tests) / int(tests) * 100 if tests != 0 else 0.0,
                int(hospitalizations),
                deaths,
            )

        # else if only positive tests were reported
        else:

            # generate the full status update using the full template
            status_update = TWEET_TEMPLATE_PARTIAL % (
                STATE_NAME,
                friendly_date,
                int(positive_tests),
                int(hospitalizations),
                deaths,
            )

    # log a message
    logger.info(status_update)

    # if the tweet should be sent (i.e. not debugging)
    if SEND_TWEET == "True":

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
