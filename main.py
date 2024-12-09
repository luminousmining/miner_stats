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
        self.name = name
        self.__repository = repository

    def __call(self, url: str) -> dict:
        logging.debug(f'API: {url}')
        headers = random_header()
        if g_access_token:
            headers['Authorization'] = g_access_token
        r = requests.get(url=url, headers=headers)
        if r.status_code != 200:
            logging.error(f'{self.__repository} status code [{r.status_code}].')
            return {}
        if not r.text:
            logging.error(f'{self.__repository} have not response TEXT.')
            return {}

        return r.json()

    def run(self):
        base_url = f'https://api.github.com/repos/{self.__repository}'

        url = f'{base_url}/releases/latest'
        release = self.__call(url)
        if release == {}:
            return '', 0

        download_count = 0
        for asset in release['assets']:
            download_count += asset['download_count']
        tag_name = release['tag_name'].replace('v', '')

        logging.info(f'{self.name} v{tag_name}: {download_count}')

        return tag_name, download_count


def initialize_logger():
    log_level = logging.INFO
    logging.basicConfig(
        format='%(levelname)s[%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=log_level)


if __name__ == '__main__':
    initialize_logger()

    g_access_token = os.getenv("GITHUB_TOKEN")

    miners = [
        MinerSoftware('luminousminer', 'luminousmining/miner'),
        MinerSoftware('riggel', 'rigelminer/rigel'),
        MinerSoftware('teamredminer', 'todxx/teamredminer'),
        MinerSoftware('srbminer', 'doktor83/SRBMiner-Multi'),
        MinerSoftware('lolminer', 'Lolliedieb/lolMiner-releases'),
        MinerSoftware('bzminer', 'bzminer/bzminer'),
        MinerSoftware('gminer', 'develsoftware/GMinerRelease'),
        MinerSoftware('teamblackminer', 'sp-hash/TeamBlackMiner'),
    ]

    current_date = datetime.date.today()

    output = '# Miner Stats\n'
    output += '\n'
    output += f'Updated: {current_date}\n'
    output += '\n'
    output += '| Miner | Version | Download |\n'
    output += '|:-----:|:-------:|:--------:|\n'

    for miner in miners:
        tag_name, download_count = miner.run()
        if tag_name == '' or download_count == 0:
            continue
        output += f'| {miner.name} | {tag_name} | {download_count} |\n'

    logging.info(output)
