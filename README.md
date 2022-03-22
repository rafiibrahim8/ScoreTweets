[![License][License-shield]][License-url]

# ScoreTweets

#### Automatically post PCSPro score tweets to facebook and discord.

# DESCRIPTION
[PCSPro](https://play-cricket.com/features-playcricketscorerpro) is a cricket scoring software. That can score and analyze cricket scores and post them on Twitter. This program grabs the tweets from Twitter and posts them on Discord and Facebook to engage more users.

# INSTALLATION

From a command line enter the command to install ScoreTweets
```
pip install git+https://github.com/rafiibrahim8/ScoreTweets.git --upgrade
```
You need to have python 3.7 or up to run ScoreTweets.

# USES
You need a [Twitter Developer account](https://developer.twitter.com/en/apply-for-access) to run ScoreTweets. After getting developer credentials, create a file in `~/.config/score_tweets/` called `env.json`. In `env.json` you need to have these values:

`twitter_id`: Numerical id of the PCSPro authenticated Twitter account. (Convert username to numerical id [here](https://tweeterid.com/).)

`bearer_token`: Developer account Bearer Token

`facebook_group_id`: Facebook group id in which scores will be posted.

`discord_hook`: Discord webhook in which scores will be posted.

`debug_discord`: (Optional) Another hook in which errors and debug message will be posted.

Here is an example of `env.json` file:

```json
{
    "twitter_id": "2244994945",
    "bearer_token": "AAAAAAAAAAAAAAAAAAAAA",
    "facebook_group_id": "230000000000",
    "discord_hook": "https://discord.com/api/webhooks/90000000/f4AABZ",
    "debug_discord": "https://discord.com/api/webhooks/90000000/ABCD"
}
```


After creating the json file, run the following command to configure ScoreTweets:

```sh
scoretweets -c
```

Finally, run:
```sh
scoretweets
```
to run the program.

# ISSUES

This is very early stage of the program. It might be very buggy. You are always welcome to [create an issue](https://github.com/rafiibrahim8/ScoreTweets/issues) or [submit a pull request](https://github.com/rafiibrahim8/ScoreTweets/pulls).

[License-shield]: https://img.shields.io/github/license/rafiibrahim8/ScoreTweets
[License-url]: https://github.com/rafiibrahim8/ScoreTweets/blob/master/LICENSE

