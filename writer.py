import os


def format_stars(n: int) -> str:
    """将 star 数格式化为易读字符串，如 45678 -> '45.7k'。"""
    if n >= 1000:
        return f'{n / 1000:.1f}k'
    return str(n)


def render_note(projects: list[dict], date: str) -> str:
    """将项目列表渲染为 Obsidian Markdown 日报字符串。"""
    lines = [
        '---',
        f'date: {date}',
        'tags: [github-trending, 产品参考]',
        '---',
        '',
        f'# GitHub Trending 日报 · {date}',
        '',
        '> 自动生成 · Top 10 热门项目 · 数据来源 github.com/trending',
        '',
    ]
    for i, p in enumerate(projects, 1):
        stars_display = format_stars(p.get('stars_total', 0))
        language = p.get('language') or '未知'
        stars_today = p.get('stars_today', '')
        lines += [
            f"## {i}. {p['name']}",
            f'⭐ 今日新增 {stars_today} stars · 总计 {stars_display} · 语言: {language}',
            '',
            p.get('analysis', ''),
            '',
            f"🔗 {p['url']}",
            '',
            '---',
            '',
        ]
    return '\n'.join(lines)


def write(projects: list[dict], date: str, vault_path: str) -> str:
    """渲染日报并写入 vault，返回写入文件的绝对路径。"""
    dir_path = os.path.join(vault_path, '调研报告', 'GitHub日报')
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f'{date}.md')
    content = render_note(projects, date)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path