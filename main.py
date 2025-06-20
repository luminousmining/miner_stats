import os
import requests
import random
import logging
import datetime
from typing import List, Optional

MAX_OLD_VERSIONS = 10
GITHUB_BASE_URL = 'https://github.com/'
GITHUB_API_BASE_URL = 'https://api.github.com/repos/'

g_access_token = None


def random_header() -> dict:
    ip_generated = f'{random.randint(100, 200)}'  \
                   f'.{random.randint(100, 200)}' \
                   f'.{random.randint(100, 200)}' \
                   f'.{random.randint(100, 200)}'
    return {
        'X-Forwarded-For': ip_generated,
        'True-Client-IP': ip_generated,
        'X-Real-IP': ip_generated
    }


class MinerSoftware:

    def __init__(self, name: str, repository: str):
        self.__repository = repository
        self.name = name
        self.base_api = f'{GITHUB_API_BASE_URL }{self.__repository}'
        self.base_repo = f'{GITHUB_BASE_URL}{self.__repository}'
        self.download_count_last = 0
        self.description = ''
        self.forks = 0
        self.stars = 0

        self.set_info()

    def __call(self, url: str) -> Optional[dict]:
        global g_access_token

        logging.debug(f'API: {url}')
        headers = random_header()
        if g_access_token:
            headers['Authorization'] = f'Bearer {g_access_token}'
            headers['Accept'] = 'application/vnd.github.v3+json'
        r = requests.get(url=url, headers=headers)
        if r.status_code != 200:
            logging.error(f'{self.__repository} status code [{r.status_code}] [{r.text}].')
            return {}
        if not r.text:
            logging.error(f'{self.__repository} have not response TEXT.')
            return {}

        return r.json()

    def get_latest(self):
        url = f'{self.base_api}/releases/latest'
        release = self.__call(url)
        if release == {}:
            return '', 0

        download_count = 0
        for asset in release['assets']:
            download_count += asset['download_count']
        tag_name = release['tag_name'].replace('v', '')
        created_at = release['created_at']

        logging.info(f'[latest]{self.name} v{tag_name}: {download_count}')
        self.download_count_last = download_count

        return tag_name, download_count, created_at

    def get_old_version(self, max_count: int) -> list:
        url = f'{self.base_api}/releases?per_page={max_count + 1}'
        releases = self.__call(url)
        if len(releases) <= 1:
            return []

        versions = list()
        for release in releases[1:len(releases)]:
            count = 0
            tag_name = release['tag_name']
            created_at = release['created_at']
            assets = release['assets']
            for asset in assets:
                count += asset['download_count']
            versions.append((tag_name, count, created_at))
            logging.info(f'[old]{self.name} v{tag_name}: {count}')

        return versions

    def set_info(self):
        url = f'{self.base_api}'
        body = self.__call(url)

        self.description = body['description']
        self.forks = body['forks_count']
        self.stars = body['stargazers_count']

        if not self.description:
            self.description = ' '


def initialize_logger():
    log_level = logging.DEBUG
    logging.basicConfig(
        format='%(levelname)s[%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=log_level)


def build_header(current_date: datetime.date) -> str:
    output = '# Miner Stats\n'
    output += '\n'
    output += f'Updated: {current_date}\n'
    output += '\n'

    return output


def build_links(miners: List[MinerSoftware]) -> str:
    output = '## Miners\n'
    output += '\n'
    output += '| Miner | link | description |stars | forks |\n'
    output += '|:-----:|:----:|:-----------:|:----:|:-----:|\n'

    for miner in miners:
        output += f'|{miner.name}|{miner.base_repo}|{miner.description}|{miner.stars}|{miner.forks}|\n'

    output += '\n'

    return output


def build_latest(miners: List[MinerSoftware]) -> str:
    miner_info = []
    for miner in miners:
        tag_name, download_count, created_at = miner.get_latest()
        if tag_name and created_at:
            miner_info.append((miner.name, tag_name, download_count, created_at))

    miner_info.sort(key=lambda x: x[3], reverse=True)

    output = '## Latest Version\n\n'
    output += '| Miner | Version | Download | Release Date |\n'
    output += '|:-----:|:-------:|:--------:|:------------:|\n'
    for name, tag_name, download_count, created_at in miner_info:
        output += f'| {name} | {tag_name} | {download_count} | {created_at} |\n'

    return output


def build_old_version(miners: List[MinerSoftware], last_count: int) -> str:
    output = '\n'
    output += f'## Old version'
    output += '\n'
    for miner in miners:
        output += '| Miner | Version | Download | Release Date |\n'
        output += '|:-----:|:-------:|:--------:|:------------:|\n'
        versions = miner.get_old_version(last_count)
        for version in versions:
            output += f'| {miner.name} | {version[0]} | {version[1]} | {version[2]} |\n'
        output += '\n'

    return output


def run():
    global g_access_token

    initialize_logger()
    g_access_token = os.getenv("GITHUB_TOKEN")

    miners = [
        MinerSoftware('xmrig', 'xmrig/xmrig'),
        MinerSoftware('gminer', 'develsoftware/GMinerRelease'),
        MinerSoftware('lolminer', 'Lolliedieb/lolMiner-releases'),
        MinerSoftware('teamredminer', 'todxx/teamredminer'),
        MinerSoftware('riggel', 'rigelminer/rigel'),
        MinerSoftware('srbminer', 'doktor83/SRBMiner-Multi'),
        MinerSoftware('teamblackminer', 'sp-hash/TeamBlackMiner'),
        MinerSoftware('bzminer', 'bzminer/bzminer'),
        MinerSoftware('miniz', 'miniZ-miner/miniZ'),
        MinerSoftware('nanominer', 'nanopool/nanominer'),
        MinerSoftware('nbminer', 'NebuTech/NBMiner'),
        MinerSoftware('onezerominer', 'OneZeroMiner/onezerominer'),
        MinerSoftware('ttminer', 'TrailingStop/TT-Miner-release'),
        MinerSoftware('wildrigmulti', 'andru-kun/wildrig-multi'),
        MinerSoftware('luminousminer', 'luminousmining/miner')
    ]

    current_date = datetime.date.today()

    readme = build_header(current_date)
    readme += build_links(miners)
    readme += build_latest(miners)
    readme += build_old_version(miners, MAX_OLD_VERSIONS)
    with open('README.md', 'w') as fd:
        fd.write(readme)


if __name__ == '__main__':
    run()

