from PIL import Image, ImageFont, ImageDraw
import pymysql
import os
from discord import Interaction, ui, ButtonStyle, app_commands, SelectOption
from discord.ext import tasks
import discord
import datetime
import json
import math
import asyncio
import random
from typing import Type
from enum import Enum
from dotenv import load_dotenv
import io
import re
from PIL import Image, ImageDraw, ImageFont
from itertools import chain
con = pymysql.connect(host=os.environ['host'], password=os.environ['password'],
                      user=os.environ['user'], port=int(os.environ['port']), database=os.environ['database'], charset='utf8')
load_dotenv()
MAX_REBIRTH = 10
MAX_LEVEL = 150
STAT_PER_REBIRTH = 50
STAT_PER_LEVEL = 2
KST = datetime.timezone(datetime.timedelta(hours=9))


class reinEnum(Enum):
    '''
    강화 part 열거형
    ---------------
    `무기 : 0`
    `투구 : 1`
    `갑옷 : 2`
    `장갑 : 3`
    `신발 : 4`
    `망토 : 5`
    `목걸이 : 6`
    `반지 : 7`
    `귀걸이 : 8`
    '''
    무기 = 0
    투구 = 1
    갑옷 = 2
    장갑 = 3
    신발 = 4
    망토 = 5
    목걸이 = 6
    반지 = 7
    귀걸이 = 8


class questTypeEnum(Enum):
    일반 = 'normal'
    일일 = 'daily'
    주간 = 'weekly'


class miningEnum(Enum):
    '''
    광산 열거형
    ----------
    `기본광산 : 1`
    `깊은광산 : 2`
    `반짝이는광산 : 3`
    `요일광산EASY : -datetime.datetime.now(tz=KST).weekday()`
    `주간광산EASY : -8`
    `지옥광산`: -7`
    '''
    기본광산 = 1
    깊은광산 = 2
    반짝이는광산 = 3
    붉은광산 = 4
    녹아내리는광산 = 5
    용암광산 = 6
    요일광산EASY = -datetime.datetime.now(tz=KST).weekday()
    주간광산EASY = -8
    지옥광산 = -7


class statEnum(Enum):
    힘 = 'power'
    중량 = 'str'
    체력 = 'hp'
    방어력 = 'def'
    마나 = 'mana'
    크리티컬데미지 = 'crit_damage'


def makeDictionary(keys: list, values: tuple):
    '''
    keys : values 딕셔너리 만들기
    ----------------------------
    `return {} : not keys or not values`
    `return {keys:values} dict`
    '''
    if not values or not keys:
        return {}
    return {keys[i]: values[i] for i in range(len(keys))}


def getOption(option: str):
    '''
    무기 옵션 구하기
    ---------------
    - option: user_weapon의 option값
    - ex) "a12 p5 c5"

    `return {'power':int,'hp':int,'str':int,'crit':int,'damage':int}`
    '''
    power = sdef = hp = str = crit = damage = 0
    if option:
        for i in option.split(" "):
            number = int(i[1:])
            if i[0] == 'p':
                power += number
            elif i[0] == 'h':
                hp += number
            elif i[0] == 'sd':
                sdef += number
            elif i[0] == 'a':
                hp += number
                str += number
                sdef += number
                power += number
            elif i[0] == "c":
                crit += number
            elif i[0] == "d":
                damage += number
    return {'power': power, 'hp': hp, 'str': str, "def": sdef, 'crit': crit, 'damage': damage/100}


def getStatus(id: int):
    '''
    유저 스텟 불러오기
    -----------------
    - id: 유저 아이디

    `return {'power': 0, 'hp': 25, "str": 0, "str_stat": 0, "power_stat": 0, "power_else": 0, "hp_stat": 0, "crit_damage_stat": 0, 'damage': 0, 'crit': 0, 'crit_damage': 0, 'maxhp': 0, 'point': 0, 'title': ''}`
    '''
    cur = con.cursor()
    # 갑옷 힘,체력,중량 불러오기
    cur.execute(
        "SELECT SUM(power),SUM(hp),SUM(str/10),SUM(def),SUM(mana) FROM user_wear WHERE id=%s AND wear = 1 ", id)
    wear_stat = makeDictionary(
        ['power', 'hp', 'str', 'def', 'mana'], cur.fetchone())
    cur.execute("SELECT `key` FROM user_wear WHERE id = %s AND wear = 1", id)
    collections = {}
    collection = {"hp": 0, "power": 0, "str": 0, "def": 0, "mana": 0,
                  "avoid": 0, "crit": 0, "crit_damage": 0, "damage": 0}
    for i in cur.fetchall():
        try:
            collections[wear[i[0]]['collection']]
        except KeyError:
            collections[wear[i[0]]['collection']] = 1
        else:
            collections[wear[i[0]]['collection']] += 1
    for item, data in collections.items():
        cur.execute(
            "SELECT SUM(hp),SUM(power),SUM(def),SUM(avoid),SUM(mana),SUM(crit),SUM(power),SUM(crit_damage/100),SUM(damage) FROM collection_effect WHERE %s >= value AND collection = %s ", (data, item))
        value = makeDictionary(['hp', 'power', 'str', 'def', 'mana',
                               'avoid', 'crit', 'crit_damage', 'damage'], cur.fetchone())
        for i, d in value.items():
            collection[i] += d

    cur.execute(
        "SELECT `key` FROM user_title WHERE id = %s AND wear = 1", id)
    title_stat = {"hp": 0, "power": 0, "str": 0, "def": 0, "mana": 0,
                  "avoid": 0, "crit": 0, "crit_damage": 0, "damage": 0}
    key = cur.fetchone()
    if key:
        wear_title: dict = title[key[0]]
        del wear_title['name']
        del wear_title['description']
        del wear_title['rank']
        del wear_title['level']
        del wear_title['trade']
        for item, data in wear_title.items():
            title_stat[item] += data
        title_stat['crit_damage'] /= 100
    cur.execute(
        "SELECT power,damage/100,`option`,mana FROM user_weapon WHERE id=%s AND wear = 1", id)
    weapon_stat = makeDictionary(
        ['power', 'damage', 'option', 'mana'], cur.fetchone())
    if weapon_stat:
        option = getOption(weapon_stat['option'])
    else:
        option = {}
    cur.execute(
        "SELECT power,hp*5,str/10,def/10,crit,crit_damage/50,mana*2,avoid,point FROM user_stat WHERE id=%s", id)
    stat = makeDictionary(['power', 'hp', 'str', 'def', 'crit',
                          'crit_damage', 'mana', 'avoid', 'point'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0, 'def': 0, 'damage': 0, 'crit': 0, 'mana': 0, 'avoid': 0,
             'crit_damage': 0, 'maxhp': 0, 'point': 0}
    for key, value in chain(wear_stat.items(), weapon_stat.items(), option.items(), stat.items(), collection.items(), title_stat.items()):
        if value:
            final[key] += value
    final['maxhp'] = final['hp']
    final['cur_power'] = final['power']
    final['def'] = float(final['def'])
    final['cur_def'] = final['def']
    if final['damage'] == 0:
        final['damage'] = 1
    final['damage'] = float(final['damage'])
    final['cur_damage'] = final['damage']
    final['cur_crit'] = final['crit']
    final['cur_avoid'] = final['avoid']
    final['cur_mana'] = final['mana']
    final['str'] = float(final['str'])
    final['crit_damage'] = float(final['crit_damage'])
    final['cur_crit_damage'] = final['crit_damage']
    cur.close()
    return final


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


def getSuccess(num, all: int):
    '''
    확률 계산기
    -----------
    - num>=1~all return True

    - else return False
    '''
    if isinstance(num, float):
        if not num.is_integer():
            power = len(str(num))-(int(math.log10(num))+2)
            num = int(num*(10**power))
            all *= (10**power)
        else:
            num = int(num)
    return num >= random.uniform(1, all)


def getRandomValue1(val_range: str):
    '''
    랜덤 숫자 추출기
    ---------------
    - ex) val_range:"0 5"

    - 0~5사이 숫자 랜덤 추출하기

    `return val_range 사이 숫자` 
    '''
    a, b = val_range.split(" ")
    return random.randint(int(a), int(b))


def getRandomValue2(val_range: str):
    '''
    랜덤 숫자 추출기
    ---------------
    - ex) val_range:"0~5"

    - 0~5사이 숫자 랜덤 추출하기

    `return val_range 사이 숫자` 
    '''
    a, b = val_range.split("~")
    return random.randint(int(a), int(b))


def translateName(name: str):
    '''
    column 명은 한글로 한글은 column 으로 변환
    ----------------------------------------
    `return power <=> 힘`
    '''
    column = ['power', 'hp', 'str', 'crit', 'crit_damage',
              'damage', 'weapon', 'wear', 'title', 'item', 'money', 'level', 'collection', 'use', 'util', 'mana', 'avoid', 'def']
    korean = ['힘', '체력', '중량', '크리티컬 확률', '크리티컬 데미지',
              '데미지', '무기', '방어구', '칭호', '기타', '골드', '레벨', '컬렉션', '소비', '기타', '마나', '회피', '방어력']
    if name in column:
        return korean[column.index(name)]
    elif name in korean:
        return column[korean.index(name)]
    else:
        return ''


def getPartRein(part: int):
    '''
    방어구 스텟 확인
    ---------------
    - 0: 무기
    - parts=["힘","체력","중량","힘","체력","중량","체력","체력","체력"]

    `return parts[part]`
    '''
    parts = ['힘', '체력', '중량', '힘', '체력', '중량', '체력', '체력', '체력']
    return parts[part]


def getInfo(id: int):
    """
    유저 정보 불러오기
    -----------------
    id: 유저 아이디

    return {nickname, exp, level, rebirth, money, mooroong, role, title}
    """
    cur = con.cursor()
    cur.execute(
        "SELECT nickname,exp,level,rebirth,money,mooroong,role FROM user_info WHERE id = %s", id)
    info = makeDictionary(
        ['nickname', 'exp', 'level', 'rebirth', 'money', 'mooroong', 'role'], cur.fetchone())
    cur.execute("SELECT `key` FROM user_title WHERE id = %s AND wear = 1", id)
    key = cur.fetchone()
    if key:
        info['title'] = title[key[0]]['name']
    else:
        info['title'] = "칭호없음"
    return info


def list_chunk(lst: list, n: int):
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def checkSuccess(probabilities: list | tuple):
    random_number = random.uniform(0, 1)
    cumulative_probability = 0

    for i, prob in enumerate(probabilities):
        cumulative_probability += prob
        if random_number <= cumulative_probability:
            return i
    return -1


level = getJson('./json/level.json')
item = getJson('./json/makeItem.json')
util = getJson('./json/util.json')
rein = getJson('./json/reinforce.json')
stone = getJson('./json/stone.json')
quest = getJson('./json/quest.json')
title = getJson("./json/title.json")
weapon = getJson("./json/weapon.json")
wear = getJson("./json/wear.json")


class MyClient(discord.Client):
    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync()
        self.boost_19.start()
        self.boost_21.start()
        self.boost_23.start()
        self.boost_24.start()
        print("로그인!")

    @tasks.loop(time=datetime.time(hour=19, minute=0, second=0, tzinfo=KST))
    async def boost_19(self):
        global EXP_EARN, MONEY_EARN
        EXP_EARN = 1
        MONEY_EARN = 2

    @tasks.loop(time=datetime.time(hour=21, minute=0, second=0, tzinfo=KST))
    async def boost_21(self):
        global EXP_EARN
        EXP_EARN = 2
        MONEY_EARN = 1

    @tasks.loop(time=datetime.time(hour=23, minute=0, second=0, tzinfo=KST))
    async def boost_23(self):
        global EXP_EARN, MONEY_EARN
        EXP_EARN = 2
        MONEY_EARN = 2

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=KST))
    async def boost_24(self):
        global EXP_EARN, MONEY_EARN
        EXP_EARN = 1
        MONEY_EARN = 1


