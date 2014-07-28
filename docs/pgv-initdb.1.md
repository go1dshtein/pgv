% pgv-initdb(1)
%
% July, 2014

#NAME
pgv initdb - initializes new database for working with *pgv*.

#SYNOPSYS
**pgv init** --help

**pgv init** [-o] [-r REVISION] -d DBNAME [-h HOST] [-p PORT] [-U USERNAME] [-w|-W]

#DESCRIPTION
**pgv init** creates schema in the database for tracking changes.

#OPTIONS
-o --overwrite
:	recreates schema in the database if it is already exists;

-r *REVISION*
:	mark that database is updated to revision.

#CONNECTION OPTIONS
-d *DBNAME* --dbname *DBNAME*
:	name of target database;

-h *HOST* --host *HOST*
:	database server address;

-p *PORT* --port *PORT*
:	database port;

-U *USERNAME* --username *USERNAME*
:	database username;

-w --no-password
:	no ask for password;

-W --password
:	ask for password.

#EXAMPLES
Before pushing changes to new database, you should initialize it:

	pgv initdb -d mydb -h test -U test

If you want to enable versioning on existing database:

	pgv initdb -r <revision> -d mydb -h test -U test

#SEE ALSO
`pgv (1)`
