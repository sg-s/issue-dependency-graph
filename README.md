# issue-dependency-graph

## 🧐 Problem Description 

You're working on a project, and there are a number of things
you need to do in order to get to a MVP. So you dutifully
make issues for each atom of work on Github. However, what 
Github currently doesn't support is capturing how issues
depend on each other. So it's unclear what the order of operations
is, and this problem is more complex if you have more than one
person working on a project. 


## What this is

> A way to see dependencies between issues in Github, and have that
> be synced so you can see your progress.


## What??

See if in action right here. This repo is using this tool!

[Click here](https://github.com/sg-s/issue-dependency-graph/issues/1)

## Installation

(Assuming you have poetry installed)

```bash
git clone git@github.com:sg-s/issue-dependency-graph.git
cd issue-dependency-graph
make install

```


## Usage

To use it from the CLI, run:

```bash
make install-cli
```

and restart your terminal. 

Then, you should be able:

```bash
idg -h # prints a help command
idg sync --repo "sg-s/issue-dependency-graph"
```


## License


GPL v3
