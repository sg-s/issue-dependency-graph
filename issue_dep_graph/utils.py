from beartype import beartype
from beartype.typing import List
from github import Auth, Github


@beartype
def sync_issues_to_graph(*, repo: str):
    pass


@beartype
def get_open_issue_titles(*, repo: str) -> List[str]:
    r = g.get_repo(repo)
    open_issues = r.get_issues(state="open")
    open_issue_titles = []
    for issue in open_issues:
        open_issue_titles.append(issue.title)

    return open_issue_titles


@beartype
def extract_mermaid_code(file_loc: str) -> List:
    mermaid_code = []
    in_mermaid = False
    with open(file_loc, "r") as file:
        txt = file.readlines()

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
