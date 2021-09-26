import os
import random

import boto3
import toml
from pathvalidate import sanitize_filename

from .covers.utils import get_covers_root
from .consts import cover_art_only_album, bucket_endpoint, access_key, secret_access_key, bucket_name


def get_cover_art_image_path(song_values=None):
    if song_values is None:
        song_values = {}
    if cover_art_only_album:
        cover_art_image_path = 'covers/generated/{}'.format(
            sanitize_filename(
                "{}-{}{}".format(str(song_values['artist_name']).split("(")[0].strip(), "Musify", ".jpg")))
    else:
        cover_art_image_path = 'covers/generated/{}'.format(
            sanitize_filename("{}-{}{}".format(str(song_values['song_name']).split("(")[0].strip(),
                                               str(song_values['artist_name']).split("(")[0].strip(), ".jpg")))

    return cover_art_image_path


def get_cover_art_from_s3(image_path, values):
    print("Get image from S3 bucket")

    try:
        s3_folder_image_directory = values['s3_folder_image_directory']
        session = boto3.session.Session()
        client = session.client('s3',
                                endpoint_url=bucket_endpoint,
                                aws_access_key_id=access_key,
                                aws_secret_access_key=secret_access_key)

        if not os.path.exists(os.path.join(get_covers_root(), 'generated')):
            os.makedirs(os.path.join(get_covers_root(), 'generated'))

        client.download_file(Bucket=bucket_name, Key=s3_folder_image_directory, Filename=image_path)
    except Exception as e:
        print("Get image from S3 bucket. Error Occurred. Reason:", e)


def update_covers_config(song_values: dict):
    current_path = os.path.abspath(os.path.dirname(__file__))

    gradient_path = os.path.join(current_path, 'covers/images/gradient')
    random_gradient = None
    if os.path.exists(gradient_path):
        gradient_count = len(
            [name for name in os.listdir(gradient_path) if os.path.isfile(os.path.join(gradient_path, name))])
        random_gradient = random.randint(1, gradient_count)
        print("Random gradient chosen: {}, gradient count: {}".format(random_gradient, gradient_count))
    if cover_art_only_album:
        data = {
            "cover": [
                {
                    "bg-image": "artwork.jpg",
                    "centre-text": True,
                    "colour-gradient": "{}".format(random_gradient),
                    "do-not-greyscale": True,
                    "gradient-opacity": 30,
                    "main-text": str(song_values['artist_name']).split("(")[0].strip(),
                    "sub-text": "Musify",
                    "sub-text-above": True,
                    "logo-opacity": 70
                }
            ],
            "config": {
                "output-size": 800
            }
        }
    else:
        data = {
            "cover": [
                {
                    "bg-image": "artwork.jpg",
                    "centre-text": True,
                    "colour-gradient": "{}".format(random_gradient),
                    "do-not-greyscale": True,
                    "gradient-opacity": 30,
                    "main-text": str(song_values['song_name']).split("(")[0].strip(),
                    "sub-text": str(song_values['artist_name']).split("(")[0].strip(),
                    "sub-text-above": True,
                    "logo-opacity": 70
                }
            ],
            "config": {
                "output-size": 800
            }
        }

    config_path = os.path.join(current_path, "covers/config.toml")

    with open(config_path, "w") as toml_file:
        toml.dump(data, toml_file)
