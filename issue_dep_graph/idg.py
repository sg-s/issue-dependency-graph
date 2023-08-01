#!/Users/srinivas/Library/Caches/pypoetry/virtualenvs/issue-dep-graph-7DK3Eg2J-py3.9/bin/python
import os
from pathlib import Path

import arguably
from beartype import beartype
from beartype.typing import List, Optional
from github import Auth, Github

local_token = None
try:
    repo_root = Path(__file__).parent.parent
    token_loc = os.path.join(repo_root, "token")

    with open(token_loc, "r") as file:
        local_token = file.read().strip()
except Exception:
    pass

classes = ["classDef done fill:#8250df,color:#fff"]


def set_milestone(
    *,
    repo: str,
    token: str = local_token,
    milestone: Optional[str] = None,
):
    """for a graph of issues in the README, set a milestone
    for all those issues

    If no milestone is provided, the first milestone will be used.
    If milestone is provided, that must match the title of a valid,
    open milestone on Github
    """

    g = Github(auth=Auth.Token(token))
    r = g.get_repo(repo)

    if milestone is None:
        milestone = r.get_milestones()[0]
    else:
        for ml in r.get_milestones():
            if ml.title == milestone:
                milestone = ml
                break
        if isinstance(milestone, str):
            raise Exception("milestone is a string, which means something went wrong")

    contents = r.get_contents("README.md")
    contents = contents.decoded_content.decode().split("\n")

    # figure out what issues are referenced in the graph
    mermaid_code = extract_mermaid_code(contents)
    issues = extract_issues_from_mermaid_code(mermaid_code)
    issues = [issue["name"] for issue in issues]

    github_issues = r.get_issues(state="all")

    for issue in github_issues:
        if issue.title not in issues:
            # this is not in the graph
            continue
        if issue.milestone is None:
            issue.edit(milestone=milestone)


@arguably.command
@beartype
def sync(
    *,
    repo: Optional[str] = None,
    token: str = local_token,
):
    """Bidirectional sync between mermaid graph and issues"""

    if repo is None:
        raise Exception(
            """
===================================================
|           Repository name is not set            |
===================================================

Use --repo <repo_name> to specify the repository

            """
        )

    sync_graph_to_issues(repo=repo, token=token)
    sync_issues_to_graph(repo=repo, token=token)


@arguably.command
def sync_graph_to_issues(
    *,
    repo: str,
    token: str = local_token,
) -> None:
    """syncs mermaid graph to issues on github

    this does the following:

    - update the mermaid graph with links to those issues
    - if issue is closed, marks the node as such

    """

    g = Github(auth=Auth.Token(token))
    r = g.get_repo(repo)

    # get all issues from github
    github_issues = r.get_issues(state="all")

    # figure out what issues are referenced in the graph
    mermaid_code = get_mermaid_graph_from_repo(repo=repo, token=token)

    # make sure the mermaid code has the req classes
    insert_classes = []
    for css_class in classes:
        if css_class in mermaid_code:
            continue
        insert_classes.append(css_class)

    mermaid_code = mermaid_code[:2] + insert_classes + mermaid_code[2:]

    # get issues from mermaid text
    issues = extract_issues_from_mermaid_code(mermaid_code)

    # insert links for issues that don't have links
    new_links = []

    for issue in issues:
        if "link" in issue.keys() and issue["link"] is not None:
            continue

        key = issue["key"]
        name = issue["name"]

        # figure out which issue on github this matches
        valid_issues = [issue for issue in github_issues if issue.title == name]
        if len(valid_issues) != 1:
            continue

        valid_issue = valid_issues[0]
        this_link = valid_issue.html_url

        new_link = f'click {key} href "{this_link}" _blank'
        new_links.append(new_link)

    # insert new links into mermaid diagram
    mermaid_code = mermaid_code[0:-1] + new_links + [mermaid_code[-1]]

    # mark closed issues as done
    closed_issues = r.get_issues(state="closed")

    valid_issue_keys = []
    for issue in issues:
        key = issue["key"]
        name = issue["name"]

        # figure out which issue on github this matches
        valid_issues = [issue for issue in closed_issues if issue.title == name]

        if len(valid_issues) != 1:
            continue
        valid_issue = valid_issues[0]

        # ok this is a valid, closed issue on github.
        valid_issue_keys.append(key)

    for key in valid_issue_keys:
        issue_style = f"class {key} done"

        if issue_style not in mermaid_code:
            mermaid_code = mermaid_code[0:-1] + [issue_style] + [mermaid_code[-1]]

    # write mermaid code to remote
    write_mermaid_graph_to_repo(
        mermaid_code=mermaid_code,
        token=token,
        repo=repo,
    )


