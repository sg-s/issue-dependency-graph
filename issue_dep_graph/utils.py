import os
from pathlib import Path

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

    github_issues = r.get_issues()

    for issue in github_issues:
        if issue.title not in issues:
            # this is not in the graph
            continue
        if issue.milestone is None:
            issue.edit(milestone=milestone)


def sync_graph_to_issues(*, repo: str, token: str = local_token):
    """syncs mermaid graph to issues on github

    this does the following:

    - update the mermaid graph with links to those issues
    - if issue is closed, marks the node as such

    """

    # get all issues from github

    # get mermaid text

    # get issues from mermaid text

    pass


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
    contents = r.get_contents("README.md")

    contents = contents.decoded_content.decode().split("\n")

    # figure out what issues are referenced in the graph
    mermaid_code = extract_mermaid_code(contents)

    issues = extract_issues_from_mermaid_code(mermaid_code)
    issues = [issue["name"] for issue in issues]

    github_issues = r.get_issues()
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
def extract_mermaid_code(txt: List[str]) -> List:
    mermaid_code = []
    in_mermaid = False

    for line in txt:
        if "```mermaid" in line:
            in_mermaid = True
            continue

        if in_mermaid:
            if "```" in line:
                in_mermaid = False
            else:
                mermaid_code.append(line)

    # clean it up a little. skip comments, new lines
    mermaid_code = [line.replace("\n", "").strip() for line in mermaid_code]
    mermaid_code = [line for line in mermaid_code if len(line) > 0]
    mermaid_code = [line for line in mermaid_code if "%%" not in line]
    return mermaid_code


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
            print(line)
            _, key, _, link, _ = line.strip().split(" ")

            # figure out which issue this is in
            idx = [idx for idx, issue in enumerate(issues) if issue["key"] == key][0]
            issues[idx]["link"] = link

    return issues