EXP_EARN = 1
MONEY_EARN = 1
intents = discord.Intents.all()
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)


class User:
    _instances = {}

    def __new__(cls, id):
        if not id in cls._instances:
            cls._instances[id] = super().__new__(cls)
        return cls._instances[id]

    def __init__(self, id: int):
        self.id = id
        if not hasattr(self, 'stat'):
            self.stat = getStatus(id)
        if not hasattr(self, 'userInfo'):
            self.userInfo = getInfo(id)
        if not hasattr(self, 'where'):
            self.where = ""

    async def Info(self, interaction: Interaction):
        image = Image.open("image/info.png")
        name_font = ImageFont.truetype("malgunbd.ttf", 45)
        title_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(self.userInfo['title']))
        level_font = ImageFont.truetype("malgunbd.ttf", 30)

        draw = ImageDraw.Draw(image)
        draw.text(
            (250, 170), self.userInfo['nickname'], anchor="mm", font=name_font)
        draw.text((250, 110), self.userInfo['title'],
                  anchor="mm", font=title_font)
        draw.text(
            (585, 120), str(self.userInfo['level']), anchor='mm', font=level_font)
        draw.text(
            (895, 120), str(self.userInfo['rebirth']), anchor='mm', font=level_font)
        req = level[str(self.userInfo['rebirth'])][str(self.userInfo['level'])]
        per = int((self.userInfo['exp']/req)*100)
        text = f"{format(self.userInfo['exp'],',')}/{format(req,',')}({per}%)"
        exp_font = ImageFont.truetype("malgunbd.ttf", 40-len(text))
        draw.text((585, 240), text,
                  anchor='mm', font=exp_font)
        draw.rounded_rectangle((480, 260, 680, 290), fill="white",
                               outline="white")
        draw.rounded_rectangle((480, 260, 480+per*2, 290),
                               fill=(14, 209, 69, 255), outline=(14, 209, 69, 255))
        money_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(str(self.userInfo['money'])))
        draw.text(
            (895, 240), f"{format(self.userInfo['money'],',')}G", anchor="mm", font=money_font)
        power_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(str(self.stat['cur_power'])))
        draw.text((585, 355), format(
            int(self.stat['cur_power']), ','), anchor="mm", font=power_font)
        def_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(str(self.stat['cur_power'])))
        draw.text((740, 355), str(
            self.stat['cur_def']), anchor="mm", font=def_font)
        hp_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(str(self.stat['maxhp'])))
        draw.text((895, 355), format(
            self.stat['maxhp'], ','), anchor="mm", font=hp_font)
        draw.text(
            (585, 455), f"{self.stat['cur_crit']}%", anchor="mm", font=level_font)
        draw.text(
            (740, 455), f"{int(self.stat['cur_crit_damage']*100)}%", anchor="mm", font=level_font)
        draw.text(
            (895, 455), f"{int(self.stat['cur_damage']*100)}%", anchor="mm", font=level_font)
        draw.text(
            (585, 555), f"{self.stat['cur_avoid']}%", anchor="mm", font=level_font)
        draw.text(
            (740, 555), f"{self.stat['cur_mana']}", anchor="mm", font=level_font)
        draw.text(
            (895, 555), f"{self.stat['point']}", anchor="mm", font=level_font)
        user_avater = interaction.user.display_avatar.with_size(256)
        data = io.BytesIO(await user_avater.read())
        user_avater = Image.open(data)
        image.paste(im=user_avater, box=(130, 200, 130+256, 200+256))
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename="userInfo.png")

    async def getExp(self, exp: int = 0, type: str = "normal"):
        if type != "normal":
            e_e = 1
        else:
            e_e = EXP_EARN
        cur = con.cursor()
        cur.execute(
            "UPDATE user_info SET exp = exp + %s WHERE id = %s", (exp*e_e, self.id))
        cur.execute(
            "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = exp ", (exp*e_e, self.id))
        self.userInfo['exp'] += exp*e_e
        con.commit()
        cur.close()
        return await self.is_levelup()

    async def getMoney(self, money: int = 0, type: str = "normal"):
        if type != "normal":
            m_e = 1
        else:
            m_e = MONEY_EARN
        cur = con.cursor()
        if money > 0:
            cur.execute(
                "UPDATE user_info SET money = money + %s WHERE id = %s", (money*m_e, self.id))

            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = 'money'", (money*m_e, self.id))
            self.userInfo['money'] += money*m_e
        else:
            cur.execute(
                "UPDATE user_info SET money = money + %s WHERE id = %s", (money, self.id))

            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type`= 'spend' AND code = 'money'", (-money, self.id))
            self.userInfo['money'] += money
        con.commit()
        cur.close()

    async def getStone(self, code: str = '0', value: int = 0):
        cur = con.cursor()
        cur.execute(
            "UPDATE quest SET now = now + %s WHERE `type` = 'get-stone' AND code = %s AND id = %s", (value, code, self.id))
        con.commit()
        cur.close()

    async def getKill(self, name: str = None):
        cur = con.cursor()
        cur.execute(
            "UPDATE quest SET now = now + 1 WHERE id = %s AND `type` = 'kill' AND code = %s", (self.id, name))
        cur.execute(
            "UPDATE quest SET now = now + 1 WHERE id = %s AND `type` = 'kill' AND code = 'any'", (self.id))
        con.commit()
        cur.close()

    async def getItem(self, code: int, cnt: int, type="normal"):
        '''
        cnt 개 만큼 아이템 code에 담기
        ----------------------------
        - code: 아이템 코드
        - cnt: 넣을 아이템 갯수
        '''
        cur = con.cursor()
        await self.isExistItem(code)
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s AND id = %s", (cnt, code, self.id))
        if cnt > 0 and type == 'normal':
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = 'item'", (cnt, self.id))
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = %s", (cnt, self.id, code))
        con.commit()
        cur.close()

    async def setItem(self, code: int, cnt: int):
        '''
        아이템 code를 cnt값으로 바꾸기
        ----------------------------
        - code: 아이템 코드
        - id: 유저 아이디
        - cnt: 넣을 아이템 갯수
        '''
        cur = con.cursor()
        await self.isExistItem(self.id, code)
        cur.execute(
            "UPDATE user_item SET amount = %s WHERE item_id = %s AND id = %s", (cnt, code, self.id))
        con.commit()
        cur.close()

    async def statusUp(self, stat: statEnum, point: int):
        cur = con.cursor()
        if point < 0:
            return '0보다 작은 수는 쓸 수 없습니다.'
        elif self.stat['point'] >= point:
            cur.execute(
                f"UPDATE user_stat SET {stat.value}={stat.value} + %s, point = point - %s WHERE id = %s", (point, point, self.id))
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'up' AND code = 'stat' ", (point, self.id))
            con.commit()
            cur.close()
            await self.sync_stat()
            return f"성공적으로 **{stat.name}** 스텟을 **{point}** 만큼 올렸습니다."
        else:
            return f"스텟이 모자랍니다. 현재 **{point}** 포인트 보유중"

    async def getEntrance(self, floor: str):
        cur = con.cursor()
        cur.execute(
            "UPDATE quest SET now = now +1 WHERE id = %s AND code = %s AND `type` = 'entrance'", (self.id, floor))

    async def getReinforce(self):
        cur = con.cursor()
        cur.execute(
            "UPDATE quest SET now = now + 1 WHERE id = %s AND `type` = 'do' AND `code` = 'reinforce'", (self.id))
        con.commit()
        cur.close()

    async def isExistItem(self, code: int):
        '''
        user_item에 아이템 있는지 확인
        -----------------------------
        - id: 유저 아이디
        - code: 아이템 코드

        `return amount`
        '''
        cur = con.cursor()
        try:
            util[str(code)]
        except:
            return -1
        cur.execute(  # code에 해당하는 아이템이 있는지 확인
            "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (self.id, code))
        amount = cur.fetchone()
        if not amount:  # 없으면 아이템 insert
            cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s)",
                        (code, util[str(code)]['name'], 0,  self.id))
            con.commit()
            cur.close()
            return 0
        else:
            cur.close()
            return int(amount[0])

    def syncisExistItem(self, code: int):
        '''
            user_item에 아이템 있는지 확인
            -----------------------------
            - id: 유저 아이디
            - code: 아이템 코드

            `return amount`
            '''
        cur = con.cursor()
        try:
            util[str(code)]
        except:
            return -1
        cur.execute(  # code에 해당하는 아이템이 있는지 확인
            "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (self.id, code))
        amount = cur.fetchone()
        if not amount:  # 없으면 아이템 insert
            cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s)",
                        (code, util[str(code)]['name'], 0,  self.id))
            con.commit()
            cur.close()
            return 0
        else:
            cur.close()
            return int(amount[0])

    async def isExistItemName(self, name: str):
        cur = con.cursor()
        cur.execute(
            "SELECT SUM(amount) FROM user_item WHERE name = %s AND id= %s", (name, self.id))
        amount = cur.fetchone()[0]
        cur.close()
        return int(amount)

    async def is_levelup(self):
        '''
        레벨업 했을때
        ------------

        `return 레벨업한 숫자`
        '''
        if self.userInfo['rebirth'] == MAX_REBIRTH:
            return 0
        num = 0
        cur = con.cursor()
        while level[str(self.userInfo['rebirth'])][str(self.userInfo['level']+num)] <= self.userInfo['exp']:
            self.userInfo['exp'] -= level[str(
                self.userInfo['rebirth'])][str(self.userInfo['level']+num)]
            num += 1
            if self.userInfo['level']+num >= MAX_LEVEL+1 and self.userInfo['rebirth'] != MAX_REBIRTH:
                cur.execute(
                    "UPDATE user_info SET exp = %s, rebirth=rebirth+1 WHERE id = %s", (self.userInfo['exp'], self.id))
                cur.execute(
                    "UPDATE user_stat SET point = point + %s WHERE id = %s", (STAT_PER_REBIRTH, self.id))
                cur.execute(
                    "UPDATE quest SET now = now + 1 WHERE id = %s AND `type`='up' AND code = 'rebirth'", (self.id))
                self.getItem(8, 1)
                self.userInfo['rebirth'] += 1
                cur.close()
                con.commit()
                return MAX_LEVEL+1
        if num > 0:
            self.userInfo['level'] += num
            cur.execute(
                "UPDATE user_info SET level = level + %s , exp = %s WHERE id = %s", (num, self.userInfo['exp'], self.id))
            cur.execute(
                "UPDATE user_stat SET point = point + %s WHERE id = %s", (num*STAT_PER_LEVEL, self.id))
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type`='up' AND code = 'level'", (num, self.id))
            cur.execute(
                "UPDATE quest SET now = 1 WHERE id = %s AND `type`='level' AND code <= %s ", (self.id, self.userInfo['level']))

        cur.close()
        con.commit()

        return num

    async def useNotTradeFirst(self, name: str, amount: int):
        '''
        교환불가능 아이템 먼저 소비
        -------------------------
        - name: 아이템명
        - amount: 소비해야할 아이템 개수
        '''
        cur = con.cursor()
        cur.execute(
            "SELECT item_id,amount FROM user_item WHERE id = %s AND name = %s ORDER BY item_id ASC", (self.id, name))
        items = cur.fetchall()
        if len(items) == 2:
            if items[0][1]+items[1][1] < amount:
                return False
            if items[0][1] <= amount:
                cur.execute(
                    "UPDATE user_item SET amount = 0 WHERE id = %s AND item_id = %s", (self.id, items[0][0]))
                cur.execute("UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s ",
                            (amount-items[0][1], self.id, items[1][0]))
            else:
                cur.execute(
                    "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (amount, self.id, items[0][0]))
        else:
            if len(items) == 1 and items[0][0] >= amount:
                cur.execute(
                    "UPDATE user_item SET amount = amount - %s WHERE id = %s AND name = %s", (amount, self.id, name))
            else:
                return False
        con.commit()
        cur.close()
        return True

    async def sync_stat(self):
        self.stat = getStatus(self.id)

    async def getWeapon(self, data: dict):
        power = getRandomValue1(data['power'])
        mana = getRandomValue1(data['mana'])
        damage = getRandomValue1(data['damage'])
        weapon_data = weapon[data['key']]
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_weapon(`key`,`rank`,power,mana,damage,id) VALUES(%s,%s,%s,%s,%s,%s)", (data['key'], weapon_data['rank'], power, mana, damage, self.id))
        cur.execute(
            "UPDATE quest SET now = now + 1 WHERE id = %s AND `type` = 'make-weapon' AND code = %s", (self.id, weapon_data['name']))
        con.commit()
        cur.close()
        return {'power': power, 'mana': mana, 'damage': damage}

    async def getWear(self, data: dict):
        power = getRandomValue1(data['power'])
        hp = getRandomValue1(data['hp'])
        str = getRandomValue1(data['str'])
        sdef = getRandomValue1(data['def'])
        mana = getRandomValue1(data['mana'])
        wear_data = wear[data['key']]
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_wear(`key`,`rank`,power,hp,str,def,mana,part,id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['key'], wear_data['rank'], power, hp, str, sdef, mana, wear_data['part'], self.id))
        cur.execute(
            "UPDATE quest SET now = now + 1 WHERE id = %s AND `type` = 'make-wear' AND code = %s", (self.id, wear_data['name']))
        con.commit()
        cur.close()
        return {'power': power, 'hp': hp, 'str': str, 'def': sdef, 'mana': mana}


