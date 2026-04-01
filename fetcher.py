import base64
import requests
from bs4 import BeautifulSoup


def parse_trending_html(html: str) -> list[dict]:
    """从 GitHub Trending 页面 HTML 中提取项目基础信息。"""
    soup = BeautifulSoup(html, 'html.parser')
    projects = []
    for article in soup.select('article.Box-row'):
        link = article.select_one('h2 a')
        if not link:
            continue
        name = link['href'].strip('/')
        stars_today = ''
        for span in article.find_all('span'):
            text = span.get_text(strip=True)
            if 'stars today' in text:
                stars_today = text.replace('stars today', '').strip()
                break
        projects.append({
            'name': name,
            'url': f'https://github.com/{name}',
            'stars_today': stars_today,
        })
    return projects


def fetch_repo_info(name: str, headers: dict) -> dict:
    """通过 GitHub API 获取仓库描述、语言和 star 数。"""
    url = f'https://api.github.com/repos/{name}'
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        'description': data.get('description') or '',
        'language': data.get('language') or '',
        'stars_total': data.get('stargazers_count', 0),
    }


def fetch_readme(name: str, headers: dict) -> str:
    """获取仓库 README 内容，截断至前 2000 字，404 时返回空字符串。"""
    url = f'https://api.github.com/repos/{name}/readme'
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 404:
        return ''
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data['content'].replace('\n', '')).decode('utf-8', errors='replace')
    return content[:2000]


def fetch_trending(token: str | None = None) -> list[dict]:
    """抓取 GitHub Trending Top 10 项目，合并 API 数据后返回。"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    if token:
        headers['Authorization'] = f'token {token}'

    resp = requests.get('https://github.com/trending', headers=headers, timeout=15)
    resp.raise_for_status()
    projects = parse_trending_html(resp.text)[:10]

    result = []
    for p in projects:
        try:
            info = fetch_repo_info(p['name'], headers)
            readme = fetch_readme(p['name'], headers)
            result.append({**p, **info, 'readme': readme})
        except Exception as e:
            print(f"Warning: failed to fetch info for {p['name']}: {e}")
            result.append({**p, 'description': '', 'language': '', 'stars_total': 0, 'readme': ''})
    return result