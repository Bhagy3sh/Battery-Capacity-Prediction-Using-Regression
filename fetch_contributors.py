import requests
import os
import re
from pathlib import Path

def main():
    try:
        # Get repository details
        repo_details = os.getenv('REPO_DETAILS', '').split('/')
        if len(repo_details) != 2:
            raise ValueError("Invalid repository details format in environment variable.")
        repo_owner, repo_name = repo_details
        api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contributors'

        headers = {'Authorization': f'token {os.getenv("GH_TOKEN")}'}
        
        # Fetch contributors
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch contributors: {response.status_code} - {response.text}")
        
        contributors = response.json()
        
        # Generate contributor section
        contributors_section = '<!-- readme: contributors -start -->\n'
        for contributor in contributors:
            username = contributor['login']
            avatar_url = contributor['avatar_url']
            profile_url = f'https://github.com/{username}'
            contributors_section += f'![{username}]({avatar_url}?s=50) [{username}]({profile_url})\n'
        
        contributors_section += '<!-- readme: contributors -end -->\n'
        
        # Read and update the README file
        readme_path = Path('README.md')
        if not readme_path.exists():
            raise FileNotFoundError("README.md not found.")
        
        with readme_path.open('r') as file:
            readme_content = file.read()
        
        if '<!-- readme: contributors -start -->' in readme_content:
            readme_content = re.sub(
                r'<!-- readme: contributors -start -->.*?<!-- readme: contributors -end -->',
                contributors_section,
                readme_content,
                flags=re.DOTALL
            )
        else:
            introduction_section = '## 1. Introduction\n'
            insert_position = readme_content.find(introduction_section) + len(introduction_section)
            if insert_position == -1:
                raise ValueError("Introduction section not found.")
            readme_content = (
                readme_content[:insert_position] +
                '\n' + contributors_section +
                readme_content[insert_position:]
            )
        
        with readme_path.open('w') as file:
            file.write(readme_content)
        
        print("README.md updated successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
