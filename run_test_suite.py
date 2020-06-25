import pytest
import os
import sys

if os.environ.get('DEPLOYMENT_NAME') != 'DOCKER':
    os.environ['DEPLOYMENT_NAME'] = "TESTING"

if __name__ == "__main__":

    # use '--setup-show' to show fixture SETUP and TEARDOWN
    # -k "MyClass and not method" will run TestMyClass.test_something but not TestMyClass.test_method_simple.

    # Argument definitions here https://gist.github.com/kwmiebach/3fd49612ef7a52b5ce3a
    # or (pytest --help)

    r = pytest.main(["-v", "-x", "-s", "--cov=./", "--cov-report=xml", "tests"] + sys.argv[1:])
    exit(r)