class Quest:
    def __init__(self, user: User):
        self.user = user
        self.article_font = ImageFont.truetype("malgunbd.ttf", 60)
        self.page = 0
        self.quest = []

    async def questInfo(self, type: str, code: str, amount: int):
        if type == "kill":
            text = f"{code} {amount}회 처치"
        elif type == "level":
            text = f"{code}레벨 달성하기"
        elif type == "get-stone":
            text = f"{stone[code]['name']} {amount}개 획득하기"
        elif type == "handover-util":
            text = f"{util[code]['name']} {amount}개 제출하기"
        elif type == "up":
            if code == "level":
                text = f"{amount} 레벨업 하기"
            elif code == "stat":
                text = f"스텟 {amount}개 올리기"
        elif type == "do":
            if code == "reinforce":
                text = f"강화 {amount}번 진행하기"
        elif type == "get":
            if code == "gold":
                text = f"{amount} 골드 획득하기"
            elif code == "exp":
                text = f"{amount} 경험치 획득하기"
            elif code == "util":
                text = f"기타아이템 {amount}개 획득하기"
            elif code == "use":
                text = f"소비아이템 {amount}개 획득하기"
            else:
                text = f"{util[code]['name']} {amount}개 획득하기"
        elif type == "spend":
            if code == "money":
                text = f"{amount}골드 사용하기"
        elif type == "make-wear":
            text = f"{code} {amount}회 제작하기"
        elif type == "entrance":
            text = f"{code} {amount}회 입장하기"
        return text

    async def getQuest(self, type: str):
        if self.page < 0:
            self.page = 0
        image = Image.open("image/quest.png")
        cur = con.cursor()
        cur.execute(
            "SELECT `key`,`type`,`code`,amount,now,now>=amount AS sucess FROM quest WHERE id = %s AND quest_type = %s ORDER BY sucess DESC, date LIMIT %s,3", (self.user.id, type, self.page*3))
        quests = cur.fetchall()
        cur.close()
        if not quests:
            if self.page > 0:
                self.page -= 1
                return await self.getQuest(type)
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                return discord.File(fp=image_binary, filename="normalQuest.png")
        self.quest = quests
        for idx, i in enumerate(quests):
            y_pos = [100, 370, 640]
            text = await self.questInfo(i[1], i[2], i[3])
            draw = ImageDraw.Draw(image)
            draw.text((100, y_pos[idx]), text, font=self.article_font)
            now = f"{i[4]}/{i[3]}"
            now_font = ImageFont.truetype("malgunbd.ttf", 60-len(now))
            draw.text(
                (1535, y_pos[idx]+70), "클리어!" if i[-1] else now, fill='red' if i[-1] else 'white', anchor="mm", font=now_font)
            try:
                description = quest[type][str(i[0])]['description']
            except KeyError:
                description = ""
            description_font = ImageFont.truetype("malgunbd.ttf", 40)
            draw.text((100, y_pos[idx]+70), description, font=description_font)
            page_font = ImageFont.truetype("malgunbd.ttf", 45)
            draw.text((844, 880), f"{self.page+1}페이지",
                      anchor="mm", font=page_font)
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename="normalQuest.png")

    async def makeQuest(self, type: str, key: str):
        quest_info: dict = quest[type][key]
        cur = con.cursor()
        cur.execute("DELETE FROM quest WHERE id = %s AND `key` = %s AND quest_type = %s",
                    (self.user.id, key, type))
        insert_value = list(quest_info.values())[:-2]
        insert_value.insert(0, key)
        insert_value.append(self.user.id)
        if insert_value[1] == "level" and self.user.userInfo['level'] >= int(insert_value[2]):
            insert_value.append(1)
        else:
            insert_value.append(0)
        insert_value.append(datetime.datetime.now())
        insert_value.append(type)
        cur.execute(
            "INSERT INTO quest VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ", insert_value)
        con.commit()
        cur.close()

    async def claimQuest(self):
        cur = con.cursor()
        cur.execute(
            "SELECT `key`,`type`,`code`,amount,gold,exp,util,`use`,weapon,wear,quest_type FROM quest WHERE id = %s AND now>=amount ORDER BY quest_type", self.user.id)
        cleared_quest = cur.fetchall()
        normal_text = ''
        daily_text = ''
        weekly_text = ''
        num = 0
        for i in cleared_quest:
            quest_info = quest[i[-1]][str(i[0])]
            if quest_info['next']:
                await self.makeQuest(i[-1], quest_info['next'])
            quest_name = await self.questInfo(i[1], i[2], i[3])
            await self.user.getMoney(i[4], "quest")
            num = await self.user.getExp(i[5], "quest")
            util_text = ""
            for j in quest_info['util'].split(" "):
                code, value = j.split("-")
                await self.user.getItem(code, int(value))
                util_text += f"{util[code]['name']} {value}개 "
            if i[-1] == "normal":
                normal_text += f"```{quest_name} 퀘스트 클리어!\n"
                normal_text += f"보상 : {i[4]}골드 {i[5]}경험치\n{util_text}```\n\n"
            elif i[-1] == "daily":
                daily_text += f"```{quest_name} 퀘스트 클리어!\n"
                daily_text += f"보상 : {i[4]}골드 {i[5]}경험치\n{util_text}```\n\n"
            cur.execute("DELETE FROM quest WHERE id = %s AND `key` = %s AND quest_type = %s",
                        (self.user.id, i[0], i[-1]))
        con.commit()
        cur.close()
        return normal_text, daily_text, weekly_text, num


