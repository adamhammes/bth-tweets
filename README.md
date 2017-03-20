# Beyond the Hashtags: Rehydration

The public report
[Beyond the Hashtags: #Ferguson, #Blacklivesmatter, and the Online Struggle for Offline Justice](http://cmsimpact.org/resource/beyond-hashtags-ferguson-blacklivesmatter-online-struggle-offline-justice/)
used a dataset of tweets purchased from Twitter.
The authors have made the data public - with a slight catch.
[From the original announcement](http://dfreelon.org/2017/01/03/beyond-the-hashtags-twitter-data/):

> Unfortunately, Twitter’s Terms of Service restricts users from publishing any Twitter data except tweet IDs.
However, these IDs can be programmatically “hydrated,” which recreates the original dataset minus any tweets that have been deleted or removed from public view since the dataset was generated.

The announcement also included sample code.
The sample code by itself is insufficient to download the *entirety* of the data.
This repo expands the sample code to facilitate downloading the entire data set.

## Prerequisites

You will need to have Git and Python 3 installed and available via the command-line.
You can test that Git is installed by running:

```
$ git --version
```

To check Python, run

```
$ python --version
```

or

```
$ python3 --version
```

The version printed should start with a 3 (e.g., `3.4.3`).
The first command (without the `3`) may print out a python 2 version (like `2.7.10`).
If so, try the second.
If the latter command worked, then you will need to replace `python` and `pip` in the usage instructions with `python3` and `pip3`.

If either command fails, or says `No command found`, you will need to install the appropriate package.

You will also need to [create a Twitter API account](https://apps.twitter.com).
Once that is created, create a new app.
The account information/tokens you need are under the "Keys and Access Tokens" tab of the app page.

## Usage

If at any point in this process you get lost or are struggling, please [file an issue](https://github.com/adamhammes/bth-tweets/issues/new).

Download the repo and change directory to it by running

```
$ git clone https://github.com/adamhammes/bth-tweets
$ cd bth-tweets
```

Download the [zip of tweet ids](http://dfreelon.org/data/bth_ids.zip) from Deen Freelon's website (it's around 250 megabytes).
Unzip it and copy all the files inside to `id_files/`.
If you are working from the command-line, something like this should work:

```
$ curl -o ids.zip -A  "Mozilla/5.0" http://dfreelon.org/data/bth_ids.zip
$ unzip ids.zip -d id_files/
```


If you haven't yet, create your Twitter API account and app.
Paste your app secrets into the relevant fields in `secrets.toml`.

Then, install the program's dependencies with

```
$ pip install -r requirements.txt
```

Finally, run the program with

```
$ python rehydrate.py
```

Re-running the program will resume hydration from where it was previously stopped.

If the program crashes at any point, please [file an issue](https://github.com/adamhammes/bth-tweets/issues/new) with the stacktrace and I'll look into it.

