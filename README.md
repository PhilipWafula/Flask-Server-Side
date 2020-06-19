## Flask-Server-Side

![Flask Server-Side CI](https://github.com/PhilipWafula/Flask-Server-Side/workflows/Flask%20Server-Side%20CI/badge.svg)
![codecov](https://codecov.io/gh/PhilipWafula/Flask-Server-Side/branch/master/graph/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A small flask application that provides the server side functionality for a basic SAAS application.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development
and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You may want to ensure you have the following prerequisites before cloning the repository:

_This guide assumes you are running a linux DistrOS_

- **Python 3** installed on your system.
- Redis
- PostgreSQL
- Access to system settingss.


### Getting system configs

We use ` git secret` and encrypt our settings files using gpg keys. To get access the secret files and decrypt them,
setup [git secret](https://git-secret.io/). Once complete, reach out to [Philip Wafula](philipwafula2@gmailcom)
and request to have your public gpg key added to the public keys set in the `.gitsecret` file.

Once your credentials have been added to the key ring, decrypt the config files:
```shell script
git secret reveal
```

Succeeding a successful decryption of the config files, change the settings to match your local environment
set up:

```
password                                     = your_password
database                                     = flask_server_side_development/flask_server_side_testing
user                                         = your_database_user
```

### Installing

To get your dev environment setup locally:


```shell script
python3 -m venv venv
source venv/bin/activate
```

Run `install_requirements.sh` to install all requirements, with the command:

```shell script
cd devtools/
source install_requirements.sh
```
To get a fully functional instance of the application set up from scratch, run the 
`setup_development_environment.sh` script from the devtools folder:

```shell script
source setup_development_environment.sh
```
The script provides an interactive interface to add your db postgres user and password. It then drops and rebuilds the database
and seeds system data.

#### Exporting app path to python path
This script also exports the application's parent folder to `$PYTHONPATH ` to ensure the import system recognizes the packages
in the application. In the event that you run into an error regarding the app module not being detected on the python path,
run the `quick_env.sh`

```shell script
source quick_env.sh
```

### Database
First, setup your postgres database `flask_server_side_development`, using the username and password from the local config file.

Next, to update your database to the latest migration file:

```shell script
cd app
python3 manage.py db upgrade
```

To create a new migration:

Make the modifications to the model file to reflect the database changes.

```shell script
python3 manage.py db migrate
```

Remember to commit the file!

Sometimes, branches split and you will have multiple heads:

```shell script
python3 manage.py db merge heads
```

### Testing
To conduct some gorilla tests on the API, import the provided `test_apis_postman_collections.json` into your postman
application and run the tests from there.

### Background tasks
To run background tasks such as sending actual emails, ensure you're in the root directory then run:

```shell script
celery worker -A worker.tasks --loglevel=info
```

## Contributing
Contributions are welcome. Questions can be asked on the issues page. Before creating a new issue, please take a moment
to search and make sure a similar issue does not already exist. If one does exist, you can comment (most simply even
with just a :+1:) to show your support for that issue.

If you have direct contributions you would like considered for incorporation into the project you can fork this
repository and submit a pull request for review, ensure you follow the the [Contribution guidelines](CONTRIBUTING.md)

## Authors

* [**Philip wafula**](https://github.com/PhilipWafula)
* [**Spencer Ofwiti**](https://github.com/SpencerOfwiti)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
