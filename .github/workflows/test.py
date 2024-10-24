import os
import requests
import json
import sys

def post_status(pull_number, msg, committers, action):
    msg = msg + '\n\n**Note:** `INFO` level messages can be ignored and the PR can be merged successfully. In case you want to know more about the linter output, kindly visit this link:#interpreting-linter-output'
    token = os.environ['GITHUB_API_TOKEN']
    base_url = 'https://api.github.com/repos/Tester2k23/jenkins-test'
    headers = {'Authorization': 'token ' + token}
    
    request_body = {'body': msg, 'event': action}
    r = requests.post(url=f'{base_url}/pulls/{pull_number}/reviews', headers=headers, json=request_body)

    if r.status_code == 200:
        print(f'[INFO]: Successfully posted status to pull request number {pull_number}.')
    else:
        print(f'[WARN]: Unable to post status to pull request number {pull_number}. Please replay the build.')
        exit(1)

def simplifyDictionary(committed_files):
    simple = []
    for c in committed_files:
        if not any(f['file'] == c['file'] for f in simple):
            simple.append(c)
    return simple

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

        committed_files = []

        if mcsr.status_code >= 200 and mcsr.status_code < 300:
            content = mcsr.json()
            print(json.dumps(content, indent=4))
            committed_files = content.get('files', [])
            commit_urls = [file['raw_url'] for file in committed_files]

            print("Committed Files URLs:")
            for file_url in commit_urls:
                print(file_url)
            mcsr_files = [z['filename'] for z in content['files']]
            for f in content['files']:
                file_name = f['filename']
                status = f['status']
                try:
                    file_name = file_name.split('/')[1]
                except IndexError:
                    pass
                try:
                    if file_name != 'prm-migrate':
                        committed_files.append({
                            'file': f['filename'],
                            'committer': content['commit']['committer']['name'],
                            'login': content['author']['login'],
                            'patch': f['patch'],
                            'sha_value': content['sha']
                        })
                    else:
                        committed_files.append({
                            'file': f['filename'],
                            'committer': content['commit']['committer']['name'],
                            'login': content['author']['login'],
                            'patch': '',
                            'sha_value': content['sha']
                        })
                except KeyError as error:
                    if status != 'renamed':
                        msg = "**![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) ERROR** Git patch error too many changes in the PR, please split the changes into multiple PRs."
                        dummy_argument = ""
                        post_status(pull_number, msg, dummy_argument, 'COMMENT')
                        exit(1)
        else:
            print('[WARN]: Unable to determine actual merge drift')

        for file in committed_files:
            if file['committer'] != 'Github' or file['committer'] is not None:
                ur = requests.get(url=base_url + '/users/' + file['committer'])
                if ur.status_code >= 200 and ur.status_code < 300:
                    continue
                else:
                    print('[WARN]: Could not verify user based on user name, attempting verification using email.')
                    er = requests.get(url=base_url + '/users/' + file['login'])
                    if er.status_code >= 200 and er.status_code < 300:
                        print('[INFO]: Identified user ' + file['login'] + '.')
                    else:
                        print('[WARN]: Could not verify user.')

        committed_files = simplifyDictionary(committed_files)
        return {'committed_files': committed_files, 'error_code': 0, 'error_message': ''}
    
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
