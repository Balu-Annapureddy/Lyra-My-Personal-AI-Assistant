# web_search.py - DuckDuckGo HTML fallback then try summarizing using LLM
import requests
from bs4 import BeautifulSoup
from config import SEARCH_TIMEOUT, USER_AGENT
from llm_adapter import chat

HEADERS = {"User-Agent": USER_AGENT}

def search_web_fallback(query: str) -> str:
    """
    Try DuckDuckGo page scrape and summarize the first result with the local LLM.
    If LLM is offline, return top links.
    """
    try:
        url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=SEARCH_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.select("a.result__a")[:3]:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            results.append({"title": title, "url": href})
        if not results:
            return "I couldn't find anything relevant online."

        # Try fetch first url text and summarize
        first_url = results[0]["url"]
        page_text = _fetch_text(first_url)
        if len(page_text) > 200:
            summary = chat(f"Summarize the key points of this page for a user question '{query}':\n\n{page_text[:4000]}")
            if summary and not summary.startswith("(LLM offline/error)"):
                return summary

        # fallback: return links
        out = [f"Top results for '{query}':"]
        for r_ in results:
            out.append(f"- {r_['title']}: {r_['url']}")
        return "\n".join(out)
    except Exception as e:
        return f"Search error: {e}"

def _fetch_text(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=SEARCH_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","noscript"]):
            tag.extract()
        text = " ".join(soup.get_text(separator=" ").split())
        return text
    except Exception:
        return ""