class Reinforce:
    def __init__(self, user: User, part: reinEnum, interaction: Interaction):
        self.user = user
        self.part = part
        self.isWeapon = self.part.value == 0
        self.interaction = interaction
        self.reinItem = {}

    async def chooseItem(self):
        if self.reinItem:
            return
        cur = con.cursor()
        category = {}
        if self.isWeapon:
            cur.execute(
                "SELECT item_id,`key`,upgrade,`rank` FROM user_weapon WHERE id = %s AND wear = 1", self.user.id)
            category = weapon
        else:
            cur.execute("SELECT item_id,`key`,upgrade,`rank` FROM user_wear WHERE id = %s AND part = %s AND wear = 1 ",
                        (self.user.id, self.part.value))
            category = wear
        reinItem = cur.fetchone()
        if not reinItem:
            self.reinItem = {}
            return
        self.reinItem = makeDictionary(
            ['item_id', 'key', 'upgrade', 'rank'], reinItem)
        self.reinItem['name'] = category[self.reinItem['key']]['name']
        self.reinItem['url'] = category[self.reinItem['key']]['url']

    async def validityReinforce(self):
        await self.chooseItem()
        rank = str(self.reinItem['rank'])
        upgrade = str(self.reinItem['upgrade'])
        if self.user.userInfo['money'] < rein['money'][rank][upgrade]:
            return False, "돈이 부족합니다."
        for i in rein['item'][rank][upgrade].split(","):
            name, amount = i.split("/")
            if await self.user.isExistItemName(name) < int(amount):
                return False, "재료가 부족합니다."
        cur = con.cursor()
        if self.isWeapon:
            cur.execute("SELECT COUNT(*) FROM user_weapon WHERE id = %s AND wear = 1 AND `key` = %s AND upgrade = %s AND `rank` = %s AND item_id = %s",
                        (self.user.id, self.reinItem['key'], self.reinItem['upgrade'], self.reinItem['rank'], self.reinItem['item_id']))
        else:
            cur.execute("SELECT COUNT(*) FROM user_wear WHERE id = %s AND wear = 1 AND `key` = %s AND upgrade = %s AND `rank` = %s AND part = %s AND item_id = %s",
                        (self.user.id, self.reinItem['key'], self.reinItem['upgrade'], self.reinItem['rank'], self.part.value, self.reinItem['item_id']))
        if not cur.fetchone()[0]:
            self.reinItem = {}
            await self.chooseItem()
            return False, "해당 아이템이 존재하지 않거나 정보가 잘못되었습니다."
        return True, ""

    async def doReinforce(self):
        rank = str(self.reinItem['rank'])
        upgrade = str(self.reinItem['upgrade'])
        await self.user.getMoney(-rein['money'][rank][upgrade])
        for i in rein['item'][rank][upgrade].split(","):
            name, amount = i.split("/")
            if not await self.user.useNotTradeFirst(name, int(amount)):
                print("?")
                return False
        return True

    async def successReinforce(self):
        await self.user.getReinforce()
        rank = str(self.reinItem['rank'])
        upgrade = str(self.reinItem['upgrade'])
        if await self.doReinforce() and getSuccess(rein['percent'][upgrade], 100):
            cur = con.cursor()
            if self.isWeapon:
                cur.execute("UPDATE user_weapon SET power = power + %s, upgrade = upgrade + 1 WHERE id = %s AND item_id = %s",
                            (rein['weapon'][rank][upgrade], self.user.id, self.reinItem['item_id']))
                self.reinItem['upgrade'] += 1
            else:
                cur.execute("UPDATE user_wear SET `%s` = `%s` + %s WHERE id = %s AND item_id = %s AND part = %s", (translateName(getPartRein(self.part.value)),
                            translateName(getPartRein(self.part.value)), rein['wear'][rank][upgrade], self.user.id, self.reinItem['item_id'], self.part.value))
            await self.user.sync_stat()
            con.commit()
            cur.close()
            return True
        else:
            return False

    async def validity(self):
        if self.user.where:
            await self.interaction.response.send_message(f"현재 {self.user.where}에 있습니다.", ephemeral=True)
        else:
            await self.chooseItem()
            if not self.reinItem:
                return await self.interaction.response.send_message(f"장착중인 아이템이 없습니다.", ephemeral=True)
            self.user.where = "강화소"
            await self.interaction.response.send_message(f"강화소에 입장중..!", ephemeral=True)
            await self.setup(self.interaction)

    class setupView(ui.View):
        def __init__(self, parent: 'Reinforce'):
            super().__init__(timeout=None)
            self.parent = parent

        @ui.button(label="강화하기", emoji="🔨", style=ButtonStyle.green)
        async def reinforce(self, interaction: Interaction, button: ui.Button):
            validity, message = await self.parent.validityReinforce()
            if not validity:
                embed: discord.Embed = await self.parent.setupEmbed()
                embed.set_footer(text=message)
                await interaction.response.edit_message(embed=embed)
            else:
                if await self.parent.successReinforce():
                    color = 0x009900
                    title = "강화성공!"
                else:
                    color = 0xff0000
                    title = "강화실패..."
                embed = discord.Embed(title=title, color=color)
                await interaction.response.edit_message(embed=embed, view=None)
                await asyncio.sleep(2)
                await self.parent.setup(interaction)

        @ui.button(label="끝내기", style=ButtonStyle.red)
        async def end(self, interaction: Interaction, button: ui.Button):
            self.parent.user.where = ""
            await interaction.response.edit_message(content="강화소를 떠났습니다.", view=None, embed=None)
            await interaction.delete_original_response()

    async def setupEmbed(self):
        rank = str(self.reinItem['rank'])
        upgrade = str(self.reinItem['upgrade'])
        embed = discord.Embed(
            title=f"{self.reinItem['name']} +{self.reinItem['upgrade']} > +{self.reinItem['upgrade']+1} 강화")
        text = "```"
        text += f"{format(self.user.userInfo['money'],',')}/{format(rein['money'][rank][upgrade],',')} 골드\n"
        for i in rein['item'][rank][upgrade].split(","):
            name, amount = i.split("/")
            text += f"{name} {await self.user.isExistItemName(name)}/{amount}개\n"
        text += "```"
        embed.add_field(name="재료", value=text, inline=False)
        embed.add_field(
            name=f"성공확률 : {rein['percent'][upgrade]}%", value=f"성공시 **{getPartRein(self.part.value)} +{rein['weapon'][rank][upgrade] if self.isWeapon else rein['wear'][rank][upgrade]}**", inline=False)
        embed.set_thumbnail(url=self.reinItem['url'])
        return embed

    async def setup(self, interaction: Interaction):
        try:
            await interaction.response.edit_message(content="", embed=await self.setupEmbed(), view=self.setupView(self))
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=await self.setupEmbed(), view=self.setupView(self))


