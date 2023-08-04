# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["issue_dep_graph"]

package_data = {"": ["*"]}

install_requires = [
    "arguably>=1.2.5,<2.0.0",
    "beartype>=0.15.0,<0.16.0",
    "poetry2setup>=1.1.0,<2.0.0",
    "pygithub>=1.59.0,<2.0.0",
]

setup_kwargs = {
    "name": "issue-dep-graph",
    "version": "0.2.0",
    "description": "",
    "long_description": "# issue-dependency-graph\n\n## 🧐 Problem Description \n\nYou're working on a project, and there are a number of things\nyou need to do in order to get to a MVP. So you dutifully\nmake issues for each atom of work on Github. However, what \nGithub currently doesn't support is capturing how issues\ndepend on each other. So it's unclear what the order of operations\nis, and this problem is more complex if you have more than one\nperson working on a project. \n\n\n## What this is\n\n> A way to see dependencies between issues in Github, and have that\n> be synced so you can see your progress.\n\n\n## What??\n\nSee if in action right here. This repo is using this tool!\n\n[Click here](https://github.com/sg-s/issue-dependency-graph/issues/1)\n\n## Installation\n\n(Assuming you have poetry installed)\n\n```bash\ngit clone git@github.com:sg-s/issue-dependency-graph.git\ncd issue-dependency-graph\nmake install\n\n```\n\n\n## Usage\n\nTo use it from the CLI, run:\n\n```bash\nmake install-cli\n```\n\nand restart your terminal. \n\nThen, you should be able:\n\n```bash\nidg -h # prints a help command\nidg sync --repo \"sg-s/issue-dependency-graph\"\n```\n\n\n## License\n\n\nGPL v3\n",
    "author": "Srinivas Gorur-Shandilya",
    "author_email": "code@srinivas.gs",
    "maintainer": "None",
    "maintainer_email": "None",
    "url": "None",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.9,<4.0",
}


setup(**setup_kwargs)
