## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development
and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You may want to ensure you have the following prerequisites before cloning the repository:

_This guide assumes you are running a linux DistrOS_

- **Python 3** installed on your system

- Access to system configurations. _[Getting Configs](README.md#System configs)_

 
### System configs

We use ` git secret` and encrypt our configuration files using gpg keys. To get access the config files and decrypt them,
setup [git secret](https://git-secret.io/). Once complete, reach out to [Philip Wafula](philipwafula2@gmailcom)
and request to have your public gpg key added to the public keys set in the `.gitsecret` file.

### Installing

To get your dev environment setup locally:


```shell script
python -m venv venv
source venv/bin/activate
```


## Authors

* **Philip wafula**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
