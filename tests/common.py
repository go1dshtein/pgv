import os


def is_travis():
    return 'TRAVIS_BUILD_ID' in os.environ
