import requests
from bs4 import BeautifulSoup

def get_top_projects():
    url = "https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc"
    response = requests.get(url).json()
    projects = []
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
    with open('market_intelligence.md', 'w') as file:
        file.write(formatted_data)

if __name__ == "__main__":
    main()
