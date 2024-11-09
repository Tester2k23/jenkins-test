import os
import requests
from typing import Union


class GitHubPostStatus:
    def __init__(self, pull_number: str, msg: str, committers: Union[str, dict], action: str):
        self.pull_number = pull_number
        self.msg = msg
        self.committers = committers
        self.action = action
        self.token = os.environ['GITHUB_API_TOKEN']
        self.base_url = 'https://api.github.com/repos/Tester2k23/jenkins-test'
        self.headers = {'Authorization': f'token {self.token}'}

    def format_message(self):
        """
        Format the message for posting, appending additional information.
        """
        formatted_msg = (
            f"{self.msg}\n\n"
            "**Note:** `INFO` level msg can be ignored and PR can be merged successfully. "
            "In case you want to know more about the linter output, kindly visit this link "
            "https://github.com/uhg-internal/hcc-dp-kaas-prod#interpreting-linter-output"
        )
        return formatted_msg

    def post_status(self):
        """
        Post the status to the GitHub pull request.
        """
        request_body = {
            'body': self.format_message(),
            'event': self.action
        }

        url = f"{self.base_url}/pulls/{self.pull_number}/reviews"
        response = requests.post(url=url, headers=self.headers, json=request_body)

        if response.status_code == 200:
            print(f'[INFO]: Successfully posted status to pull request number {self.pull_number}.')
        else:
            print(f'[WARN]: Unable to post status to pull request number {self.pull_number}. Please replay the build.')
            exit(1)


# Example of using the class
def post_status_example():
    pull_number = "34"
    msg = "Some linter output message"
    committers = {"committer1": "details", "committer2": "details"}  # Example committers
    action = "approved"

    github_status = GitHubPostStatus(pull_number, msg, committers, action)
    github_status.post_status()
