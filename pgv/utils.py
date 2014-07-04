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


def execute(config, args):
    if args.command == "init":
        import pgv.installer
        initializer = pgv.installer.Initializer(get_connection_string(args))
        initializer.initialize(args.overwrite)
    elif args.command == "make":
        import pgv.builder
        builder = pgv.builder.Builder(config)
        package = builder.make(from_rev=args.from_rev,
                               to_rev=args.to_rev,
                               format=args.format)
        path = args.output
        if path is None:
            path = config.package.path
        package.save(path)
    elif args.command == "install":
        import pgv.installer
        import pgv.package
        installer = pgv.installer.Installer(
            get_connection_string(args),
            get_isolation_level(config.database.isolation_level))
        package = pgv.package.Package(config.package.format)
        path = args.input
        if path is None:
            path = config.package.path
        package.load(path)
        installer.install(package)
    elif args.command == "skip":
        import pgv.skiplist
        skiplist = pgv.skiplist.SkipList(config)
        skiplist.add(args.revision, args.filename)
    elif args.command == "show":
        import pgv.viewer
        viewer = pgv.viewer.Viewer(config)
        if args.skipped:
            viewer.show_skipped(args.to_rev)
        else:
            viewer.show(args.with_skipped,
                        from_rev=args.from_rev,
                        to_rev=args.to_rev)
    else:
        raise Exception("Unknown command: %s" % args.command)
