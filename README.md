# State COVID-19 Twitter Bot

 This is a Twitter bot that tweets daily, state-level COVID-19 data using The COVID Tracking Project's data API.

 ## Dependencies

 The Twitter bot has several dependencies.

 ### The COVID Tracking Project's Data API

 Daily, state-level COVID-19 data is retrieved from The COVID Tracking Project's data API, which is described in detail at https://covidtracking.com/data/api.  It is available under a [CC BY-NC-4.0 license](https://covidtracking.com/about-data/license).

 ### Twitter Developer API

 In order to tweet COVID-19 data daily, the bot must have access to access token and consumer key information from a valid [Twitter Developer API](https://developer.twitter.com/en) account.

 ### Tweepy

 The bot utilizes the [Tweepy](http://docs.tweepy.org/en/latest/) module in order to actually post tweets via the Twitter Developer API.

 ## Environment Variables

 The Twitter bot depends on several environment variables in order to function properly.  Those environment variables are defined below:

 | Environment Variable        | Description                                                                                                                                          | Example          |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| STATE_ABBREVIATION          | 2-character state abbreviation in lowercase.                                                                                                         | wa               |
| STATE_NAME                  | Name of the state that you want to appear in tweets.                                                                                                 | Washington State |
| SEND_TWEET                  | Flag to control whether a tweet is published or not (to help with debugging).  Any value other than "True" will keep the tweet from being published. | True             |
| TWITTER_ACCESS_TOKEN        | Access token associated with a Twitter Developer API account.                                                                                        | N/A              |
| TWITTER_ACCESS_TOKEN_SECRET | Access token secret associated with a Twitter Developer API account.                                                                                 | N/A              |
| TWITTER_CONSUMER_KEY        | Consumer key associated with a Twitter Developer API account.                                                                                        | N/A              |
| TWITTER_CONSUMER_SECRET     | Consumer key associated with a Twitter Developer API account.                                                                                        | N/A              |

## Twitter Bot in the Wild

This Twitter bot has been implemented as an [AWS Lambda](https://aws.amazon.com/lambda/) function in order to automatically tweet daily, state-level COVID-19 data for Washington State at the [@covid_wa](https://twitter.com/covid_wa) Twitter account.

The following is [an example tweet](https://twitter.com/covid_wa/status/1301311964057083905) from the account:

> Washington State COVID-19 numbers for Monday, August 31, 2020: 304 new positive case(s) out of 6794 test(s) (4.5%); 24 new hospitalization(s); 16 new death(s). #coronavirus #covid19
