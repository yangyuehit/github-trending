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