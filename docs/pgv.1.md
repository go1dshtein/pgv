<!---
%pgv(1)
%
%July, 2014
-->

#NAME
pgv - PostgreSQL schema versioning tool.

#SYNOPSYS
**pgv** [--help] [-c *CONFIG*] *COMMAND*

#DESCRIPTION
**pgv** is schema versioning tool for PostgreSQL.

It helps to support database schemas in VCS repository and push changes into
database as needed - revision by revision.
Revision is native revision of your VCS, so no mappings are needed.

All information about files which you need to apply to database should be stored in specific
directory structure. See [CODE STRUCTURE](#code-structure) below for further details.

Information of applied changes will be stored to schema *pgv* of target database.

#COMMANDS
**init**
:       initializes repository in the current directory;

**initdb**
:       initializes new database for working with *pgv*;


**collect**
:       collect changes into package;

**push**
:       applies changes to target database;

**skip**
:       marks specified revisions(whole or some files) for skip in collecting;

**show**
:       shows information about revisions in repository and database.

#OPTIONS
--help
:       print help and exit;

-c *CONFIG* --config *CONFIG*
:       use *CONFIG* instead of VCS repository wide *pgv.yaml* configuration file.

#CODE STRUCTURE
*pgv* divide all sql file into two folders - schemas and scripts.
Schemas folder containes subfolders named after desired schemas, e.g.: public.
It contains sql files which defines schema - tables, views, types, functions etc.

Scripts folder contains staff sql procedures like creating users, grants, data fixes etc.
It has specific names, like <name>_<event>.sql.

Event defines the place in flow when script should be applied:

**start**
:       before all other, once per revision;

**stop**
:       after all other, once per revision;

**pre**
:       before applying schema, once per schema;

**post**
:       after applying schema, once per schema;

**success**
:       after successfully finished schema script;

**error**
:       after unsuccessfully finished schema script.

If scripts does not ends with *event*
then it will never be applied. But it can be included to another script using *\\i*
or
*\\ir*
directive.

Scripts can contains placeholders like *%(variable)s* for variables.
Supported variables are:

**revision**
:       currently applying revision;

**schema**
:       currently applying schema, if available;

**filename**
:       currently applying schema filename, if available;

#FILES
By default *pgv* searches for *pgv.yaml*
configuration file in current and parent directories recursively.
This file describes location of directory with SQL files,
type of generated package, permanently included files and logging.
More info about configuration file see in `pgv (5)`.

<!---
#SEE ALSO
`pgv (5)`
`pgv-init (1)`
`pgv-collect (1)`
`pgv-push (1)`
`pgv-skip (1)`
`pgv-show (1)`
-->
