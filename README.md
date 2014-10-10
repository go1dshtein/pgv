
##PostgreSQL Schema Versioning Tool
**pgv** is an open source utility that makes available to support PostgreSQL schemas in a VCS repository.


###Overview
**pgv** helps you if it is needed to:

*   store SQL files in VCS repository;
*   track changes of your database schemas;
*   make possible to apply changes to various databases
* *     even if you have just local access to it.

###Installation
You can install **pgv** using *pip*:

    pip install pgv

###Usage
So, for example, you want to store database schemas in the git repository *repo.git* in folder *db*.
First of all, you need to initialize repository:

	~:    user$ git clone repo.git
	~:    user$ cd repo
	repo: user$ pgv init -p db

This command creates simple **pgv** config **pgv.yaml** in working directory and folder **db**:

    db/
      schemas/
      scripts/

According to the convention **schemas** subfolder should contains folders named after desired schemas in database.
Files inside these directories should be the SQL scripts, that describes corresponding schema.
E.g. you want to create table **foo** and function **bar** in schema **public**:

    schemas/
      public/
        tables/
          foo.sql
        functions/
          bar.sql

**Scripts** subfolder should contains some staff scripts: data fixes, migrations and so on. SQL files in this folder can contains prefix
that defines the position on execution flow. E.g. you need to add script that grants access to all objects in the database. It should be executed after all other.

    scripts/
      grants_post.sql

More details about **schemas** and **scripts** see in [pgv.1](https://github.com/go1dshtein/pgv/blob/master/docs/pgv.1.md).

Ok, you want to apply committed changes to database. Let's initialize it:

	repo: user$ pgv initdb -d test

Than push changes to database **test**:

	repo: user$ pgv push -c -d test

E.g. you've made some checks on **test** database and you've understood that function **bar** is not needed. Let's skip it:

	repo: user$ pgv show
	c2d658898d4a1369c20285464bd5bb95713173f6
	  schemas/public/tables/foo.sql
	  schemas/public/functions/bar.sql
	  scripts/grants_post.sql
	repo: user$ pgv skip -f schemas/public/functions/bar.sql c2d658898d4a1369c20285464bd5bb95713173f6
    repo: user$ git add db/.skiplist
    repo: user$ git commit
    repo: user$ pgv show
    cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3 [s]
      .skiplist

    c2d658898d4a1369c20285464bd5bb95713173f6
      schemas/public/tables/foo.sql
	  scripts/grants_post.sql

After fix you want to push changes to **production**, but database allows only local connections. Let's make package with changes:

	repo: user$ pgv collect -o changes-to-prod.tar.gz
	repo: user$ scp changes-to-prod.tar.gz prod://tmp
	repo: user$ ssh prod
	~:    user@prod$ pgv push -i /tmp/changes-to-prod.tar.gz -d prod

###Documentation

[**pgv**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv.1.md)  and
[**pgv-config**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv.5.md)

####Subcommands

[**pgv init**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-init.1.md) - initializes repository in the current directory.

[**pgv initdb**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-initdb.1.md) - initializes new database for working with **pgv**.

[**pgv collect**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-collect.1.md) - collects changes into package.

[**pgv push**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-push.1.md) - applies changes to target database.

[**pgv show**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-show.1.md) - shows revisions in the repository.

[**pgv skip**](https://github.com/go1dshtein/pgv/blob/master/docs/pgv-skip.1.md) - skips some changes from collecting to package.

### Tests

To run test use:

	tox
