import requests
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

API_KEY = os.getenv('SEMANTIC_API_KEY')

if not API_KEY:
    raise ValueError("API key not found in environment variables.")

BASE_URL = "https://api.semanticscholar.org/graph/v1"


def get_author_id(author_name):
    """Retrieve the author ID using the author's name."""
    url = f"{BASE_URL}/author/search?query={author_name}&fields=authorId,name,citationCount"
    headers = {
        "x-api-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)
    
    if "data" in data and len(data["data"]) > 0:
        # Initialize variables to track the author with the highest citations
        max_citations = -1
        author_id_with_max_citations = None

        # Loop through the authors to find the one with the highest citations
        for author in data["data"]:
            print(author)
            author_id = author.get("authorId")
            citations = author.get("citationCount", 0)
            print(citations)
            if citations > max_citations:
                max_citations = citations
                author_id_with_max_citations = author_id

        if author_id_with_max_citations is not None:
            return author_id_with_max_citations
        
    raise Exception("Author not found or no citations available")

def get_papers_and_citations(author_id):
    """Retrieve all papers and their citation counts for the given author ID."""
    url = f"{BASE_URL}/author/{author_id}/papers/?fields=title,citationCount&limit=999" # set to maximum allowed by API key
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
    citations = np.zeros(len(papers))
    print("\n", len(papers), " papers have been found!")
    for id, paper in enumerate(papers):
      print("Title: {:12s}, cites: {:4d}".format(paper['title'][:50].ljust(50), paper['citation_count']))
      citations[id] = paper['citation_count'] 


    # optional remove zero citations
    citations = np.array(citations[citations > 1])
    nbins = int(round(len(papers)/3))
    plt.figure(figsize=(4, 3.4))
    plt.hist(citations, bins=nbins, color='skyblue', edgecolor='black')  # 30 bins for better visualization
    plt.xlabel(r'\textcent')
    plt.ylabel(r'Number of Papers')
    plt.grid(axis='y')  
    plt.tight_layout()
    plt.savefig("media/" + author_name)

    print(citations)
    plt.figure(figsize=(4, 3.4))
    sns.kdeplot(citations, bw_adjust=0.5)  # bw_adjust adjust smoothing
    plt.xlabel(r'\textcent')
    plt.ylabel(r'Paper density')
    plt.grid(axis='x')  
    plt.tight_layout()
    plt.savefig("media/kde_" + author_name)
    
author_name = "Luca Salasnich"
main(author_name)
