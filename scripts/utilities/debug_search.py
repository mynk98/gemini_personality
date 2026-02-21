import warnings
warnings.filterwarnings("ignore")
from duckduckgo_search import DDGS
import sys

def test_search_v8(query):
    print(f"[*] Searching with v8.1.1 for: {query}")
    with DDGS() as ddgs:
        print("\n--- Testing .text() standard ---")
        try:
            results = ddgs.text(keywords=query, max_results=5)
            # v8 returns a list
            print(f"DEBUG: result type: {type(results)}")
            for r in results:
                print(f"Title: {r.get('title')}")
        except Exception as e:
            print(f"Text error: {e}")

        print("\n--- Testing .text() with region and safesearch off ---")
        try:
            results = ddgs.text(keywords=query, region='wt-wt', safesearch='off', max_results=5)
            for r in results:
                print(f"Title: {r.get('title')}")
        except Exception as e:
            print(f"Text error with params: {e}")

        print("\n--- Testing .news() ---")
        try:
            results = ddgs.news(keywords=query, max_results=5)
            for r in results:
                print(f"Title: {r.get('title')}")
        except Exception as e:
            print(f"News error: {e}")

if __name__ == "__main__":
    test_search_v8("President of India")
