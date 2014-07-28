%pgv-init (1)
%
% July, 2014

#NAME
pgv push - applies changes to target database.

#SYNOPSYS
**pgv push** --help

**pgv push** [-c] -d *DBNAME* [-h *HOST*] [-U *USERNAME*] [-w|-W] [-i *PATH*] [-F *FORMAT*]

#DESCRIPTION
**pgv push** reads package with changes and executes SQL scripts from it on database.

#OPTIONS
--help
:	print help and exit;

-c --collect
:	collect changes to package, alias to `pgv collect && pgv push`

-i *PATH* --input *PATH*
:	path to package;

-F *FORMAT* --format *FORMAT*
:	format of package;

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
For example, you have collected package and want to push it to database *test*:

	pgv push -d test

If you want to push changes from another package:

	pgv push -d test -i path/to/package.tar.gz

#SEE ALSO
`pgv (1)`

