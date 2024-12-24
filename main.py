import os
import requests
import random
import logging
import datetime


g_access_token = None


def random_header() -> dict:
    ip_generated = f'{random.randint(100, 200)}' \
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
        self.base_url = f'https://api.github.com/repos/{self.__repository}'
        self.download_count_last = 0

    def __call(self, url: str) -> dict:
        logging.info(f'API: {url}')
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
        url = f'{self.base_url}/releases/latest'
        release = self.__call(url)
        if release == {}:
            return '', 0

        download_count = 0
        for asset in release['assets']:
            download_count += asset['download_count']
        tag_name = release['tag_name'].replace('v', '')

        logging.info(f'{self.name} v{tag_name}: {download_count}')
        self.download_count_last = download_count

        return tag_name, download_count

    def get_old_version(self, max_count: int) -> list:
        url = f'{self.base_url}/releases?per_page={max_count + 1}'
        releases = self.__call(url)
        if len(releases) <= 1:
            return []

        versions = list()
        for release in releases[1:len(releases)]:
            count = 0
            tag_name = release['tag_name']
            assets = release['assets']
            for asset in assets:
                count += asset['download_count']
            versions.append((tag_name, count))

        return versions


def initialize_logger():
    log_level = logging.INFO
    logging.basicConfig(
        format='%(levelname)s[%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=log_level)


def build_header() -> str:
    output = '# Miner Stats\n'
    output += '\n'
    output += f'Updated: {current_date}\n'
    output += '\n'

    return output


def build_latest() -> str:
    output = '## Latest Version'
    output += '\n'
    output += '| Miner | Version | Download |\n'
    output += '|:-----:|:-------:|:--------:|\n'
    for miner in miners:
        tag_name, download_count = miner.get_latest()
        if tag_name == '' or download_count == 0:
            continue
        output += f'| {miner.name} | {tag_name} | {download_count} |\n'
    return output


def build_old_version(last_count: int) -> str:
    output = '\n'
    output += f'## Old version'
    output += '\n'
    for miner in miners:
        output += '| Miner | Version | Download |\n'
        output += '|:-----:|:-------:|:--------:|\n'
        versions = miner.get_old_version(last_count)
        for version in versions:
            output += f'| {miner.name} | {version[0]} | {version[1]} |\n'
        output += '\n'

    return output


if __name__ == '__main__':
    initialize_logger()

    g_access_token = os.getenv("GITHUB_TOKEN")

    miners = [
        MinerSoftware('gminer', 'develsoftware/GMinerRelease'),
        MinerSoftware('lolminer', 'Lolliedieb/lolMiner-releases'),
        MinerSoftware('teamredminer', 'todxx/teamredminer'),
        MinerSoftware('riggel', 'rigelminer/rigel'),
        MinerSoftware('srbminer', 'doktor83/SRBMiner-Multi'),
        MinerSoftware('teamblackminer', 'sp-hash/TeamBlackMiner'),
        MinerSoftware('bzminer', 'bzminer/bzminer'),
        MinerSoftware('luminousminer', 'luminousmining/miner'),
    ]

    current_date = datetime.date.today()

    readme = build_header()
    readme += build_latest()
    readme += build_old_version(10)

    print(readme)
