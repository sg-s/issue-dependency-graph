import os
from pathlib import Path

from beartype import beartype
from beartype.typing import List
from github import Auth, Github

local_token = None
try:
    repo_root = Path(__file__).parent.parent
    token_loc = os.path.join(repo_root, "token")

    with open(token_loc, "r") as file:
        local_token = file.read().strip()
except Exception:
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
    issues = []

    for line in txt:
        if "(" in line and ")" in line:
            a = line.find("(")
            key = line[0:a]
            name = line[a + 1 : -1]

            this_issue = dict(key=key, name=name)
            issues.append(this_issue)

    return issues
