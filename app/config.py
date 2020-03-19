import configparser
import os

API_VERSION = '0.0.1'

# get absolute path for config file [/faulu-api-demo/config]
CONFIG_FILE_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), ".."))

# get environment on which API is running
DEPLOYMENT_ENVIRONMENT = os.environ.get('DEPLOYMENT_NAME') or 'development'

# ensure console shows dev environment they are running on:
print('CURRENT DEPLOYMENT ENVIRONMENT: ' + DEPLOYMENT_ENVIRONMENT)

# get config file name
CONFIG_FILENAME = '{}_config.ini'.format(DEPLOYMENT_ENVIRONMENT.lower())

# define config file parser
config_file_parser = configparser.ConfigParser()

# get folder for path for config files
config_file_folder_path = os.path.join(CONFIG_FILE_DIRECTORY, 'config/' + CONFIG_FILENAME)

# check if specific config files are present
if not os.path.isfile(config_file_folder_path):
    raise Exception("Missing Config File: {}".format(CONFIG_FILENAME))

# read files from config file paths
config_file_parser.read(config_file_folder_path)

# get deployment name
DEPLOYMENT_NAME = config_file_parser['APP']['DEPLOYMENT_NAME']

# check that the deployment name specified by the env matches the one in the config file
if DEPLOYMENT_ENVIRONMENT.lower() != DEPLOYMENT_NAME.lower():
    raise RuntimeError('deployment name in env ({}) does not match that in config ({}), aborting'.format(
        DEPLOYMENT_ENVIRONMENT.lower(),
        DEPLOYMENT_NAME.lower()))

# define checks for deployment environment
IS_TEST = config_file_parser['APP'].getboolean('IS_TEST', False)
IS_PRODUCTION = config_file_parser['APP'].getboolean('IS_PRODUCTION')

# get secret key
SECRET_KEY = config_file_parser['APP'].get('secret_key')

# get application host
APP_HOST = config_file_parser['APP']['HOST']

# get application port
APP_PORT = config_file_parser['APP']['PORT']

# get default country
DEFAULT_COUNTRY = config_file_parser['APP']['DEFAULT_COUNTRY']

# define redis uri
REDIS_URL = 'redis://' + config_file_parser['REDIS']['URI']

# get database user
DATABASE_USER = config_file_parser['DATABASE'].get('user')

# get database password
DATABASE_PASSWORD = config_file_parser['DATABASE']['password']

# get database host
DATABASE_HOST = config_file_parser['DATABASE']['host']

# get database name
DATABASE_NAME = config_file_parser['DATABASE'].get('database')

# get database port
DATABASE_PORT = config_file_parser['DATABASE'].get('port')


def get_database_uri(name, host, censored=True):
    return 'postgresql://{}:{}@{}:{}/{}'.format(DATABASE_USER,
                                                '*******' if censored else DATABASE_PASSWORD,
                                                host,
                                                DATABASE_PORT,
                                                name)


# build sqlalchemy uri
SQLALCHEMY_DATABASE_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST,
                                           censored=False)

# build censored uri for logging
CENSORED_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST,
                                censored=True)

print('Working database URI: ' + CENSORED_URI)

# define sqlalchemy track modifications
SQLALCHEMY_TRACK_MODIFICATIONS = False

# get password pepper
PASSWORD_PEPPER = config_file_parser['APP']['PASSWORD_PEPPER']

# get africa's talking username
AFRICASTALKING_USERNAME = config_file_parser['AFRICASTALKING']['USERNAME']

# get africa's talking api key
AFRICASTALKING_API_KEY = config_file_parser['AFRICASTALKING']['API_KEY']
