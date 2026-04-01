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