import configparser
import os

API_VERSION = '0.0.1'

# get absolute path for config file
CONFIG_FILE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

# get environment on which API is running
DEPLOYMENT_ENVIRONMENT = os.environ.get('DEPLOYMENT_NAME') or 'development'

# ensure console shows dev environment they are running on:
print('CURRENT DEPLOYMENT ENVIRONMENT: ' + DEPLOYMENT_ENVIRONMENT)

# get config file name
CONFIG_FILENAME = '{}_config.ini'.format(DEPLOYMENT_ENVIRONMENT.lower())

# define config parsers
specific_config_file_parser = configparser.ConfigParser()

# get folder for path for config files
specific_config_file_folder_path = os.path.join(CONFIG_FILE_DIRECTORY, 'config/' + CONFIG_FILENAME)


# check if specific config files are present
if not os.path.isfile(specific_config_file_folder_path):
    raise Exception("Missing Config File: {}".format(CONFIG_FILENAME))

# read files from config file paths
specific_config_file_parser.read(specific_config_file_folder_path)

# get deployment name
DEPLOYMENT_NAME = specific_config_file_parser['APP']['DEPLOYMENT_NAME']

# check that the deployment name specified by the env matches the one in the config file
if DEPLOYMENT_ENVIRONMENT.lower() != DEPLOYMENT_NAME.lower():
    raise RuntimeError('deployment name in env ({}) does not match that in config ({}), aborting'.format(
        DEPLOYMENT_ENVIRONMENT.lower(),
        DEPLOYMENT_NAME.lower()))

# define checks for deployment environment
IS_TEST = specific_config_file_parser['APP'].getboolean('IS_TEST', False)
IS_PRODUCTION = specific_config_file_parser['APP'].getboolean('IS_PRODUCTION')

# get application host
APP_HOST = specific_config_file_parser['APP']['HOST']

# get application port
APP_PORT = specific_config_file_parser['APP']['PORT']

# define redis uri
REDIS_URL = 'redis://' + specific_config_file_parser['REDIS']['URI']

# get database user
DATABASE_USER = specific_config_file_parser['DATABASE'].get('user')

# get database password
DATABASE_PASSWORD = specific_config_file_parser['DATABASE']['password']

# get database host
DATABASE_HOST = specific_config_file_parser['DATABASE']['host']

# get database name
DATABASE_NAME = specific_config_file_parser['DATABASE'].get('database')

# get database port
DATABASE_PORT = specific_config_file_parser['DATABASE'].get('port')


def get_database_uri(name, host, censored=True):
    return 'postgresql://{}:{}@{}:{}/{}'.format(DATABASE_USER,
                                                '*******' if censored else DATABASE_PASSWORD,
                                                host,
                                                DATABASE_PORT,
                                                name)


SQLALCHEMY_DATABASE_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST,
                                           censored=False)
CENSORED_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST,
                                censored=True)

print('Working database URI: ' + CENSORED_URI)
SQLALCHEMY_TRACK_MODIFICATIONS = False


