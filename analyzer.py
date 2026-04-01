import time
import anthropic


def build_prompt(project: dict) -> str:
    """构建发送给 Claude 的产品分析 prompt。"""
    readme = project.get('readme') or ''
    readme_section = readme[:2000] if readme else '（无 README）'
    return f"""你是一位产品经理，请基于以下 GitHub 项目信息，生成一份产品分析简报。

项目：{project['name']}
描述：{project.get('description') or '（无描述）'}
语言：{project.get('language') or '未知'} | Stars：{project.get('stars_total', 0)} | 今日新增：{project.get('stars_today', '')}
README 摘要：
{readme_section}

请输出以下四部分（Markdown 格式，中文）：
**一句话简介**（20字以内，说明它解决什么问题）
**功能拆解**（3-5个要点）
**商业模式**（目标用户、盈利方式、竞品对比）
**技术架构**（技术栈、架构亮点、对产品设计的借鉴价值）"""


def analyze_project(project: dict, client: anthropic.Anthropic) -> dict:
    """调用 Claude API 分析单个项目，失败时返回错误占位文本。"""
    try:
        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': build_prompt(project)}],
        )
        analysis = msg.content[0].text
    except Exception as e:
        print(f"Warning: analysis failed for {project['name']}: {e}")
        analysis = '> 分析生成失败'
    return {**project, 'analysis': analysis}


def analyze(projects: list[dict], api_key: str) -> list[dict]:
    """串行分析所有项目，每次调用间隔 1 秒。"""
    client = anthropic.Anthropic(api_key=api_key)
    result = []
    for i, project in enumerate(projects, 1):
        print(f"  [{i}/{len(projects)}] {project['name']}...")
        result.append(analyze_project(project, client))
        if i < len(projects):
            time.sleep(1)
    return result