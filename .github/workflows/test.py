import os
import requests
import json
import sys

def main(pull_number):
    token = os.environ['GITHUB_API_TOKEN']
    base_url = 'https://api.github.com/repos/Tester2k23/jenkins-test'
    headers = {'Authorization': 'token ' + token}

    # Get pull request details
    pr_url = f'{base_url}/pulls/{pull_number}'
    r = requests.get(url=pr_url, headers=headers)

    if r.status_code == 200:
        content = r.json()
        link = content['_links']['commits']['href']
        sha = content['head']['sha']
        mcs = content['merge_commit_sha']
        
        print(f"PR Commit Link: {link}")
        print(f"SHA: {sha}")
        print(f"Merge Commit SHA: {mcs}")

        # Get the merge commit details
        mcsr_url = f'{base_url}/commits/{mcs}'
        mcsr = requests.get(url=mcsr_url, headers=headers)

        if mcsr.status_code >= 200 and mcsr.status_code < 300:
            mcsr_content = mcsr.json()
            print(json.dumps(mcsr_content, indent=4))
            committed_files = mcsr_content.get('files', [])
            commit_urls = [file['raw_url'] for file in committed_files]
            
            print("Committed Files URLs:")
            for file_url in commit_urls:
                print(file_url)

            return {'committed_files': commit_urls, 'error_code': 0, 'error_message': None}
        else:
            return {'committed_files': None, 'error_code': 2, 'error_message': 'Unable to get merge commit content.'}
    else:
        return {'committed_files': None, 'error_code': 1, 'error_message': 'Unable to get pull request content.'}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <pull_number>")
        sys.exit(1)

    pull_number = sys.argv[1]
    result = main(pull_number)
    
    if result['error_code'] != 0:
        print(f"Error: {result['error_message']}")
    else:
        print("Success:", result['committed_files'])
