import warnings
# Try to suppress before any imports
warnings.filterwarnings("ignore", category=RuntimeWarning)
from duckduckgo_search import DDGS
import sys

def web_search(query):
    print(f"[*] Testing web_search -> {query}")
    try:
        results = []
        with DDGS() as ddgs:
            # 1. Try text search
            print("DEBUG: Trying text search...")
            try:
                for r in ddgs.text(keywords=query, max_results=5):
                    results.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}\n")
            except Exception as e:
                print(f"DEBUG: Text search error: {e}")

            # 2. Try news search
            is_news_query = any(word in query.lower() for word in ["news", "latest", "current", "today", "trending"])
            if not results or is_news_query:
                print("DEBUG: Trying news search...")
                try:
                    for r in ddgs.news(keywords=query, max_results=5):
                        results.append(f"Title: {r.get('title')}\nLink: {r.get('url') or r.get('href')}\nSnippet: {r.get('body')}\nSource: {r.get('source')}\n")
                except Exception as e:
                    print(f"DEBUG: News search error: {e}")
            
            # 3. Try videos search
            if "video" in query.lower() or "youtube" in query.lower():
                print("DEBUG: Trying video search...")
                try:
                    # Note: Newer versions use keywords=, region='wt-wt', etc.
                    for r in ddgs.videos(keywords=query, max_results=5):
                        results.append(f"Title: {r.get('title')}\nLink: {r.get('content') or r.get('embed_url')}\nDescription: {r.get('description')}\n")
                except Exception as e:
                    print(f"DEBUG: Video search error: {e}")

        return "\n---\n".join(results)
    except Exception as e:
        return f"Error searching the web: {str(e)}"

if __name__ == "__main__":
    query = "trending videos on YouTube"
    res = web_search(query)
    print("\n--- Results ---")
    if res:
        print(res[:1000] + "...")
    else:
        print("EMPTY RESULTS")
    print("---------------")
