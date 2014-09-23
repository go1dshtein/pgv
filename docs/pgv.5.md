<!---
%pgv(5)
%
%July, 2014
-->

###NAME
pgv.yaml - PostgreSQL schema versioning tool configuration file.

###DESCRIPTION
**pgv** is schema versioning tool for PostgreSQL. 
It is best if **pgv.yaml** is located in top of project repository.
File can contains sections and options described below, otherwise default values will be used.

Values can be containes environment variables, like *$HOME* or *$PWD*.

###VCS
This section describes version control system(e.g.: *git*, *hg*, ...) that you want to use.
Key **provider** defines type of vcs, by default it is git.
Other keys are provider dependant.
**prefix** is prefix of target files relatively to top of repository defined by **url**.
**include** can be contains list of patterns.
All matching files will be added to revision even it does not changed.

###DATABASE
**isolation_level** describes transaction isolation level(autocommit by default).
It can be on of:
* autocommit
* read_commited
* repeatable_read
* serializable

See [psycopg2](http://initd.org/psycopg/docs/extensions.html#isolation-level-constants) for details.

###PACKAGE
This section setup default package **format** and **path**.
**format** can be:

**directory**
:	simple directory with sql files.

**tar**
:	tar archive with sql files.

**tar.gz**
:	gzipped tar archive.

**tar.bz2**
:	bzipped tar archive.

If **format** is not specified then it will computed from **path** by extension.
Default *path* is **$PWD/.pgv/dist.tar.gz**.

###LOGGING

**level** and **filename** - names speak for themselves. 
**INFO** and **$PWD/.pgv/pgv.log** by default respectively. 
**bytes** and **count** describes log rotating(1000000 and 4 by default).
<!---
#SEE ALSO
`pgv (1)`
-->
