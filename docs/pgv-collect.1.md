<!---
%pgv-collect(1)
%
%July, 2014
-->

#NAME
pgv collect - collect changes into package.

#SYNOPSYS
**pgv collect** [--help]

**pgv collect** [-f *REVISION*] [-t *REVISION*] [-o *PATH*] [-F *FORMAT*]

**pgv collect** -d *DBNAME* [-h *HOST*] [-p *PORT*] [-U *USERNAME*] [-w|-W]
[-o *PATH*] [-F *FORMAT*]

#DESCRIPTION
**pgv collect** collects changes to package which one can be pushed to database.

If *DBNAME* is defined then *pgv* gets miniman revision(_--from_ analogue) from database.

#OPTIONS
--help
:	print help and exit;

-o *PATH* --output *PATH*
:	path to package;

-F *FORMAT* --format *FORMAT*
:	format of package;

-f *REVISION* --from *REVISION*
:	no collect changes older then *REVISION*;

-t *REVISION* --to *REVISION*
:	no collect changes newer then *REVISION*.

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
If you want to collect changes into the package on default path:

	pgv collect

You can skip psuhed changes:

	pgv collect -d mydb -h test -U test

And you can specify set of changes to collect:

	pgv collect -f <revision> -t <revision>
<!---
#SEE ALSO
`pgv(1)`
-->
