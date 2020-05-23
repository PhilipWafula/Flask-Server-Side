import configparser
import os

from pathlib import Path

API_VERSION = '0.0.1'

# get absolute path for config file [/faulu-api-demo/config]
CONFIG_FILE_DIRECTORY = Path(os.path.dirname(__file__)).parent

# get environment on which API is running
DEPLOYMENT_ENVIRONMENT = os.environ.get('DEPLOYMENT_NAME') or 'development'

# ensure console shows dev environment they are running on:
print('CURRENT DEPLOYMENT ENVIRONMENT: ' + DEPLOYMENT_ENVIRONMENT)

# get config file name
CONFIG_FILENAME = f'{DEPLOYMENT_ENVIRONMENT.lower()}_config.ini'

# define config file parser
config_file_parser = configparser.ConfigParser()

# get folder for path for config files
config_file_folder_path = os.path.join(CONFIG_FILE_DIRECTORY, 'config/' + CONFIG_FILENAME)

# check if specific config files are present
if not os.path.isfile(config_file_folder_path):
    raise Exception(f'Missing Config File: {CONFIG_FILENAME}')

# read files from config file paths
config_file_parser.read(config_file_folder_path)

# get deployment name
DEPLOYMENT_NAME = config_file_parser['APP']['DEPLOYMENT_NAME']

# check that the deployment name specified by the env matches the one in the config file
if DEPLOYMENT_ENVIRONMENT.lower() != DEPLOYMENT_NAME.lower():
    raise RuntimeError(f'deployment name in env ({DEPLOYMENT_ENVIRONMENT.lower()}) does not match that in config ({DEPLOYMENT_NAME.lower()}), aborting')

# define checks for deployment environment
IS_TEST = config_file_parser['APP'].getboolean('IS_TEST')
IS_PRODUCTION = config_file_parser['APP'].getboolean('IS_PRODUCTION')

# get application configs
SECRET_KEY = config_file_parser['APP'].get('secret_key')
APP_HOST = config_file_parser['APP'].get('host')
APP_PORT = config_file_parser['APP'].get('port')
APP_DOMAIN = config_file_parser['APP'].get('client_domain')
DEFAULT_COUNTRY = config_file_parser['APP'].get('default_country')

# define redis configs
REDIS_URL = 'redis://' + config_file_parser['REDIS'].get('uri')

# get database configs
DATABASE_USER = config_file_parser['DATABASE'].get('user')
DATABASE_PASSWORD = config_file_parser['DATABASE'].get('password')
DATABASE_HOST = config_file_parser['DATABASE'].get('host')
DATABASE_NAME = config_file_parser['DATABASE'].get('database')
DATABASE_PORT = config_file_parser['DATABASE'].get('port')


def get_database_uri(name, host, censored=True):
    return f'postgresql://{DATABASE_USER}:{"*******" if censored else DATABASE_PASSWORD}@{host}:{DATABASE_PORT}/{name}'


SQLALCHEMY_DATABASE_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST, censored=False)

# build censored uri for logging
CENSORED_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST, censored=True)

print('Working database URI: ' + CENSORED_URI)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# get password pepper
PASSWORD_PEPPER = config_file_parser['APP'].get('password_pepper')

# get africa's talking credentials
AFRICASTALKING_USERNAME = config_file_parser['AFRICASTALKING'].get('username')
AFRICASTALKING_API_KEY = config_file_parser['AFRICASTALKING'].get('api_key')

# define mailer settings
MAILER_SERVER = config_file_parser['MAILER'].get('server')
MAILER_PORT = config_file_parser['MAILER'].get('port')
MAILER_USERNAME = config_file_parser['MAILER'].get('username')
MAILER_PASSWORD = config_file_parser['MAILER'].get('password')
MAILER_DEFAULT_SENDER = config_file_parser['MAILER'].get('default_sender')
MAILER_MAX_EMAILS = config_file_parser['MAILER'].get('max_emails')
MAILER_USE_SSL = config_file_parser['MAILER'].getboolean('use_ssl')
MAILER_USE_TSL = config_file_parser['MAILER'].getboolean('use_tsl')
