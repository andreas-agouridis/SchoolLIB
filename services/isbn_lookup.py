import queue
import re
import threading
import time

import requests

TIMEOUT = 5
CALL_TIMEOUT = 15
HEADERS = {
    "User-Agent": "SchoolLIB/2.0 (school library app; +https://schoollib.ct.ws) requests/2"
}

_CACHE = {}


def clean_isbn(value):
    return (value or "").strip().replace("-", "").replace(" ", "")


def _extract_year(value):
    m = re.search(r"\d{4}", str(value or ""))
    return m.group() if m else ""


def _get(url, params=None, sleep=0.5, retries=1):
    last = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
            if resp.status_code == 429:
                last = requests.exceptions.HTTPError(f"429 Too Many Requests ({url})")
                time.sleep(sleep * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            last = requests.exceptions.Timeout(f"Χρονικό όριο (timeout) για το {url}")
            time.sleep(0.3)
        except requests.exceptions.ConnectionError as e:
            last = e
            time.sleep(0.3)
        except requests.exceptions.HTTPError:
            raise
    if isinstance(last, Exception):
        raise last
    return None


def lookup_openlibrary(isbn):
    url = "https://openlibrary.org/api/books"
    resp = _get(url, params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}, retries=1)
    data = resp.json()
    info = data.get(f"ISBN:{isbn}")
    if not info:
        return None
    authors = [a.get("name", "") for a in info.get("authors", [])]
    publishers = [p.get("name", "") for p in info.get("publishers", [])]
    return {
        "title": info.get("title", ""),
        "author": ", ".join(authors),
        "publisher": ", ".join(publishers),
        "year": _extract_year(info.get("publish_date", "")),
        "pages": info.get("number_of_pages"),
        "isbn": isbn,
    }


def lookup_google(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    resp = _get(url, params={"q": f"isbn:{isbn}"}, retries=2, sleep=1.0)
    data = resp.json()
    items = data.get("items") or []
    if not items:
        return None
    vol = items[0].get("volumeInfo", {})
    authors = vol.get("authors") or []
    return {
        "title": vol.get("title", ""),
        "author": ", ".join(authors),
        "publisher": vol.get("publisher", ""),
        "year": _extract_year(vol.get("publishedDate", "")),
        "pages": vol.get("pageCount"),
        "isbn": isbn,
    }


def lookup_isbn(isbn):
    isbn = clean_isbn(isbn)
    if len(isbn) < 10:
        return None
    if isbn in _CACHE:
        return _CACHE[isbn]
    sources = [lookup_openlibrary, lookup_google]
    last_err = None
    for batch in range(2):
        result = _lookup_batch(isbn, sources)
        if isinstance(result, dict):
            result["isbn"] = isbn
            _CACHE[isbn] = result
            return result
        if result is not None:
            last_err = result
        if batch == 0:
            time.sleep(1.5)
    _CACHE[isbn] = None
    if last_err:
        raise last_err
    return None


def _lookup_batch(isbn, sources):
    results = queue.Queue()
    last_err = None

    def worker(fn):
        try:
            results.put(("ok", fn(isbn)))
        except Exception as e:
            results.put(("err", e))

    threads = []
    for fn in sources:
        t = threading.Thread(target=worker, args=(fn,), daemon=True)
        t.start()
        threads.append(t)

    deadline = time.time() + CALL_TIMEOUT
    remaining_threads = list(threads)
    while remaining_threads and time.time() < deadline:
        try:
            status, payload = results.get(timeout=max(0.1, deadline - time.time()))
        except queue.Empty:
            break
        if status == "ok":
            if payload:
                return payload
        else:
            last_err = payload
        remaining_threads = [t for t in remaining_threads if t.is_alive()]
    if last_err:
        return last_err
    return None