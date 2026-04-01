import os
import tempfile

from writer import format_stars, render_note, write


def _make_project(**kwargs):
    base = {
        'name': 'owner/repo',
        'url': 'https://github.com/owner/repo',
        'language': 'Python',
        'stars_total': 1000,
        'stars_today': '100',
        'analysis': '**一句话简介**\n解决测试问题\n\n**功能拆解**\n- 功能1',
    }
    return {**base, **kwargs}


def test_format_stars_thousands():
    assert format_stars(45678) == '45.7k'


def test_format_stars_small():
    assert format_stars(999) == '999'


def test_format_stars_zero():
    assert format_stars(0) == '0'


def test_render_note_has_frontmatter():
    note = render_note([_make_project()], '2026-04-01')
    assert 'date: 2026-04-01' in note
    assert 'tags: [github-trending, 产品参考]' in note


def test_render_note_has_project_header():
    note = render_note([_make_project()], '2026-04-01')
    assert '## 1. owner/repo' in note
    assert '⭐' in note
    assert '1.0k' in note  # format_stars(1000)
    assert 'Python' in note


def test_render_note_embeds_analysis():
    note = render_note([_make_project()], '2026-04-01')
    assert '**一句话简介**' in note
    assert '解决测试问题' in note


def test_render_note_has_github_link():
    note = render_note([_make_project()], '2026-04-01')
    assert '🔗 https://github.com/owner/repo' in note


def test_render_note_numbers_projects_correctly():
    projects = [_make_project(name=f'owner/repo{i}', url=f'https://github.com/owner/repo{i}')
                for i in range(3)]
    note = render_note(projects, '2026-04-01')
    assert '## 1. owner/repo0' in note
    assert '## 2. owner/repo1' in note
    assert '## 3. owner/repo2' in note


def test_write_creates_file_and_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write([_make_project()], '2026-04-01', tmpdir)
        assert os.path.exists(path)
        assert path.endswith('2026-04-01.md')
        content = open(path, encoding='utf-8').read()
        assert 'owner/repo' in content


def test_write_creates_nested_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write([_make_project()], '2026-04-01', tmpdir)
        expected_dir = os.path.join(tmpdir, '调研报告', 'GitHub日报')
        assert os.path.isdir(expected_dir)