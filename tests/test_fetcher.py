from fetcher import parse_trending_html


def test_parse_single_project():
    html = """
    <article class="Box-row">
      <h2 class="h3 lh-condensed">
        <a href="/owner/myrepo">owner / myrepo</a>
      </h2>
      <span>1,234 stars today</span>
    </article>
    """
    result = parse_trending_html(html)
    assert len(result) == 1
    assert result[0]['name'] == 'owner/myrepo'
    assert result[0]['url'] == 'https://github.com/owner/myrepo'
    assert result[0]['stars_today'] == '1,234'


def test_parse_skips_article_without_link():
    html = '<article class="Box-row"><p>No link here</p></article>'
    result = parse_trending_html(html)
    assert result == []


def test_parse_stars_today_defaults_to_empty():
    html = """
    <article class="Box-row">
      <h2 class="h3 lh-condensed">
        <a href="/owner/repo">owner/repo</a>
      </h2>
    </article>
    """
    result = parse_trending_html(html)
    assert result[0]['stars_today'] == ''


def test_parse_multiple_projects():
    html = """
    <article class="Box-row">
      <h2><a href="/a/one">a/one</a></h2>
      <span>100 stars today</span>
    </article>
    <article class="Box-row">
      <h2><a href="/b/two">b/two</a></h2>
      <span>200 stars today</span>
    </article>
    """
    result = parse_trending_html(html)
    assert len(result) == 2
    assert result[0]['name'] == 'a/one'
    assert result[1]['name'] == 'b/two'


import base64
import textwrap
from unittest.mock import patch, MagicMock

from fetcher import fetch_repo_info, fetch_readme, fetch_trending


def test_fetch_repo_info_returns_fields():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'description': 'A cool project',
        'language': 'Python',
        'stargazers_count': 5000,
    }
    with patch('fetcher.requests.get', return_value=mock_resp):
        result = fetch_repo_info('owner/repo', {})
    assert result == {
        'description': 'A cool project',
        'language': 'Python',
        'stars_total': 5000,
    }


def test_fetch_repo_info_handles_null_fields():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'description': None,
        'language': None,
        'stargazers_count': 0,
    }
    with patch('fetcher.requests.get', return_value=mock_resp):
        result = fetch_repo_info('owner/repo', {})
    assert result['description'] == ''
    assert result['language'] == ''


def test_fetch_readme_returns_decoded_content():
    content_str = 'Hello README ' * 200  # 2600 chars, exceeds 2000
    encoded = base64.b64encode(content_str.encode()).decode()
    encoded_with_newlines = '\n'.join(textwrap.wrap(encoded, 76)) + '\n'

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'content': encoded_with_newlines}
    with patch('fetcher.requests.get', return_value=mock_resp):
        result = fetch_readme('owner/repo', {})
    assert result == content_str[:2000]
    assert len(result) == 2000


def test_fetch_readme_returns_empty_on_404():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch('fetcher.requests.get', return_value=mock_resp):
        result = fetch_readme('owner/repo', {})
    assert result == ''


def test_fetch_trending_merges_data():
    with patch('fetcher.requests.get') as mock_get, \
         patch('fetcher.parse_trending_html') as mock_parse, \
         patch('fetcher.fetch_repo_info') as mock_info, \
         patch('fetcher.fetch_readme') as mock_readme:

        trending_resp = MagicMock()
        trending_resp.text = '<html></html>'
        mock_get.return_value = trending_resp
        mock_parse.return_value = [
            {'name': 'owner/repo', 'url': 'https://github.com/owner/repo', 'stars_today': '500'}
        ]
        mock_info.return_value = {'description': 'desc', 'language': 'Python', 'stars_total': 1000}
        mock_readme.return_value = 'readme content'

        result = fetch_trending()

    assert len(result) == 1
    assert result[0]['name'] == 'owner/repo'
    assert result[0]['description'] == 'desc'
    assert result[0]['stars_total'] == 1000
    assert result[0]['readme'] == 'readme content'