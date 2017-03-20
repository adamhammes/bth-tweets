import csv
import os
from io import open

import toml
from twarc import Twarc

in_dir = 'id_files'
out_dir = 'hydrated_files'
secrets_path = 'secrets.toml'

twarc = None


def file_root_name(full_name):
    """
    Returns the name of the file without the extension.
    Example: folder/id5.txt -> id5
    """
    file_name = os.path.basename(full_name)
    return os.path.splitext(file_name)[0]


def generate_out_file_name(file_root):
    """
    File roots are of the form 'bth_ids_%y-%m-%d'. This method simply returns the date portion with '.csv' added at the
    end.
    """
    bth, ids, name = file_root.split('_')
    return os.path.join(out_dir, name + '.csv')


def find_remaining_ids(in_file_name, out_file_name):
    """
    Find all the tweets that have not yet been hydrated.

    If this program is stopped for some reason, it's important to be able to pick up where it was previously. If we did
    not filter out the ids contained in the out_file, we would be duplicating a lot of work and, more importantly,
    wasting a lot of time.

    :param in_file_name: The relative path to the file containing the tweet ids
    :param out_file_name: The relative path to the file containing any rehydrated tweets
    :return: (out_file_exists, remaining_ids), where `out_file_exists` indicates if the out file has been already
    created and remaining_ids is an set of all the unprocessed ids in in_file.
    """
    assert os.path.isfile(in_file_name), '{} does not exist'.format(in_file_name)

    if os.path.isfile(out_file_name.rstrip('.tmp')):
        return True, set()

    with open(in_file_name, 'r') as in_file:
        all_ids = set(in_file.read().splitlines())

    if not os.path.isfile(out_file_name):
        return False, all_ids

    print('Determining which tweets have already been read...')

    with open(out_file_name, 'r', encoding='utf-8') as out_file:
        reader = csv.DictReader(out_file)
        finished_ids = {row['id'] for row in reader}

    return True, sorted(all_ids - finished_ids)


def flush_rows(out_file_name, rows):
    """
    Write all the tweets contained in `rows` to `out_file_name`, then clear `rows`.
    """
    assert os.path.isfile(out_file_name), '{} does not exist'.format(out_file_name)

    with open(out_file_name, 'a', newline='\n', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(rows)

    rows.clear()


def print_hydration_status(iteration, total_tweets):
    percent = float(iteration) / total_tweets * 100
    print('Written {} out of {} tweets ({:.1f}%).'.format(iteration, total_tweets, percent))


def read_secrets():
    with open(secrets_path, 'r') as file:
        return toml.loads(file.read())


def hydrate_file(file_root):
    """
    Given the name of the file containing tweet ids, attempt to download the tweets and their associated metadata, then
    store the results in a csv file. Only some of the fields returned by the Twitter API are written; for a list of
    these, see `column_names`.

    :param file_root: The name of the file to be hydrated, excluding any directories.
    :return: None
    """

    in_file_path = os.path.join(in_dir, file_root + '.txt')

    # The '.tmp' extension is added to indicate that the file is only partially rehydrated. The out file will be renamed
    # once all the tweets have been processed.
    out_file_path = generate_out_file_name(file_root) + '.tmp'

    file_exists, remaining_ids = find_remaining_ids(in_file_path, out_file_path)

    if not remaining_ids:
        # All the tweets in this file have been rehydrated
        return

    if not file_exists:
        print('Hydrating {}'.format(file_root))
        column_names = [u'retweet_count', u'favorite_count', u'text', u'id', u'created_at', u'lang', u'is_quote_status',
                        u'user_id', u'user_name', u'user_screen_name']

        with open(out_file_path, 'w', newline='\n', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(column_names)

    else:
        print('Resuming hydration of {}'.format(file_root))

    # We "batch" the writes of the csv to prevent out of memory errors on the big files. The frequency of these writes
    # is controlled by `rows_before_flushing`, which is set to 100 to match the batching of the twarc library.
    rows = []
    rows_before_flushing = 100
    iteration = 0

    for tweet in twarc.hydrate(remaining_ids):
        iteration += 1
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

        if iteration % rows_before_flushing == 0:
            flush_rows(out_file_path, rows)
            print_hydration_status(iteration, len(remaining_ids))

    flush_rows(out_file_path, rows)

    # Remove the '.tmp' extension to mark that the file has been completely rehydrated
    os.rename(out_file_path, out_file_path.rstrip('.tmp'))


def main(files):
    """
    Go through every file in the in_dir and try to rehydrate them. This will take a while.
    """

    for filename in files:
        hydrate_file(file_root_name(filename))


if __name__ == '__main__':
    if not os.path.isdir(in_dir):
        os.makedirs(in_dir)

    in_files = [file for file in os.listdir(in_dir) if file.endswith('.txt')]

    if len(in_files) < 365:
        print('ERROR: Didn\'t find the expected number of id files in {}.'.format(in_dir))
        print('Make sure that you have all the dehydrated tweet files ready.')
        print('See "Usage" in README.md for instructions.')
        exit()

    secrets = read_secrets()

    consumer_key = secrets['consumer_key']
    consumer_secret = secrets['consumer_secret']
    access_token = secrets['access_token']
    access_token_secret = secrets['access_token_secret']

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print('ERROR: Please make sure that you have filled in the API information in secrets.toml')
        print('Visit https://apps.twitter.com/ if you haven\'t generated these yet.')
        exit()

    twarc = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    main(in_files)