class Mining:
    ticket = {
        -0: {'code': 2, 'value': 1, 'cnt': 3},
        -1: {'code': 2, 'value': 1, 'cnt': 3},
        -2: {'code': 2, 'value': 1, 'cnt': 3},
        -3: {'code': 2, 'value': 1, 'cnt': 3},
        -4: {'code': 2, 'value': 1, 'cnt': 3},
        -5: {'code': 2, 'value': 1, 'cnt': 3},
        -6: {'code': 2, 'value': 1, 'cnt': 3},
        -8: {'code': 4, 'value': 1, 'cnt': 6},
        -7: {'code': 11, 'value': 1, 'cnt': 10}}

    def __init__(self, user: User, floor: miningEnum, interaction: Interaction):
        self.floor = floor
        self.user = user
        self.user.effect = {}
        self.interaction = interaction
        self.exp = 0
        self.inventory = {'util': {}, 'use': {}, 'stone': {}}
        self.cnt = -1

    async def validity(self):
        if self.user.where:
            await self.interaction.response.send_message(f"현재 {self.user.where}에 있어요!", ephemeral=True)
        elif await self.haveTicket():
            self.user.where = "광산"
            await self.interaction.response.send_message("광산에 진입중...!", ephemeral=True)
            await self.user.getEntrance(self.floor.name)
            await self.setup(self.interaction)
        else:
            await self.interaction.response.send_message(f"**{util[str(Mining.ticket[self.floor.value]['code'])]['name']}**이 없습니다.", ephemeral=True)

    async def haveTicket(self):
        if self.floor.value in Mining.ticket.keys():
            floor = Mining.ticket[self.floor.value]
            amount = await self.user.isExistItem(floor['code'])
            if amount >= floor['value']:
                await self.user.getItem(floor['code'], -floor['value'])
                self.cnt = floor['cnt']

                return True
            else:
                return False
        return True

    def stone_result(self):
        total_weight = 0
        for item, data in self.inventory['stone'].items():
            total_weight += data * stone[item]['weight']
        return total_weight

    class fightView(ui.View):
        def __init__(self, parent: 'Mining'):
            super().__init__(timeout=None)
            self.parent = parent

        async def classify_effect(self, effect, name):
            if name == "user":
                maxhp = self.parent.user.stat['maxhp']
                hp = self.parent.user.stat['hp']
                atk = self.parent.user.stat['power']
                sdef = self.parent.user.stat['def']
                damage = self.parent.user.stat['damage']
            else:
                maxhp = self.parent.user.stat['maxhp']
                hp = self.parent.enemy['hp']
                atk = self.parent.enemy['power']
                sdef = self.parent.enemy['def']
                damage = self.parent.enemy['damage']

            if effect == "🩸":
                dam = maxhp//20
                if name == 'user':
                    self.parent.user.stat['hp'] -= dam
                else:
                    self.parent.enemy['hp'] -= dam
                return 'dam', -dam

            if effect == "🗡":
                damage = 0.25
                if name == 'user':
                    self.parent.user.stat['damage'] += damage
                else:
                    self.parent.enemy['damage'] += damage
                return 'damage', damage

            if effect == "🩹":
                heal = maxhp//10
                if name == 'user':
                    self.parent.user.stat['hp'] += heal
                else:
                    self.parent.enemy['hp'] += heal
                return 'heal', heal

            return 'None', None

        async def handle_effect(self):
            text = ''
            self.parent.user.stat['power'] = self.parent.user.stat['cur_power']
            self.parent.user.stat['def'] = self.parent.user.stat['cur_def']
            self.parent.user.stat['damage'] = self.parent.user.stat['cur_damage']
            for item, data in self.parent.user.effect.items():
                self.parent.user.effect[item] -= 1
                effect_type, value = await self.classify_effect(item, 'user')
                if effect_type == 'damage':
                    text += f"{item} 데미지가 상승합니다. **+{value}%**\n"
                if effect_type == 'dam':
                    text += f"{item} 데미지를 입습니다. **{value}**\n"
                if effect_type == 'heal':
                    text += f"{item} 체력을 회복합니다. **{value}**\n"
            self.parent.user.effect = {
                key: value for key, value in self.parent.user.effect.items() if value != 0}
            for item, data in self.parent.enemy['effect'].items():
                self.parent.enemy['effect'][item] -= 1
                effect_type, value = await self.classify_effect(item, 'enemy')
                if effect_type == 'damage':
                    text += f"{item} 데미지가 상승합니다. **+{value}%**\n"
                if effect_type == 'dam':
                    text += f"{item} 데미지를 입습니다. **-{value}**\n"
                if effect_type == 'heal':
                    text += f"{item} 체력을 회복합니다. **{value}**\n"
            self.parent.enemy['effect'] = {
                key: value for key, value in self.parent.enemy['effect'].items() if value != 0}
            return text

        async def getStone(self):
            code = self.parent.enemy['item_code'].split(" ")
            percent = self.parent.enemy['item_percent'].split(" ")
            value = self.parent.enemy['item_amount'].split(" ")
            stones = []
            for i in range(len(code)):
                if getSuccess(int(percent[i]), 100):
                    randomValue = getRandomValue2(value[i])
                    if self.parent.inventory['stone'].get(code[i]):
                        self.parent.inventory['stone'][code[i]
                                                       ] += randomValue
                    else:
                        self.parent.inventory['stone'][code[i]
                                                       ] = randomValue
                    stones.append((code[i], randomValue))
                    await self.parent.user.getStone(code[i], randomValue)
            return stones

        async def getUtil(self):
            code = self.parent.enemy['util_code'].split(" ")
            percent = self.parent.enemy['util_percent'].split(" ")
            value = self.parent.enemy['util_amount'].split(" ")
            utils = []
            for i in range(len(code)):
                if getSuccess(float(percent[i]), 100):
                    randomValue = getRandomValue2(value[i])
                    if self.parent.inventory['util'].get(code[i]):

                        self.parent.inventory['util'][code[i]
                                                      ] += randomValue
                    else:
                        self.parent.inventory['util'][code[i]
                                                      ] = randomValue
                    utils.append((code[i], randomValue))

            return utils

        async def getUse(self):
            code = self.parent.enemy['use_code'].split(" ")
            percent = self.parent.enemy['use_percent'].split(" ")
            value = self.parent.enemy['use_amount'].split(" ")
            uses = []
            for i in range(len(code)):
                if getSuccess(float(percent[i]), 100):
                    randomValue = getRandomValue2(value[i])
                    if self.parent.inventory['use'].get(code[i]):
                        self.parent.inventory['use'][code[i]
                                                     ] += randomValue
                    else:
                        self.parent.inventory['use'][code[i]
                                                     ] = randomValue
                    uses.append((code[i], randomValue))
            return uses

        async def loseStone(self):
            stones = []
            for key in self.parent.inventory['stone'].keys():
                if getSuccess(50, 100):
                    stones.append(key)
            return stones

        async def loseUtil(self):
            utils = []
            for key in self.parent.inventory['util'].keys():
                if getSuccess(50, 100):
                    utils.append(key)
            return utils

        async def loseUse(self):
            uses = []
            for key in self.parent.inventory['use'].keys():
                if getSuccess(50, 100):
                    uses.append(key)
            return uses

        async def winEmbed(self, stones: list, utils: list, uses: list):
            embed = discord.Embed(title="승리!!!", color=0x008000)
            embed.add_field(
                name=f"{self.parent.enemy['exp']} 경험치 획득!", value='\u200b', inline=False)
            await self.parent.user.getKill(self.parent.enemy['name'])
            text = ''
            for i in stones:
                code, value = i
                text += f"**{stone[code]['name']}** **{value}**개 획득!\n"
            if stones:
                embed.add_field(name="광석", value=text, inline=False)
            text = ''
            for i in utils:
                code, value = i
                text += f"**{util[code]['name']}** **{value}**개 획득!\n"
            if utils:
                embed.add_field(name="기타", value=text, inline=False)
            text = ''
            for i in uses:
                code, value = i
                text += f"**{stone[code]['name']}** **{value}**개 획득!\n"
            if uses:
                embed.add_field(name="소비", value=text, inline=False)
            return embed

        async def loseEmbed(self, stones: list, utils: list, uses: list):
            embed = discord.Embed(title="기절했습니다...", colour=0xff0000)
            self.parent.exp //= 2
            embed.add_field(
                name=f"{self.parent.exp} 경험치를 잃어버렸습니다.", value="\u200b", inline=False)
            text = ''
            for i in stones:
                self.parent.inventory['stone'].pop(i)
                text += f"**{stone[i]['name']}**을 전부 잃어버렸습니다.\n"
            if text:
                embed.add_field(name="광석", value=text, inline=False)
            text = ''
            for i in utils:
                self.parent.inventory['util'].pop(i)
                text += f"**{util[i]['name']}**을 전부 잃어버렸습니다.\n"
            if text:
                embed.add_field(name="기타", value=text, inline=False)
            text = ''
            for i in uses:
                self.parent.inventory['use'].pop(i)
                text += f"**{stone[i]['name']}**을 전부 잃어버렸습니다.\n"
            if text:
                embed.add_field(name="소비", value=text, inline=False)
            return embed

        async def win(self, interaction: Interaction):
            stones = await self.getStone()
            utils = await self.getUtil()
            uses = await self.getUse()
            self.parent.exp += self.parent.enemy['exp']
            embed = await self.winEmbed(stones, utils, uses)
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(4)
            await self.parent.setup(interaction)

        async def lose(self, interaction: Interaction):
            stones = await self.loseStone()
            utils = await self.loseUtil()
            uses = await self.loseUse()
            embed = await self.loseEmbed(stones, utils, uses)
            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(4)
            await self.parent.setup(interaction)

        async def handle_attack(self, text: str):
            damage = self.parent.user.stat['power'] * \
                self.parent.user.stat['damage']
            if not getSuccess(self.parent.enemy['avoid'], 100):
                if getSuccess(self.parent.user.stat['crit'], 100):
                    final_damage = damage * \
                        (1+self.parent.user.stat['crit_damage']
                         ) - self.parent.enemy['def']
                    if final_damage < 5:
                        final_damage = 5
                    self.parent.enemy['hp'] -= final_damage
                    text += f"**크리티컬!!!** **{round(final_damage,2)}** 피해를 입혔습니다!\n"
                else:
                    final_damage = damage - \
                        self.parent.enemy['def']
                    if final_damage < 5:
                        final_damage = 5
                    self.parent.enemy['hp'] -= final_damage
                    text += f"**{final_damage}** 피해를 입혔습니다!\n"

            else:
                text += f"적이 **회피** 했습니다!\n"
            if not getSuccess(self.parent.user.stat['avoid'], 100):
                e_damage = self.parent.enemy['power'] * \
                    (self.parent.enemy['damage']) - \
                    self.parent.user.stat['def']
                if e_damage < 5:
                    e_damage = 5
                self.parent.user.stat['hp'] -= e_damage
                text += f"**{round(e_damage,2)}** 피해를 받았습니다!\n"
            else:
                text += "공격을 **회피** 했습니다!\n"
            return text

        async def handle_win(self, interaction: Interaction):
            if self.parent.user.stat['hp'] <= 0:
                self.parent.cnt -= 1
                if self.parent.user.stat['hp'] >= self.parent.enemy['hp']:
                    return await self.win(interaction)
                else:
                    return await self.lose(interaction)
            if self.parent.enemy['hp'] <= 0:
                self.parent.cnt -= 1
                return await self.win(interaction)

        @ui.button(label="⛏", row=1, style=ButtonStyle.green)
        async def attack(self, interaction: Interaction, button: ui.Button):
            text = await self.handle_effect()
            text = await self.handle_attack(text)
            await self.handle_win(interaction)
            if not interaction.response.is_done():
                embed: discord.Embed = self.parent.fight_embed()
                embed.add_field(name="현황", value=text, inline=False)
                await interaction.response.edit_message(embed=embed)

        @ui.button(label="🔮", row=1, style=ButtonStyle.gray, disabled=True)
        async def skill(self, interaction: Interaction, button: ui.Button):
            pass

        @ui.button(label="💊", row=1, style=ButtonStyle.gray, disabled=True)
        async def use(self, interaction: Interaction, button: ui.Button):
            pass

        @ui.button(label="💨", row=1, style=ButtonStyle.red)
        async def run(self, interaction: Interaction, button: ui.Button):
            await self.parent.setup(interaction)

    def fight_embed(self):
        embed = discord.Embed()
        effects = ''
        for item, value in self.user.effect.items():
            effects += f"{item}x{value} "
        embed.add_field(
            name=self.user.userInfo['nickname'],
            value=f"""
            ❤ **{round(self.user.stat['hp'],2)}**
            ⛏ **{self.user.stat['power']}**
            🗡 **{round(self.user.stat['damage'],2)}**
            🛡 **{self.user.stat['def']}**
            {effects}
            """)
        effects = ''
        for item, value in self.enemy['effect'].items():
            effects += f"{item}x{value} "
        embed.add_field(
            name=self.enemy['name'],
            value=f"""
            ❤ **{round(self.enemy['hp'],2)}**
            ⚡ **{self.enemy['power']}**
            🗡 **{round(self.enemy['damage'],2)}**
            🛡 **{self.enemy['def']}**
            {effects}
            """)
        embed.set_thumbnail(url=self.enemy['url'])
        return embed

    class meetView(ui.View):
        def __init__(self, parent: 'Mining'):
            super().__init__(timeout=None)
            self.parent = parent

        @ui.button(label="도전하기", row=1, style=ButtonStyle.green)
        async def go(self, interaction: Interaction, button: ui.Button):
            embed = self.parent.fight_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent.fightView(self.parent))

        @ui.button(label="도망가기", row=1, style=ButtonStyle.red)
        async def back(self, interaction: Interaction, button: ui.Button):
            await self.parent.setup(interaction)

    class setupView(ui.View):
        def __init__(self, parent: 'Mining'):
            super().__init__(timeout=None)
            self.parent = parent
            self.go_button()
            self.end_button()
            self.heal_button()

        async def stone_price(self):
            total_price = 0
            stones = []
            for item, data in self.parent.inventory['stone'].items():
                total_price += data * stone[item]['price']
                stones.append(
                    (stone[item]['name'], data, stone[item]['price']))
            return stones, total_price

        async def endEmbed(self):
            embed = discord.Embed(title="탐험 종료", color=0x008000)
            exp_text = ''
            await self.parent.user.getExp(self.parent.exp)
            exp_text += f"**{self.parent.exp*EXP_EARN}({self.parent.exp}x{EXP_EARN})** 경험치 획득!\n"
            level = await self.parent.user.is_levelup()
            if level:
                if level == MAX_LEVEL+1:
                    exp_text += f"{self.parent.user.userInfo['rebirth']}차 환생 달성!"
                else:
                    exp_text += f"{self.parent.user.userInfo['level']}레벨 달성!"
            embed.add_field(name=f"{exp_text}", value='\u200b', inline=False)
            stones, total_price = await self.stone_price()
            stone_text = ''
            for name, amount, price in stones:
                stone_text += f"**{name} {amount}**개 가격 **{price*amount*MONEY_EARN} ({price}x{amount}x{MONEY_EARN})**\n"
            if stone_text:
                stone_text += f"\n**총 가격 {total_price*MONEY_EARN} ({total_price}x{MONEY_EARN})**"
                embed.add_field(name="광석", value=stone_text, inline=False)
                await self.parent.user.getMoney(total_price)
            util_text = ''
            for key, value in self.parent.inventory['util'].items():
                util_text += f"**{util[key]['name']} {value}**개 획득!\n"
                await self.parent.user.getItem(key, value)
            if util_text:
                embed.add_field(name="기타", value=util_text, inline=False)
            use_text = ''
            for key, value in self.parent.inventory['use'].items():
                # use_text+=f"{}"
                pass
            return embed

        def go_button(self):
            button = ui.Button(label="채광하러가기", emoji="⛏", row=1, style=ButtonStyle.green,
                               disabled=self.parent.user.stat['hp'] == 0 or self.parent.stone_result() > self.parent.user.stat['str'])

            async def go(interaction: Interaction):
                await self.parent.make_enemy()
                self.parent.enemy['effect'] = {}
                enemy = self.parent.enemy
                embed = discord.Embed(title=enemy['name'])
                embed.add_field(
                    name=f"⚡{enemy['power']}\n❤{enemy['hp']}\n🛡{enemy['def']}", value='\u200b')
                embed.set_thumbnail(url=enemy['url'])
                await interaction.response.edit_message(embed=embed, view=self.parent.meetView(self.parent))
            button.callback = go
            self.add_item(button)

        def heal_button(self):
            button = ui.Button(label="회복하기", emoji="🩹",
                               row=1, style=ButtonStyle.red)

            async def heal(interaction: Interaction):
                self.parent.user.stat['hp'] = self.parent.user.stat['maxhp']
                await self.parent.setup(interaction)
            button.callback = heal
            self.add_item(button)

        class throwView(ui.View):
            def __init__(self, parent: 'Mining.setupView'):
                super().__init__(timeout=None)
                self.parent = parent
                self.throw_select()

            def throw_select(self):
                options = [SelectOption(label=f"{stone[item]['name']} {data}개 ({data*stone[item]['price']}💵)", description=f"개당 중량 : {stone[item]['weight']} 총 중량 : {round(stone[item]['weight']*data,2)}", value=item)
                           for item, data in self.parent.parent.inventory['stone'].items()]
                options.insert(0, SelectOption(label="뒤로가기", value='back'))
                options.append(SelectOption(label="모두 버리기", value="drop"))
                select = ui.Select(options=options)

                async def throw(interaction: Interaction):
                    if interaction.data['values'][0] == "back":
                        return await self.parent.parent.setup(interaction)
                    if interaction.data['values'][0] == "drop":
                        self.parent.parent.inventory['stone'] = {}
                        embed: discord.Embed = await self.parent.parent.setupEmbed()
                        embed.add_field(name="광석을 모두 버렸습니다.",
                                        value="\u200b", inline=False)
                        return await interaction.response.edit_message(embed=embed, view=self.parent.throwView(self.parent))
                    await interaction.response.send_modal(self.throwAmountModal(interaction.data['values'][0], self))
                select.callback = throw
                self.add_item(select)

            class throwAmountModal(ui.Modal):

                def __init__(self, code, parent: 'Mining.setupView.throwView'):
                    super().__init__(
                        title=f"{stone[code]['name']} {parent.parent.parent.inventory['stone'][code]}개", timeout=None)
                    self.parent = parent
                    self.code = code
                    self.answer = ui.TextInput(
                        label="버릴 개수를 적어주세요.", default=self.parent.parent.parent.inventory['stone'][code], min_length=1)
                    self.add_item(self.answer)

                async def on_submit(self, interaction: Interaction):
                    value = int(
                        re.sub(pattern=r'[^0-9]', repl='', string=self.answer.value))
                    if self.parent.parent.parent.inventory['stone'][self.code] >= value:
                        self.parent.parent.parent.inventory['stone'][self.code] -= value
                        if self.parent.parent.parent.inventory['stone'][self.code] == 0:
                            del self.parent.parent.parent.inventory['stone'][self.code]
                        message = f"{stone[self.code]['name']} {value}개를 버렸습니다."
                    else:
                        message = f"{stone[self.code]['name']}을 버리지 못했습니다."
                    embed: discord.Embed = await self.parent.parent.parent.setupEmbed()
                    embed.add_field(name=message, value="\u200b", inline=False)
                    await interaction.response.edit_message(embed=embed, view=self.parent.parent.throwView(self.parent.parent))

        @ui.button(label="아이템버리기", emoji="🗑", row=2, style=ButtonStyle.gray)
        async def throwItem(self, interaction: Interaction, button: ui.Button):
            await interaction.response.edit_message(embed=await self.parent.setupEmbed(), view=self.throwView(self))

        def end_button(self):
            button = ui.Button(label="돌아가기", emoji="🏠",
                               row=2, style=ButtonStyle.danger, disabled=self.parent.stone_result() > self.parent.user.stat['str'])

            async def end(interaction: Interaction):
                self.parent.user.where = '광산 정산중'
                embed = await self.endEmbed()
                await interaction.response.edit_message(embed=embed, view=None)
                await asyncio.sleep(7)
                await interaction.delete_original_response()
                self.parent.user.where = ''
            button.callback = end
            self.add_item(button)

    async def make_enemy(self):
        cur = con.cursor()
        cur.execute(
            "SELECT percent FROM enemy WHERE floor = %s", self.floor.value)
        percent = cur.fetchall()
        percent = [value[0] for value in percent]
        idx = checkSuccess(percent)
        if idx == -1:
            embed = discord.Embed(title=self.floor.name)
            embed.add_field(name="아무것도 만나지 못했습니다.",
                            value="\u200b", inline=False)
            await self.interaction.edit_original_response(embed=embed, view=None)
            await asyncio.sleep(3)
            await self.setup()
        else:
            cur.execute(
                "SELECT name,power,hp,def,avoid,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,use_code,use_percent,use_amount,url FROM enemy WHERE floor = %s  LIMIT %s, 1", (self.floor.value, idx))
            self.enemy = makeDictionary(['name', 'power', 'hp', 'def', 'avoid', 'exp', 'item_code', 'item_percent',
                                        'item_amount', 'util_code', 'util_percent', 'util_amount', 'use_code', 'use_percent', 'use_amount', 'url'], cur.fetchone())
            self.enemy['damage'] = 1
            self.enemy['maxhp'] = self.enemy['hp']
            self.enemy['effect'] = {}

    async def setupEmbed(self):
        embed = discord.Embed(title=self.floor.name)
        if self.user.stat['hp'] < 0:
            self.user.stat['hp'] = 0
            embed.set_footer(text="체력이 없습니다!")
        self.user.effect = {}
        embed.add_field(
            name=f"중량: {round(self.stone_result(),2)}/{self.user.stat['str']}\n❤{ round(self.user.stat['hp'],2)}", value='\u200b', inline=False)
        embed.add_field(name=f"얻은 경험치 : {self.exp}",
                        value="\u200b", inline=False)
        if self.cnt >= 0:
            embed.add_field(name=f"남은 탐험 기회 : {self.cnt}", value="\u200b")
            if self.cnt == 0:
                embed.set_footer(text="탐험 기회가 없습니다!")
        if self.stone_result() > self.user.stat['str']:
            embed.set_footer(text="무게가 너무 무겁습니다!")
        return embed

    async def setup(self, interaction: Interaction):
        embed = await self.setupEmbed()
        try:
            await interaction.response.edit_message(content="", embed=embed, view=self.setupView(self))
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=self.setupView(self))


