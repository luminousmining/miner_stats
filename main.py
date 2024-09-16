import requests
import random
import logging
import datetime


def random_header() -> dict:
    ip_generated = f'{random.randint(100, 200)}' \
                   f'.{random.randint(100, 200)}' \
                   f'.{random.randint(100, 200)}' \
                   f'.{random.randint(100, 200)}'
    return {'X-Forwarded-For': ip_generated, 'True-Client-IP': ip_generated, 'X-Real-IP': ip_generated}


class MinerSoftware:

    def __init__(self, name: str, url: str):
        self.__name = name
        self.__url = url

    def run(self) -> bool:
        logging.info(f'URL: {self.__url}')
        r = requests.get(url=self.__url, headers=random_header())
        if r.status_code != 200:
            return False
        if not r.text:
            logging.error(f'{self.__url} have not response TEXT.')
            return False

        for release in r.json():
            for asset in release['assets']:
                name = asset['name']
                download_count = asset['download_count']
                logging.info(f'{name}: {download_count}')

        return True


def initialize_logger():
    log_level = logging.INFO
    logging.basicConfig(
        format='%(levelname)s[%(asctime)s]: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=log_level)


if __name__ == '__main__':
    initialize_logger()

    miners = [
        MinerSoftware('luminousminer', 'https://api.github.com/repos/luminousmining/miner/releases'),
        MinerSoftware('riggel', 'https://api.github.com/repos/rigelminer/rigel/releases'),
        MinerSoftware('teamredminer', 'https://api.github.com/repos/todxx/teamredminer/releases'),
        MinerSoftware('srbminer', 'https://api.github.com/repos/doktor83/SRBMiner-Multi/releases'),
        MinerSoftware('lolminer', 'https://api.github.com/repos/Lolliedieb/lolMiner-releases/releases'),
        MinerSoftware('bzminer', 'https://api.github.com/repos/bzminer/bzminer/releases'),
        MinerSoftware('gminer', 'https://api.github.com/repos/develsoftware/GMinerRelease/releases'),
        MinerSoftware('teamblackminer', 'https://api.github.com/repos/sp-hash/TeamBlackMiner/releases'),
    ]

    for miner in miners:
        miner.run()
