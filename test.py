import json
import random


def getJson(url: str):
    '''
    JSON 구하기
    -----------
    - url: JSON 파일 주소

    - ex) getJson('./json/util.json')

    `return 파싱된 JSON 파일`
    '''
    file = open(url, 'r', encoding="utf-8")
    data: dict = json.load(file)
    return data


quest = getJson('./json/quest.json')

print(random.sample(list(quest['daily'].keys()), 2))
