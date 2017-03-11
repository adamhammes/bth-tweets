import csv
import os

import toml
from twarc import Twarc

in_dir = 'id_files'
out_dir = 'hydrated_files'
secrets_path = 'secrets.toml'

twarc = None


def read_secrets():
    with open(secrets_path, 'r') as file:
        return toml.loads(file.read())


def main():
    """
    Go through every file in the in_dir and try to rehydrate them. This will take a while, and should be only done with
    a stable Internet connection.

    :return: None
    """
    file_names = []

    for filename in os.listdir(in_dir):
        if filename.endswith('.txt'):
            file_names.append(filename)

    for file_name in file_names:
        hydrate_file(file_name)


def hydrate_file(file):
    """
    Given the name of the file containing tweet ids, attempt to download the tweets and their associated metadata, then
    store the results in a json file.

    The infile (the file containing the tweet ids) will be looked for in the `in_dir`. The corresponding outfile (which
    will contain the actual tweets and metadata) will have the same name and be stored in the `out_dir`.

    Note that the outfile will have the same name and extension as the infile, even though it contains JSON data. This
    is for the sole reason that I am lazy.

    :param file: The name of the file to be hydrated, excluding any directories.
    :return: None
    """

    # Because we may be running this program over the course of several days, it's important to not waste time
    # rehydrating the same file over and over. To this end, I attempt to check if a file has already been hydrated by
    #   (1) See if the corresponding hydrated file exists
    #   (2) See if the hydrated file is non-empty
    #
    # Step (2) is necessary because the file may have been created but not yet written to.
    out_file_name = os.path.join(out_dir, file)
    if os.path.isfile(out_file_name) and os.path.getsize(out_file_name) > 0:
        print('{} appears to have already been hydrated - skipping over.'.format(file))
        print('If you would still like to hydrate this file, call')
        print('hydrate_file({})'.format(file))
        print('directly.\n')
        return

    print('Hydrating {}'.format(file))
    rows = []

    with open(os.path.join(in_dir, file), 'r') as in_file:
        ids = in_file.read().splitlines()

    for tweet in twarc.hydrate(ids):
        rows.append([
            tweet['retweet_count'],
            tweet['favorite_count'],
            tweet['text'],
            tweet['id'],
            tweet['created_at'],
            tweet['lang'],
            tweet['is_quote_status'],
            tweet['user']['id'],
            tweet['user']['name'],
            tweet['user']['screen_name']
        ])

    column_names = ['retweet_count', 'favorite_count', 'text', 'id', 'created_at', 'lang', 'is_quote_status', 'user_id',
                    'user_name', 'user_screen_name']

    with open(out_file_name, 'w', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(column_names)
        writer.writerows(rows)


if __name__ == '__main__':
    if not os.path.isdir(in_dir):
        print('Error! Could not find the directory of the dehydrated tweets.')
        print('Make sure that the folder is named {} and is in the same folder as your code.'.format(in_dir))
        exit()

    secrets = read_secrets()

    consumer_key = secrets['consumer_key']
    consumer_secret = secrets['consumer_secret']
    access_token = secrets['access_token']
    access_token_secret = secrets['access_token_secret']

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print('Please make sure that you have filled in the API information in secrets.toml')
        print('Visit https://apps.twitter.com/ if you haven\'t generated these yet.')
        exit()

    twarc = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    main()
