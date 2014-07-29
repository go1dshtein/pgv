###PostgreSQL Schema Versioning Tool
**pgv** can help you if it is needed to:

*   store SQL files in VCS repository;
*   track changes of your database schemas;
*   make possible to apply changes to various databases
* *     even if you have just local access to it;

###Installation
You can install **pgv** using *pip*:

    pip install pgv

###Usage
So, for example, you want to store you database schemas in the git repository *repo.git* in folder *db*.
First of all, you need to initialize repository:

	~:    user$ git clone repo.git
	~:    user$ cd repo
	repo: user$ pgv init -p db

This command creates simple **pgv** config  **.pgv** in working directory and folder **db**:

*   db
* *     schemas
* *     scripts

According to the convention **schemas** subfolder should contains folder named after desired schemas in database.
All files inside these directories should be the SQL scripts, that describes corresponding schema.
E.g.: you want to create table **foo** and function **bar** in schema **public**:

*    schemas
* *     public
* * *      tables
* * * *     foo.sql
* * *      functions
* * * *     bar.sql

**Scripts** subfolder should contains some staff scripts: datafixes, migrations and so on. SQL files in this folder can contains prefix
that defines the position on execution flow. E.g. you need to add script that grants accesss to all objects in the database. It should be executed last.

*   scripts
* *   grants_post.sql

More details about **schemas** and **scripts** see in [pgv.1](https://github.com/go1dshtein/pgv/blob/master/docs/pgv.1.md).

You have added files and commit it. Ok, you want to apply changes to database. Let's initialize database:

	repo: user$ pgv initdb -d test -h test -U test -w
	
Than push changes:

	repo: user$ pgv push -c -d test -h test -U test -w
	

####Directory structure


####Commands





