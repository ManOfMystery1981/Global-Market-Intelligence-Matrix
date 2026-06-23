import os
import requests
from bs4 import BeautifulSoup

def get_top_projects():
    url = "https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc"
    response = requests.get(url).json()
    projects = []
    # Safeguard against API issues by making sure items exist
    if "items" in response:
        for item in response["items"][:5]:
            project = {
                "name": item["full_name"],
                "description": item["description"],
                "language": item["language"],
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "open_issues": item["open_issues_count"]
            }
            projects.append(project)
    return projects

def format_projects(projects):
    result = ""
    for project in projects:
        result += f"## {project['name']}\n\n"
        result += f"### Description:\n{project['description']}\n\n"
        result += f"### Metrics:\n"
        result += f"* Languages: {project['language']}\n"
        result += f"* Stars: {project['stars']}\n"
        result += f"* Forks: {project['forks']}\n"
        result += f"* Open Issues: {project['open_issues']}\n\n"
    return result

def main():
    projects = get_top_projects()
    formatted_data = format_projects(projects)
    
    # Force explicit absolute directory file creation parameters
    root_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(root_path, "market_intelligence.md")
    
    with open(target_file, 'w') as file:
        file.write(formatted_data)
    print("💾 Market intelligence asset written successfully to root directory.")

if __name__ == "__main__":
    main()
