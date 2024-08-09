import requests
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
import time

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
    if "data" in data and len(data["data"]) > 0:
        # Initialize variables to track the author with the highest citations
        max_citations = -1
        author_id_with_max_citations = None

        # Loop through the authors to find the one with the highest citations
        for author in data["data"]:
            author_id = author.get("authorId")
            citations = author.get("citationCount", 0)
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

def plot_author_data(author_name, citations, subplot_index, total_authors):
    """Plot histogram and KDE for a single author."""
    nbins = int(round(len(citations) / 3))
    # threshold = np.max(citations) / 20
    threshold = 0
    citations = np.array(citations[citations>threshold])
     
    # Histogram
    plt.subplot(total_authors, 2, subplot_index * 2 - 1)
    plt.hist(citations, bins=nbins, color='skyblue', edgecolor='black')
    plt.xlabel('Citation Count')
    plt.ylabel('Number of Papers')
    plt.title(f'Histogram for {author_name}')
    plt.grid(axis='y')

    # KDE Plot
    plt.subplot(total_authors, 2, subplot_index * 2)
    sns.kdeplot(citations, bw_adjust=0.5)
    plt.xlabel('Citation Count')
    plt.ylabel('Density')
    plt.title(f'KDE for {author_name}')
    plt.grid(axis='x')

def main():
    # Read author names from CSV
    author_names = pd.read_csv("input/names.csv")["name"].tolist()  # Adjust this based on the actual column name

    total_authors = len(author_names)
    plt.figure(figsize=(8, total_authors * 4))

    for index, author_name in enumerate(author_names):
      persevere = 10
      while persevere:
        try:
            author_id = get_author_id(author_name)
            time.sleep(np.random.exponential(0.2))
            papers = get_papers_and_citations(author_id)
            citations = np.array([paper['citation_count'] for paper in papers if paper['citation_count'] > 1])
            
            print(f"\n{len(papers)} papers found for {author_name}!")
            plot_author_data(author_name, citations, index + 1, total_authors)
            persevere = 0
        except Exception as e:
            print(f"Error processing {author_name}: {e}")
            persevere -= 1
    plt.tight_layout()
    plt.savefig("media/combined_authors_plot.pdf")  # Save the combined plot
    # plt.show()  # Show the combined plot

if __name__ == "__main__":
    main()