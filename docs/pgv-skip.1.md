<!---
%pgv-skip
%
%July, 2014
-->

###NAME
pgv skip - skips some changes from collecting to package.

###SYNOPSYS
**pgv skip** --help

**pgv skip** [[-f FILENAME] ...] REVISION

###DESCRIPTION
Sometimes it is needed to skip some changes from collecting to package.
So, you can skip whole revision or just few files from it.

**pgv skip** creates *skipfile* in schemas base directory.
Do not forget to commit it.
Changes in *skipfile* leads to appearance new revision.
So revision can contains changes in *skiplist* and nothing more.

When **pgv** collects changes to package
it looks for skiplist in last(newest) revision.
So changes in the *skiplist* can alterate resulting schema in a database.

###OPTIONS
-f *FILENAME* --filename *FILENAME*
:       skip only selected file;

*REVISION*
:       skip chnage with *REVISION*.

###EXAMPLES
If you want to skip "bad" revision:

	pgv skip <revision>

If you commit wrong file, you can skip later:

	pgv skip -f bad-file.sql <revision>

<!---
#SEE ALSO
`pgv(1)`
`pgv-show(1)`
-->
