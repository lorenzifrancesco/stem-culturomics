import requests

import os

API_KEY = os.getenv('SEMANTIC_API_KEY')

if not API_KEY:
    raise ValueError("API key not found in environment variables.")

BASE_URL = "https://api.semanticscholar.org/graph/v1"

def get_author_id(author_name):
    """Retrieve the author ID using the author's name."""
    url = f"{BASE_URL}/author/search?query={author_name}"
    headers = {
        "x-api-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)
    if "data" in data and len(data["data"]) > 0:
        return data["data"][4]["authorId"]
    else:
        raise Exception("Author not found")

def get_papers_and_citations(author_id):
    """Retrieve all papers and their citation counts for the given author ID."""
    url = f"{BASE_URL}/author/{author_id}/papers/?fields=title,citationCount&limit=999"
    headers = {
        "x-api-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    papers = []
    for paper in data["data"]:
            papers.append({
                "title": paper["title"],
                "citation_count": paper["citationCount"]
            })
    return papers

def main(author_name):
    author_id = get_author_id(author_name)
    print(author_id)
    papers = get_papers_and_citations(author_id)
    for paper in papers:
        print("Title: {:12s}, cites: {:4d}".format(paper['title'][:20].ljust(20), paper['citation_count']))

author_name = "Luca Salasnich"
main(author_name)
