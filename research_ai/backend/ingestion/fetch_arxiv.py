import json
import os
import arxiv

def fetch_arxiv_papers(max_results=1000):
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw_papers', 'arxiv_papers.json')
    output_path = os.path.abspath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Fetching {max_results} papers from ArXiv...")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG OR cat:cs.CV",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    
    for result in client.results(search):
        paper = {
            "paper_id": result.get_short_id(),
            "title": result.title,
            "abstract": result.summary,
            "authors": [author.name for author in result.authors],
            "categories": result.categories,
            "published_date": result.published.isoformat(),
            "pdf_url": result.pdf_url
        }
        papers.append(paper)
        if len(papers) % 100 == 0:
            print(f"Fetched {len(papers)} papers...")
            
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully saved {len(papers)} papers to {output_path}")

    # S3 upload (additive — does not affect local pipeline)
    try:
        from utils.storage_manager import storage
        storage.upload_file(output_path, "raw_papers/arxiv_papers.json")
    except Exception:
        pass  # S3 is optional; local file is the source of truth

if __name__ == "__main__":
    fetch_arxiv_papers(1000)
