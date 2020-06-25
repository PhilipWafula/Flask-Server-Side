import configparser
import logging
import os

from pathlib import Path

API_VERSION = "0.0.1"

log = logging.getLogger(__file__)

# get absolute path for config file [/flask-server-side/config]
CONFIG_FILE_DIRECTORY = Path(os.path.dirname(__file__)).parent

# get environment on which API is running
DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_NAME") or "development"

# ensure console shows dev environment they are running on:
log.info("CURRENT DEPLOYMENT ENVIRONMENT: " + DEPLOYMENT_ENVIRONMENT)

# get config file name
COMMON_CONFIG_FILENAME = "common_secrets.ini"
SECRETS_CONFIG_FILENAME = f"{DEPLOYMENT_ENVIRONMENT.lower()}_secrets.ini"
PUBLIC_CONFIG_FILENAME = f"{DEPLOYMENT_ENVIRONMENT.lower()}_config.ini"


# define config file parser
common_config_file_parser = configparser.ConfigParser()
public_config_file_parser = configparser.ConfigParser()
secrets_config_file_parser = configparser.ConfigParser()

# get folder for path for config files
public_config_files_folder_path = os.path.join(
    CONFIG_FILE_DIRECTORY, "config/public/" + PUBLIC_CONFIG_FILENAME
)
common_config_files_folder_path = os.path.join(
    CONFIG_FILE_DIRECTORY, "config/secret/" + COMMON_CONFIG_FILENAME
)
secret_config_files_folder_path = os.path.join(
    CONFIG_FILE_DIRECTORY, "config/secret/" + SECRETS_CONFIG_FILENAME
)

# check if specific config files are present
if not os.path.isfile(common_config_files_folder_path):
    raise Exception(f"Missing Common Config File: {COMMON_CONFIG_FILENAME}")

if not os.path.isfile(public_config_files_folder_path):
    raise Exception(f"Missing Config File: {PUBLIC_CONFIG_FILENAME}")

# read files from config file paths
common_config_file_parser.read(common_config_files_folder_path)
public_config_file_parser.read(public_config_files_folder_path)
secrets_config_file_parser.read(secret_config_files_folder_path)

# get deployment name
DEPLOYMENT_NAME = public_config_file_parser["APP"]["DEPLOYMENT_NAME"]

# check that the deployment name specified by the env matches the one in the config file
if DEPLOYMENT_ENVIRONMENT.lower() != DEPLOYMENT_NAME.lower():
    raise RuntimeError(
        f"deployment name in env ({DEPLOYMENT_ENVIRONMENT.lower()}) does not match that in config ({DEPLOYMENT_NAME.lower()}), aborting"
    )

# define checks for deployment environment
IS_TEST = public_config_file_parser["APP"].getboolean("IS_TEST")
IS_PRODUCTION = public_config_file_parser["APP"].getboolean("IS_PRODUCTION")

# get application configs
SECRET_KEY = secrets_config_file_parser["APP"].get("secret_key")
APP_HOST = public_config_file_parser["APP"].get("host")
APP_PORT = public_config_file_parser["APP"].get("port")
APP_DOMAIN = public_config_file_parser["APP"].get("client_domain")
DEFAULT_COUNTRY = public_config_file_parser["APP"].get("default_country")

# define redis configs
REDIS_URL = "redis://" + public_config_file_parser["REDIS"].get("uri")

# get database configs
DATABASE_USER = public_config_file_parser["DATABASE"].get("user")
DATABASE_PASSWORD = public_config_file_parser["DATABASE"].get("password")
DATABASE_HOST = public_config_file_parser["DATABASE"].get("host")
DATABASE_NAME = public_config_file_parser["DATABASE"].get("database")
DATABASE_PORT = public_config_file_parser["DATABASE"].get("port")


def get_database_uri(name, host, censored=True):
    return f'postgresql://{DATABASE_USER}:{"*******" if censored else DATABASE_PASSWORD}@{host}:{DATABASE_PORT}/{name}'


SQLALCHEMY_DATABASE_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST, censored=False)

# build censored uri for logging
CENSORED_URI = get_database_uri(DATABASE_NAME, DATABASE_HOST, censored=True)

log.info("Working database URI: " + CENSORED_URI)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# get password pepper
PASSWORD_PEPPER = secrets_config_file_parser["APP"].get("password_pepper")

# get africa's talking credentials
AFRICASTALKING_USERNAME = secrets_config_file_parser["AFRICASTALKING"].get("username")
AFRICASTALKING_API_KEY = secrets_config_file_parser["AFRICASTALKING"].get("api_key")
AFRICASTALKING_PRODUCT_NAME = secrets_config_file_parser["AFRICASTALKING"].get(
    "product_name"
)
AFRICASTALKING_MOBILE_CHECKOUT_URL = public_config_file_parser["AFRICASTALKING"].get(
    "mobile_checkout"
)
AFRICASTALKING_MOBILE_B2B_URL = public_config_file_parser["AFRICASTALKING"].get(
    "mobile_b2b"
)
AFRICASTALKING_MOBILE_B2C_URL = public_config_file_parser["AFRICASTALKING"].get(
    "mobile_b2c"
)
AFRICAS_TALKING_WALLET_BALANCE = public_config_file_parser["AFRICASTALKING"].get(
    "wallet_balance"
)

# define mailer settings
MAILER_SERVER = common_config_file_parser["MAILER"].get("server")
MAILER_PORT = common_config_file_parser["MAILER"].get("port")
MAILER_USERNAME = common_config_file_parser["MAILER"].get("username")
MAILER_PASSWORD = common_config_file_parser["MAILER"].get("password")
MAILER_DEFAULT_SENDER = common_config_file_parser["MAILER"].get("default_sender")
MAILER_MAX_EMAILS = common_config_file_parser["MAILER"].get("max_emails")
MAILER_USE_SSL = common_config_file_parser["MAILER"].getboolean("use_ssl")
MAILER_USE_TSL = common_config_file_parser["MAILER"].getboolean("use_tsl")
