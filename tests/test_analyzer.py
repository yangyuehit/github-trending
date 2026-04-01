from unittest.mock import MagicMock

from analyzer import build_prompt, analyze_project, analyze


def _make_project(**kwargs):
    base = {
        'name': 'owner/repo',
        'description': 'A test project',
        'language': 'Python',
        'stars_total': 1000,
        'stars_today': '100',
        'url': 'https://github.com/owner/repo',
        'readme': 'This is the README content.',
    }
    return {**base, **kwargs}


def test_build_prompt_contains_project_info():
    project = _make_project()
    prompt = build_prompt(project)
    assert 'owner/repo' in prompt
    assert 'A test project' in prompt
    assert 'Python' in prompt
    assert '1000' in prompt
    assert '100' in prompt
    assert 'This is the README content.' in prompt


def test_build_prompt_handles_missing_readme():
    project = _make_project(readme='')
    prompt = build_prompt(project)
    assert '无 README' in prompt


def test_analyze_project_adds_analysis_field():
    project = _make_project()
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [
        MagicMock(text='**一句话简介**\n解决测试问题')
    ]
    result = analyze_project(project, mock_client)
    assert result['analysis'] == '**一句话简介**\n解决测试问题'
    assert result['name'] == 'owner/repo'  # 原始字段保留


def test_analyze_project_preserves_original_fields():
    project = _make_project(stars_total=999)
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [MagicMock(text='analysis')]
    result = analyze_project(project, mock_client)
    assert result['stars_total'] == 999


def test_analyze_project_handles_api_failure():
    project = _make_project()
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception('API error')
    result = analyze_project(project, mock_client)
    assert result['analysis'] == '> 分析生成失败'


def test_analyze_processes_all_projects():
    projects = [_make_project(name=f'owner/repo{i}') for i in range(3)]
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [MagicMock(text='ok')]

    import analyzer
    import unittest.mock as mock
    with mock.patch('analyzer.time.sleep'):  # 跳过等待
        with mock.patch('analyzer.anthropic.Anthropic', return_value=mock_client):
            result = analyze(projects, 'fake-key')

    assert len(result) == 3
    assert all('analysis' in p for p in result)