class MakeItem:
    def __init__(self, user: User, interaction: Interaction):
        self.user = user
        self.interaction = interaction
        self.category = ""
        self.page = 0

    async def validity(self):
        if self.user.where:
            await self.interaction.response.send_message(f"현재 {self.user.where}에 있어 입장할 수 없습니다.", ephemeral=True)
        else:
            self.user.where = "제작소"
            await self.categorySetup(self.interaction, '0')

    async def categorySetup(self, interaction: Interaction, value='1'):
        if value == "0":
            await interaction.response.send_message(view=self.categoryView(self), ephemeral=True)
        else:
            await interaction.response.edit_message(view=self.categoryView(self))

    class categoryView(ui.View):
        def __init__(self, parent: 'MakeItem'):
            super().__init__(timeout=None)
            self.parent = parent

        @ui.button(label="무기", emoji="⛏", row=0, style=ButtonStyle.green)
        async def weapon(self, interaction: Interaction, button: ui.Button):
            self.parent.category = "weapon"
            await self.parent.setup(interaction)

        @ui.button(label="방어구", emoji="🛡", row=0, style=ButtonStyle.green)
        async def wear(self, interaction: Interaction, button: ui.Button):
            self.parent.category = "wear"
            await self.parent.setup(interaction)

        @ui.button(label="소비", emoji="💊", row=1, style=ButtonStyle.green)
        async def use(self, interaction: Interaction, button: ui.Button):
            self.parent.category = "use"
            await self.parent.setup(interaction)

        @ui.button(label="기타", emoji="📜", row=1, style=ButtonStyle.green)
        async def util(self, interaction: Interaction, button: ui.Button):
            self.parent.category = "item"
            await self.parent.setup(interaction)

        @ui.button(label="칭호", emoji="💬", row=0, style=ButtonStyle.green)
        async def title(self, interaction: Interaction, button: ui.Button):
            self.parent.category = "title"
            await self.parent.setup(interaction)

        @ui.button(label="나가기", emoji="🚪", row=2, style=ButtonStyle.red)
        async def quit(self, interaction: Interaction, button: ui.Button):
            self.parent.category = ""
            self.parent.user.where = ""
            await interaction.response.edit_message(content="제작소에서 나갑니다.", embed=None, view=None)
            await interaction.delete_original_response()

    class setupView(ui.View):
        def __init__(self, parent: 'MakeItem'):
            super().__init__(timeout=None)
            self.parent = parent
            self.select_function()
            self.amount = 1
            self.key = "1"

        async def getItemEmbed(self, key: str):
            data: dict = list(
                item[self.parent.category][int(key)].values())[0]
            if self.parent.category == "item":
                embed = discord.Embed(
                    title=f"{data['name']} {data['amount']*self.amount}개")
            elif self.parent.category == "weapon":
                value = weapon[data['key']]
                embed = discord.Embed(
                    title=f"[{value['rank']}]{value['name']}")
                embed.add_field(
                    name="스텟", value=f"```공격력 : {data['power'].replace(' ','~')}\n마나 : {data['mana'].replace(' ','~')}\n데미지 : {data['damage'].replace(' ','~')}%```")
                embed.set_thumbnail(url=value['url'])
            elif self.parent.category == "wear":
                value = wear[data['key']]
                embed = discord.Embed(
                    title=f"[{value['rank']}]{value['name']}")
                embed.add_field(
                    name="스텟", value=f"```공격력 : {data['power'].replace(' ','~')}\n체력 : {data['hp'].replace(' ','~')}\n중량 : {data['str'].replace(' ','~')}\n방어력 : {data['def'].replace(' ','~')}\n마나 : {data['mana'].replace(' ','~')}```")
                embed.set_thumbnail(url=value['url'])

            text = '```'
            for i, d in data['required'].items():
                if i == "money":
                    text += f"{format(self.parent.user.userInfo['money'],',')}/{format(d*self.amount,',')} 골드\n"
                else:
                    text += f"{util[i]['name']} {await self.parent.user.isExistItem(i)}/{d*self.amount}개\n"
            text += "```"
            embed.add_field(name="재료", value=text, inline=False)
            return embed

        class AmountUpDown(ui.View):
            def __init__(self, parent: 'MakeItem.setupView'):
                super().__init__(timeout=None)
                self.parent = parent
                if self.parent.parent.category == "use" or self.parent.parent.category == "item":
                    self.setupButton()
                self.makeButton()

            def setupButton(self):
                for i in ['+1', '+5', '+10', '+25']:
                    button = ui.Button(style=ButtonStyle.green,
                                       label=i, custom_id=i, row=0)
                    button.callback = self.buttonCallback
                    self.add_item(button)
                for i in ['-1', '-5', '-10', '-25', '초기화']:
                    button = ui.Button(style=ButtonStyle.red,
                                       label=i, custom_id=i, row=1)
                    button.callback = self.buttonCallback
                    self.add_item(button)

            def makeButton(self):
                data: dict = item[self.parent.parent.category][int(
                    self.parent.key)]
                data = list(data.values())[0]
                disabled = False
                for i, d in data['required'].items():
                    if i == "money":
                        disabled = self.parent.parent.user.userInfo['money'] < d * \
                            self.parent.amount
                    else:
                        disabled = self.parent.parent.user.syncisExistItem(
                            i) < d*self.parent.amount
                    if disabled:
                        break
                make_button = ui.Button(
                    style=ButtonStyle.blurple, label="제작하기", disabled=disabled, row=2)
                make_button.callback = self.makeButtonCallback
                self.add_item(make_button)

            async def makeButtonCallback(self, interaction: Interaction):
                amount = 0
                data = list(item[self.parent.parent.category]
                            [int(self.parent.key)].values())[0]
                for key, value in data['required'].items():
                    if key == "money":
                        await self.parent.parent.user.getMoney(-value*self.parent.amount)
                    else:
                        await self.parent.parent.user.getItem(key, -value*self.parent.amount)
                if self.parent.parent.category == "item" or self.parent.parent.category == "use":
                    for i in range(self.parent.amount):
                        if getSuccess(data['percent'], 100):
                            amount += 1
                    await self.parent.parent.user.getItem(data['code'], amount)
                    total_amount = self.parent.amount
                    self.parent.amount = 1
                    embed = await self.parent.getItemEmbed(self.parent.key)
                    embed.add_field(
                        name="제작완료", value=f"{total_amount}개 중에 {amount}개 제작에 성공했습니다.", inline=False)
                else:
                    embed = await self.parent.getItemEmbed(self.parent.key)
                    if getSuccess(data['percent'], 100):
                        text = '```'
                        if self.parent.parent.category == "weapon":
                            stat = await self.parent.parent.user.getWeapon(data)

                        if self.parent.parent.category == "wear":
                            stat = await self.parent.parent.user.getWear(data)
                        for key, value in stat.items():
                            text += f"{translateName(key)} {value}\n"
                        text += '```'

                        embed.add_field(name="제작성공", value=text, inline=False)
                self.parent.amount = 1
                await interaction.response.edit_message(embed=embed, view=self.parent.AmountUpDown(self.parent))

            async def buttonCallback(self, interaction: Interaction):
                custom_id = interaction.data['custom_id']
                if custom_id == "초기화":
                    self.parent.amount = 1
                else:
                    value = int(custom_id)
                    self.parent.amount += value
                    if self.parent.amount < 1:
                        self.parent.amount = 1
                await interaction.response.edit_message(embed=await self.parent.getItemEmbed(self.parent.key), view=self.parent.AmountUpDown(self.parent))

            @ui.button(label="뒤로가기", style=ButtonStyle.red, row=2)
            async def quit(self, interaction: Interaction, button: ui.Button):
                await self.parent.parent.setup(interaction)

        def select_function(self):
            select = ui.Select(placeholder="아이템을 선택해주세요.",
                               options=self.options())

            async def item_select(interaction: Interaction):
                self.key = interaction.data['values'][0]
                if self.key == "next":
                    self.parent.page += 1
                    await self.parent.setup(interaction)

                elif self.key == "prev":
                    self.parent.page -= 1
                    await self.parent.setup(interaction)
                else:
                    await interaction.response.edit_message(embed=await self.getItemEmbed(interaction.data['values'][0]), view=self.AmountUpDown(self))
            select.callback = item_select
            self.add_item(select)

        def options(self):
            items = list_chunk(item[self.parent.category], 10)
            options = []
            for i in items[self.parent.page]:
                i: dict
                key = list(i.keys())[0]
                option_item: dict = list(i.values())[0]
                if self.parent.category == "item":
                    options.append(SelectOption(
                        label=f"{option_item['name']} {option_item['amount']}개", description="거래가능" if util[option_item['code']]['trade'] else '거래불가', value=key))
                elif self.parent.category == "wear":
                    data: dict = wear[option_item['key']]
                    options.append(SelectOption(
                        label=f"Lv.{data['level']} [{data['rank']}] {data['name']}", description=f"{data['collection']} 세트", value=key))
                elif self.parent.category == "weapon":
                    data: dict = weapon[option_item['key']]
                    options.append(SelectOption(
                        label=f"Lv.{data['level']} [{data['rank']}] {data['name']}", value=key))
                elif self.parent.category == "title":
                    data: dict = title[option_item['key']]
                    options.append(SelectOption(
                        label=f"Lv.{data['level']} [{data['rank']}] {data['name']}", description=data['description'], value=key))
            if len(items) > self.parent.page + 1:
                options.append(SelectOption(label="다음으로", value="next"))
            if self.parent.page > 0:
                options.append(SelectOption(label="이전으로", value="prev"))
            return options

        @ui.button(label="뒤로가기", emoji="🚪", style=ButtonStyle.red, row=1)
        async def quit(self, interaction: Interaction, button: ui.Button):
            await self.parent.categorySetup(interaction)

    async def setupEmbed(self):
        embed = discord.Embed(title=f"{translateName(self.category)} 제작소")
        return embed

    async def setup(self, interaction: Interaction):
        try:
            await interaction.response.edit_message(embed=await self.setupEmbed(), view=self.setupView(self))
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(embed=await self.setupEmbed(), view=self.setupView(self))


