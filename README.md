## Flask-Server-Side
A small flask application that provides the server side functionality for a basic SAAS application. 
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development
and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You may want to ensure you have the following prerequisites before cloning the repository:

_This guide assumes you are running a linux DistrOS_

- **Python 3** installed on your system

- Access to system configurations.

 
### Getting system configurations

We use ` git secret` and encrypt our configuration files using gpg keys. To get access the config files and decrypt them,
setup [git secret](https://git-secret.io/). Once complete, reach out to [Philip Wafula](philipwafula2@gmailcom)
and request to have your public gpg key added to the public keys set in the `.gitsecret` file.

### Installing

To get your dev environment setup locally:


```shell script
python -m venv venv
source venv/bin/activate
```

Run `setup.sh` to install all requirements, with the command:

```shell script
source setup.sh
```
This script also exports the application's parent folder to $PYTHONPATH to ensure the import system recognizes the packages
in the application.

### Database
First, setup your database `faulu_apis_development`, using the username and password from the local config file.

Next, to update your database to the latest migration file:

```shell script
cd app
python manage.py db upgrade
```

To create a new migration:

Make the modifications to the model file to reflect the database changes.

```shell script
python manage.py db migrate
```

Remember to commit the file!

Sometimes, branches split and you will have multiple heads:

```shell script
python manage.py db merge heads
```


## Authors

* [**Philip wafula**](https://github.com/PhilipWafula)
* [**Spencer Ofwiti**](https://github.com/SpencerOfwiti)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
