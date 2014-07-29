<!---
%pgv-show(1)
%
%July, 2014
-->

###NAME
pgv show - shows revisions in the repository.

###SYNOPSYS
**pgv show** --help

**pgv show** [-s|-w] [-f REVISION] [-t REVISION]

###OPTIONS
-s --skipped
:       shows only skipped changes;

-w --with-skipped
:       shows skipped changes;

-f *REVISION* --from *REVISION*
:	no collect changes older then *REVISION*;

-t *REVISION* --to *REVISION*
:	no collect changes newer then *REVISION*.

###EXAMPLES
You can see changes that will be collected:

	pgv show

If you want to see what changes are skipped:

	pgv show -s

Or you can see all changes:

	pgv show -w

<!---
#SEE ALSO
`pgv(1)`
-->