async def authorizeUser(user: User, interaction: Interaction):
    if not user.stat or not user.userInfo:
        await interaction.response.send_message("`캐릭터생성` 명령어를 통해 캐릭터를 생성해 주세요!", ephemeral=True)
        return True
    return False


@tree.command(name="정보", description="정보")
async def info(interaction: Interaction):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return
    await interaction.response.send_message("정보를 불러오는 중이에요!", ephemeral=True)
    image = await user.Info(interaction)

    class view(ui.View):
        @ui.button(label="새로고침", style=ButtonStyle.green)
        async def reset(self, interaction: Interaction, button: ui.Button):
            image = await User(interaction.user.id).Info(interaction)
            await interaction.response.edit_message(attachments=[image])
    await interaction.edit_original_response(content="", attachments=[image], view=view(timeout=None))


@tree.command(name="경험치획득량변경", description="운영자전용명령어")
async def exp_up(interaction: Interaction, 배율: float):
    if User(interaction.user.id).userInfo['role'] == 99:
        global EXP_EARN
        EXP_EARN = 배율
        await interaction.response.send_message(f"성공적으로 {배율}배율로 조정 되었습니다.", ephemeral=True)


@tree.command(name="골드획득량변경", description="운영자전용명령어")
async def gold_up(interaction: Interaction, 배율: float):
    if User(interaction.user.id).userInfo['role'] == 99:
        global MONEY_EARN
        MONEY_EARN = 배율
        await interaction.response.send_message(f"성공적으로 {배율}배율로 조정 되었습니다.", ephemeral=True)