@beartype
def sync_issues_to_graph(*, repo: str, token: str = local_token):
    """syncs issues on github to issues in the graph

    Assumes that there is a mermaid graph in the README.md

    Does the following:

    - creates issues on github for every item in the graph

    """

    # read README.md from repo URL
    g = Github(auth=Auth.Token(token))
    r = g.get_repo(repo)

    # figure out what issues are referenced in the graph
    mermaid_code = get_mermaid_graph_from_repo(repo=repo, token=token)

    issues = extract_issues_from_mermaid_code(mermaid_code)
    issues = [issue["name"] for issue in issues]

    github_issues = r.get_issues(state="all")
    github_issues = [issue.title for issue in github_issues]

    # figure out issues in the graph that are not
    # actual issues on github
    missing_issues = list(set(issues).difference(set(github_issues)))

    if len(missing_issues) == 0:
        print("✅ All nodes in graph have issues on Github")
    else:
        for issue in missing_issues:
            print(f"🚧 Creating issue with title {issue}")
            r.create_issue(title=issue)

    return issues


@beartype
def extract_issues_from_mermaid_code(txt: List[str]) -> List[dict]:
    """returns a list of dicts for each issue referenced
    in the mermaid code

    each issue has the following keys:

    - key
    - name
    - style
    - link

    """
    issues = []

    # first make a list of all issues -- key and name
    for line in txt:
        if "(" in line and ")" in line:
            a = line.find("(")
            z = line.find(")")
            key = line[0:a].strip()
            name = line[a + 1 : z].strip()

            this_issue = dict(key=key, name=name)
            issues.append(this_issue)

    # now figure out which ones have links
    for line in txt:
        if "click" in line and "href" in line:
            _, key, _, link, _ = line.strip().split(" ")

            # figure out which issue this is in
            idx = [idx for idx, issue in enumerate(issues) if issue["key"] == key][0]
            issues[idx]["link"] = link

    return issues


@beartype
def get_mermaid_graph_from_repo(
    *,
    repo: str,
    token: str = local_token,
) -> List[str]:
    """scans the repo's issues and figures out where
    the mermaid graph describing issue deps is. It
    assumes that this mermaid graph is in an issue
    (typically pinned). It assumes that there is only
    one mermaid graph in an issue, and that
    only one open issue contains a mermaid graph"""

    g = Github(auth=Auth.Token(token))
    r = g.get_repo(repo)
    github_issues = r.get_issues(state="open")

    txt = None
    for issue in github_issues:
        if issue.body is None:
            continue
        if "```mermaid" in issue.body:
            txt = issue.body.split("\n")
            break

    if txt is None:
        raise Exception("Could not find a mermaid graph in open issues")

    mermaid_code = [line.replace("\r", "") for line in txt]
    mermaid_code = [line.replace("\n", "").strip() for line in mermaid_code]
    mermaid_code = [line for line in mermaid_code if len(line) > 0]
    mermaid_code = [line for line in mermaid_code if "%%" not in line]

    return mermaid_code


def write_mermaid_graph_to_repo(
    *,
    repo: str,
    token: str = local_token,
    mermaid_code: List[str],
) -> None:
    """writes a mermaid graph to a specific issue that contains
    a mermaid graph"""

    g = Github(auth=Auth.Token(token))
    r = g.get_repo(repo)
    github_issues = r.get_issues(state="open")

    for issue in github_issues:
        if issue.body is None:
            continue
        if "```mermaid" in issue.body:
            issue.edit(body="\r\n".join(mermaid_code))
            return None


if __name__ == "__main__":
    arguably.run()


def start():
    arguably.run()
