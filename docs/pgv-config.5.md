<!---
%pgv(5)
%
%July, 2014
-->

#NAME
pgv - PostgreSQL schema versioning tool configuration file.

#DESCRIPTION
**pgv** is schema versioning tool for PostgreSQL.

#VCS
This section describes version control system(e.g.: git, hg, ...) that you want to use.
Key *provider* defines type of vcs, by default it is git.
Other keys are provider dependant.
If option *url* is not defined then working directory will be used.
*Prefix* is prefix of target files relatively to *url*.
*Include* can be contains list of patterns.
All matching files will be added to revision even it does not changed.

#DATABASE
*Isolation_level* describes transaction isolation level(autocommit by default).
It can be on of:
* autocommit
* read_commited
* repeatable_read
* serializable
See [psycopg2](http://initd.org/psycopg/docs/extensions.html#isolation-level-constants) for details.

#PACKAGE
This section setup default package *format* and *path*.
*Format* can be:
**directory**
:	simple directory with sql files.

**tar**
:	tar archive with sql files.

**tar.gz**
:	gzipped tar archive.

**tar.bz2**
:	bzipped tar archive.

#LOGGING


<!---
#SEE ALSO
`pgv (1)`
-->