@tree.command(name="현재획득량확인", description="경험치, 골드 획득량을 확인할수 있습니다.")
async def show_exp_gold_up(interaction: Interaction):
    await interaction.response.send_message(content=f"경험치 획득량: {EXP_EARN}배\n골드 획득량: {MONEY_EARN}배", ephemeral=True)


@tree.command(name="스텟", description="스텟 올리기")
async def stat(interaction: Interaction, 스텟: statEnum, 포인트: int):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return
    if user.where:
        return await interaction.response.send_message(f"현재 {user.where}에 있어 스텟을 올릴 수 없어요.", ephemeral=True)
    message = await user.statusUp(스텟, 포인트)
    await interaction.response.send_message(message, ephemeral=True)


@tree.command(name="기타아이템넣기", description="운영자 전용 명령어")
async def put_util(interaction: Interaction, 아이디: str, 코드: int, 개수: int):
    user = User(아이디)
    if await authorizeUser(user, interaction):
        return
    await user.getItem(코드, 개수, "put")
    await interaction.response.send_message(f"{user.userInfo['nickname']}님에게 {util[str(코드)]['name']}을 {개수}개 지급했습니다.", ephemeral=True)


@tree.command(name="퀘스트", description="퀘스트입니다.")
async def qeust(interaction: Interaction):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return
    quest = Quest(user)

    class questView(ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.type = 'normal'

        @ui.button(label="일반", emoji="📗")
        async def normal_quest(self, interaction: Interaction, button: ui.Button):
            self.type = 'normal'
            image = await quest.getQuest(self.type)
            await interaction.response.edit_message(attachments=[image])

        @ui.button(label="일일", emoji="⏰")
        async def daily_quest(self, interaction: Interaction, button: ui.Button):
            self.type = "daily"
            image = await quest.getQuest(self.type)
            await interaction.response.edit_message(attachments=[image])

        @ui.button(label="주간", emoji="📅")
        async def weekly_quest(interaction: Interaction, button: ui.Button):
            pass

        @ui.button(emoji="⬅", row=2, style=ButtonStyle.blurple)
        async def previous_page(self, interaction: Interaction, button: ui.Button):
            quest.page -= 1
            image = await quest.getQuest(self.type)
            if image:
                await interaction.response.edit_message(attachments=[image])

        @ui.button(emoji="➡", row=2, style=ButtonStyle.blurple)
        async def next_page(self, interaction: Interaction, button: ui.Button):
            quest.page += 1
            image = await quest.getQuest(self.type)
            await interaction.response.edit_message(attachments=[image])

        @ui.button(label="보상수령하기", emoji="🎁", row=2, style=ButtonStyle.green)
        async def claim(self, interaction: Interaction, button: ui.Button):
            normal_text, daily_text, weekly_text, num = await quest.claimQuest()
            if not normal_text + weekly_text + daily_text:
                embed = discord.Embed(title="퀘스트보상", color=0xff0000)
                embed.add_field(name="수령가능한 퀘스트 보상이 없습니다.", value="\u200b")
            else:
                embed = discord.Embed(title="퀘스트보상", color=0x009900)
                if normal_text:
                    embed.add_field(name="일반", value=normal_text, inline=False)
                if daily_text:
                    embed.add_field(name="일일", value=daily_text, inline=False)
                if weekly_text:
                    embed.add_field(name="주간", value=weekly_text, inline=False)
            if num == MAX_LEVEL+1:
                embed.add_field(
                    name=f"{quest.user.userInfo['rebirth']}차 환생 달성!", value="\u200b", inline=False)
            elif num:
                embed.add_field(
                    name=f"{quest.user.userInfo['level']}레벨 달성!", value='\u200b', inline=False)

            image = await quest.getQuest(self.type)
            await interaction.response.edit_message(attachments=[image], embed=embed)
    await interaction.response.send_message(file=await quest.getQuest("normal"), view=questView(), ephemeral=True)


@tree.command(name="퀘스트생성", description="운영자 전용 명령어")
async def make_quest(interaction: Interaction, 아이디: str, 키: int, 타입: questTypeEnum):
    if User(interaction.user.id).userInfo['role'] == 99:
        user = User(아이디)
        quest = Quest(user)
        await quest.makeQuest(타입.value, str(키))
        await interaction.response.send_message(f"성공적으로 {user.userInfo['nickname']}님에게 퀘스트를 생성했습니다.", ephemeral=True)
    else:
        await interaction.response.send_message(f"권한이 없습니다.", ephemeral=True)


@tree.command(name="강화", description="강화소")
async def reinforcement(interaction: Interaction, 부위: reinEnum):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return

    reinforce = Reinforce(user, 부위, interaction)
    await reinforce.validity()


@tree.command(name="채광", description="채광")
async def mining(interaction: Interaction, 광산: miningEnum):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return
    mine = Mining(user, 광산, interaction)
    await mine.validity()


@tree.command(name="제작소", description="아이템 제작")
async def makeItem(interaction: Interaction):
    user = User(interaction.user.id)
    if await authorizeUser(user, interaction):
        return
    await MakeItem(user, interaction).validity()

client.run(os.environ['token'])
