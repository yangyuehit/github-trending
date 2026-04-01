import os
import sys
from datetime import date
from dotenv import load_dotenv

load_dotenv()

import fetcher
import analyzer
import writer


def main():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY not set. Create a .env file based on .env.example')
        sys.exit(1)

    vault_path = os.getenv('OBSIDIAN_VAULT_PATH', '.')
    github_token = os.getenv('GITHUB_TOKEN')
    today = date.today().isoformat()

    print(f'[1/3] Fetching GitHub Trending (top 10)...')
    projects = fetcher.fetch_trending(token=github_token)
    print(f'      Found {len(projects)} projects')

    print(f'[2/3] Analyzing with Claude (claude-haiku-4-5-20251001)...')
    projects = analyzer.analyze(projects, api_key)

    print(f'[3/3] Writing note...')
    path = writer.write(projects, today, vault_path)
    print(f'\nDone! Note written to:\n  {path}')


if __name__ == '__main__':
    main()