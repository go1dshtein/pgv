import os
import logging
import logging.handlers
import getpass
import psycopg2


def setup_logging(config):
    directory = os.path.dirname(config.filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    logger = logging.getLogger('')  # root logger
    logger.setLevel(config.level)
    filehandler = logging.handlers.RotatingFileHandler(
        config.filename, maxBytes=config.bytes, backupCount=config.count)
    filehandler.setLevel(config.level)
    fileformatter = logging.Formatter(
        "%(asctime)s: %(levelname)-7s: %(name)-12s: %(lineno)-3d: %(message)s")
    filehandler.setFormatter(fileformatter)
    logger.addHandler(filehandler)
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.INFO)
    consoleformatter = logging.Formatter("%(message)s")
    consolehandler.setFormatter(consoleformatter)
    logger.addHandler(consolehandler)


def get_connection_string(args):
    result = ""
    if args.dbname:
        result += "dbname=%s " % args.dbname
    if args.host:
        result += "host=%s " % args.host
    if args.port:
        result += "port=%d " % args.port
    if args.username:
        result += "user=%s " % args.username
    if args.prompt_password:
        result += "password=%s" % getpass.getpass("Password: ")
    return result


def get_isolation_level(isolation_level):
    if isolation_level == "autocommit":
        return psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
    elif isolation_level == "read_committed":
        return psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    elif isolation_level == "repeatable_read":
        return psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
    elif isolation_level == "serializable":
        return psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
    else:
        raise Exception("Unknown isolation_level: %s", isolation_level)


def search_config(filename=None):
    if filename is not None:
        return filename

    filename = os.path.join(os.getcwd(), ".pgv")
    while not os.path.isfile(filename):
        dirname = os.path.dirname(filename)
        if dirname == "/":
            return None
        filename = os.path.join(dirname, "..", ".pgv")
        filename = os.path.realpath(filename)
    return filename
