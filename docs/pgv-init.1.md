<!---
%pgv-init(1)
%
%July, 2014
-->

#NAME
pgv init - initializes repository in the current directory.

#SYNOPSYS
**pgv init** --help

**pgv init** [-p *PATH*]

#DESCRIPTION
**pgv init** prepare working directory.
It creates schemas directory with right structure and
minimal configuration file in the current directory.

#OPTIONS
--help
:	print help and exit;

-p *PATH* --prefix *PATH*
:	relative path to schemas base directory.

#EXAMPLES
You start new project and want to store database schema in "./database/sql" folder:

	pgv init -p database/sql

<!---
#SEE ALSO
`pgv(1)`
-->
