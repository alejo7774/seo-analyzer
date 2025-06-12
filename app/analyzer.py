# app/analyzer.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_links(soup, base_url):
    links = soup.find_all('a', href=True)
    total_links = len(links)
    broken_links = 0
    internal_links = 0
    external_links = 0

    base_domain = urlparse(base_url).netloc

    for link in links:
        href = link.get('href')
        full_url = urljoin(base_url, href)

        if not is_valid_url(full_url):
            continue

        if urlparse(full_url).netloc == base_domain:
            internal_links += 1
        else:
            external_links += 1

        try:
            response = requests.head(full_url, timeout=5)
            if response.status_code >= 400:
                broken_links += 1
        except Exception:
            broken_links += 1

    return {
        "total_links": total_links,
        "broken_links": broken_links,
        "internal_links": internal_links,
        "external_links": external_links
    }

def analyze_seo(url):
    try:
        if not is_valid_url(url):
            return {"error": "URL inválida"}

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else "Sin título"
        meta_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_tag.get("content") if meta_tag and meta_tag.get("content") else "Sin descripción"

        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]
        images = soup.find_all("img")
        images_without_alt = [img for img in images if not img.get("alt")]

        link_data = check_links(soup, url)
        keywords = get_keywords(soup)
        seo_files = check_seo_files(url)

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "h1_tags": h1_tags,
            "total_images": len(images),
            "images_without_alt": len(images_without_alt),
            **link_data,
            "keywords": keywords,
            "has_robots": seo_files["has_robots"],
            "has_sitemap": seo_files["has_sitemap"]
        }

    except Exception as e:
        return {"error": str(e)}

import re
from collections import Counter

def get_keywords(soup):
    # Extraer solo el texto visible (sin script, style, etc.)
    for script in soup(["script", "style", "noscript"]):
        script.decompose()

    text = soup.get_text(separator=' ')
    text = re.sub(r'\W+', ' ', text).lower()  # Limpiar signos y poner en minúsculas

    words = text.split()
    stopwords = set([
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", 
        "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", 
        "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando",
        "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien"
    ])

    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    top_keywords = Counter(filtered_words).most_common(10)

    return top_keywords
def check_seo_files(base_url):
    from urllib.parse import urljoin

    robots_url = urljoin(base_url, "/robots.txt")
    sitemap_url = urljoin(base_url, "/sitemap.xml")

    def url_exists(url):
        try:
            r = requests.head(url, timeout=5)
            return r.status_code == 200
        except:
            return False

    return {
        "has_robots": url_exists(robots_url),
        "has_sitemap": url_exists(sitemap_url)
    }


