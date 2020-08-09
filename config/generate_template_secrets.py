# system imports
import argparse
import base64
import configparser
import os
import sys
from functools import partial


def add_value(config_parser, section, key, value):
    try:
        config_parser[section]
    except KeyError:
        config_parser[section] = {}

    try:
        value = value.decode()
    except AttributeError:
        pass

    config_parser[section][key] = str(value)


template_dir = './templates'
specific_secrets_read_path = os.path.join(template_dir, 'specific_secrets_template.ini')
common_secrets_read_path = os.path.join(template_dir, 'common_secrets_template.ini')
if not os.path.isdir(template_dir):
    os.mkdir(template_dir)


def generate_specific_secrets(write_path):
    specific_secrets_parser = configparser.ConfigParser()
    specific_secrets_parser.read(specific_secrets_read_path)

    add_specific_secret = partial(add_value, specific_secrets_parser)

    APP = 'APP'
    add_specific_secret(APP, 'password_pepper', base64.b64encode(os.urandom(32)))
    add_specific_secret(APP, 'secret_key', base64.b64encode(os.urandom(32)))

    DATABASE = 'DATABASE'
    username = os.environ.get('PGUSER', 'postgres')
    password = os.environ.get('PGPASSWORD', 'password')
    add_specific_secret(DATABASE, 'user', username)
    add_specific_secret(DATABASE, 'password', password)

    AFRICASTALKING = 'AFRICASTALKING'
    add_specific_secret(AFRICASTALKING, 'username', 'Sandbox')
    add_specific_secret(AFRICASTALKING, 'api_key', 'your_sandbox_api_key')

    DARAJA = 'DARAJA'
    add_specific_secret(DARAJA, 'consumer_key', 'your_consumer_key')
    add_specific_secret(DARAJA, 'consumer_secret', 'your_consumer_secret')

    with open(write_path, 'w') as f:
        specific_secrets_parser.write(f)


def generate_common_secrets(write_path):
    common_secrets_parser = configparser.ConfigParser()
    common_secrets_parser.read(common_secrets_read_path)

    add_common_secret = partial(add_value, common_secrets_parser)

    MAILER = 'MAILER'
    add_common_secret(MAILER, 'server', '')
    add_common_secret(MAILER, 'port', '')
    add_common_secret(MAILER, 'username', '')
    add_common_secret(MAILER, 'password', '')
    add_common_secret(MAILER, 'default_sender', '')
    add_common_secret(MAILER, 'max_emails', '')
    add_common_secret(MAILER, 'use_ssl', '')
    add_common_secret(MAILER, 'use_tsl', '')

    with open(write_path, 'w') as f:
        common_secrets_parser.write(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate template secrets.')

    parser.add_argument('-n', '--name', default='development',
                        help='The deployment name. Will produce file like "foo_secrets.ini"')

    args = parser.parse_args()

    specific_secrets_write_path = os.path.join(template_dir, f'{args.name}_secrets_template.ini')
    common_secrets_write_path = os.path.join(template_dir, 'common_secrets_template.ini')

    print(f'Generating deployment specific ({args.name}) secrets')
    generate_specific_secrets(specific_secrets_write_path)
    print('Generating common secrets')
    generate_common_secrets(common_secrets_write_path)
    print('Generated reasonable secrets, please modify as required')
