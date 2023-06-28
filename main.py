from discord import app_commands, Interaction, ui, ButtonStyle, SelectOption, TextStyle
from discord.ext import tasks
import discord
import random
import datetime
import pymysql
from enum import Enum
from itertools import chain
from collections import Counter
import random
import math
import asyncio
import json
import os
# from dotenv import load_dotenv

# load_dotenv()

GUILD_ID = '9134824600498483220'
STAT_PER_LEVEL = 2
STAT_PER_REBIRTH = 50
MAX_REBIRTH = 10
MAX_LEVEL = 150
KST = datetime.timezone(datetime.timedelta(hours=9))
ticket = {
    -0: {'code': 2, 'cnt': 3},
    -1: {'code': 2, 'cnt': 3},
    -2: {'code': 2, 'cnt': 3},
    -3: {'code': 2, 'cnt': 3},
    -4: {'code': 2, 'cnt': 3},
    -5: {'code': 2, 'cnt': 3},
    -6: {'code': 2, 'cnt': 3},
    -8: {'code': 4, 'cnt': 6},
    -7: {'code': 11, 'cnt': 10}}


class MyClient(discord.Client):
    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=KST))
    async def reward(self):
        await tree.sync()
        weekday = datetime.datetime.now(tz=KST).weekday()
        print(weekday)
        cur = con.cursor()
        cur.execute("SELECT id FROM user_info")
        user = cur.fetchall()
        for i in user:
            setItem(2, i[0], 1)
            cur.execute("SELECT * FROM shop WHERE id=%s", i[0])
            if cur.fetchone():
                cur.execute(
                    "UPDATE shop SET item1='3 -1 250',item2='5 10 350', item3='6 15 75', item4='7 5 1000', item5='16 1 500000',item6='9 1 50000' WHERE id = %s", i[0])
            else:
                cur.execute(
                    "INSERT INTO shop(item1,item2,item3,item4,item5,item6,id) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    ('3 -1 250', "5 10 350", "6 15 75", "7 5 1000", "8 1 30000", "9 1 50000", i[0]))
            # cur.execute("SELECT * FROM quest WHERE id = %s", i[0])
            # if cur.fetchone():
            #     cur.execute("UPDATE quest SET kill1='any 15 0', get1='any 20 0',  ")
            if weekday == 4:
                setItem(4, i[0], 1)
                cur.execute("UPDATE user_boss SET boss1=0")
        con.commit()
        cur.close()

    @tasks.loop(hours=1)
    async def reconnect_db(self):
        cur = con.cursor()
        cur.execute("SELECT * FROM user_info")
        cur.close()

    async def change_message(self):
        while not client.is_closed():
            for i in ['개발', '0.2.0a버전 관리', '버그 제보 부탁']:
                await client.change_presence(status=discord.Status.online, activity=discord.Game(i))
                await asyncio.sleep(5)

    async def on_ready(self):
        await self.wait_until_ready()
        setup()
        self.reward.start()
        self.reconnect_db.start()
        await tree.sync()
        print(miningEnum.요일광산EASY.value)
        print(f"{self.user} 에 로그인하였습니다!")
        await self.change_message()


intents = discord.Intents.all()
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)
con = pymysql.connect(host=os.environ['host'], password=os.environ['password'],
                      user=os.environ['user'], port=int(os.environ['port']), database=os.environ['database'], charset='utf8')
adventrue_inventory = {}
weapon_rein_dic = {}
mining_dic = {}
raid_dic = {}
cnt = {}


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


class makeItemEnum(Enum):
    '''
    제작소,인벤토리 열거형
    --------------------
    `무기 : "weapon"`
    `방어구 : "wear"`
    `기타 : "item"`
    `칭호 : "title"`
    '''
    무기 = "weapon"
    방어구 = "wear"
    기타 = "item"
    칭호 = "title"


class bossEnum(Enum):
    단단한돌3인 = {'name': '단단한돌', 'boss': 1, 'id': 1, 'user': 3, 'level': 30}
    단단한돌2인 = {'name': '단단한돌', 'boss': 1, 'id': 1, 'user': 2, 'level': 35}
    단단한돌1인 = {'name': '단단한돌', 'boss': 1, 'id': 1, 'user': 1, 'level': 35}


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


class statusEnum(Enum):
    '''
    스텟 열거형
    ----------
    `힘 : 'power'`
    `체력 : 'hp'`
    `중량 : 'str'`
    `크리티컬데미지 : 'crit_damage'`

    '''
    힘 = 'power'
    체력 = 'hp'
    중량 = 'str'
    크리티컬데미지 = 'crit_damage'


class rankingEnum(Enum):
    '''
    랭킹 열거형
    ----------
    `레벨 : 'level'`
    `자산 : 'money'`
    `무릉 : 'mooroong'`
    '''
    레벨 = 'level'
    자산 = 'money'
    무릉 = 'mooroong'


def isExistItem(id: int, code: int):
    '''
    user_item에 아이템 있는지 확인
    -----------------------------
    - id: 유저 아이디
    - code: 아이템 코드

    `return amount`
    '''
    cur = con.cursor()
    utils = getJson('./json/util.json')
    try:
        util = utils[str(code)]
    except:
        return -1
    cur.execute(  # code에 해당하는 아이템이 있는지 확인
        "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (id, code))
    amount = cur.fetchone()
    if not amount:  # 없으면 아이템 insert
        cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (code, util['name'], util['description'], util['rank'], util['price'], util['trade'], 0, id))
        con.commit()
        cur.close()
        return 0
    else:
        cur.close()
        return int(amount[0])


def getPart(part: int):
    '''
    part를 한글로 변환
    -----------------
    - parts=["","투구","갑옷","장갑","신발","망토","목걸이","반지","귀걸이"] 

    `return parts[part]`
    '''
    parts = ['', '투구', '갑옷', '장갑', '신발', '망토', '목걸이', '반지', '귀걸이']
    return parts[part]


def getName(id: int):
    '''
    유저 닉네임 구하는 함수
    ---------------------
    - id: 유저 아이디

    `return name`
    '''
    if not authorize(id):
        return
    cur = con.cursor()
    cur.execute("SELECT nickname FROM user_info WHERE id = %s", id)
    return cur.fetchone()[0]


def translateName(name: str):
    '''
    column 명은 한글로 한글은 column 으로 변환
    ----------------------------------------
    `return power <=> 힘`
    '''
    column = ['power', 'hp', 'str', 'crit', 'crit_damage',
              'damage', 'weapon', 'wear', 'title', 'item', 'money', 'level', 'collection']
    korean = ['힘', '체력', '중량', '크리티컬 확률', '크리티컬 데미지',
              '데미지', '무기', '방어구', '칭호', '기타', '골드', '레벨', '컬렉션']
    if name in column:
        return korean[column.index(name)]
    else:
        return column[korean.index(name)]


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


def setItem(code: int, id: int, cnt: int):
    '''
    아이템 code를 cnt값으로 바꾸기
    ----------------------------
    - code: 아이템 코드
    - id: 유저 아이디
    - cnt: 넣을 아이템 갯수
    '''
    cur = con.cursor()
    isExistItem(id, code)
    cur.execute(
        "UPDATE user_item SET amount = %s WHERE item_id = %s AND id = %s", (cnt, code, id))
    con.commit()
    cur.close()


def getItem(code: int, id: int, cnt: int):
    '''
    cnt 개 만큼 아이템 code에 담기
    ----------------------------
    - code: 아이템 코드
    - id: 유저 아이디
    - cnt: 넣을 아이템 갯수
    '''

    cur = con.cursor()
    isExistItem(id, code)
    cur.execute(
        "UPDATE user_item SET amount = amount + %s WHERE item_id = %s AND id = %s", (cnt, code, id))
    con.commit()
    cur.close()


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


def getWear(item: dict, id: int):
    '''
    방어구 정보 만들기
    ----------------
    - item: 방어구 딕셔너리
    - id: 유저 아이디
    '''
    cur = con.cursor()
    power = getRandomValue1(item['power'])
    hp = getRandomValue1(item['hp'])
    str = getRandomValue1(item['str'])
    cur.execute(
        "INSERT INTO user_wear(name,upgrade,`rank`,level,power,hp,`str`,collection,part,wear,trade,id,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (item['name'], 0, item['rank'], item['level'], power, hp, str, item['collection'], item['part'], 0, item['trade'], id, item['url']))
    con.commit()
    cur.close()


def getWeapon(item: dict, id: int):
    '''
    무기 정보 만들기
    ---------------
    - item: 무기 딕셔너리
    - id: 유저 아이디
    '''
    cur = con.cursor()
    power = getRandomValue1(item['power'])
    damage = getRandomValue1(item['damage'])
    cur.execute(
        "INSERT INTO user_weapon(name,upgrade,`rank`,level,power,damage,wear,trade,id,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (item['name'], 0, item['rank'], item['level'], power, damage, 0, item['trade'], id, item['url']))
    con.commit()
    cur.close()


def getTitle(item: dict, id: int):
    '''
    칭호 정보 만들기
    ---------------
    - item: 칭호 딕셔너리
    - id: 유저 아이디
    '''
    cur = con.cursor()
    cur.execute(
        "INSERT INTO user_title(name,`rank`,level,power,hp,`str`,crit,crit_damage,damage,description,wear,trade,id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (item['name'], item['rank'], item['level'], item['power'], item['hp'], item['str'], item['crit'], item['crit_damage'], item['damage'], item['description'], 0, item['trade'], id))
    con.commit()
    cur.close()


def useNotTradeFirst(name: str, amount: int, id: int):
    '''
    교환불가능 아이템 먼저 소비
    -------------------------
    - name: 아이템명
    - amount: 소비해야할 아이템 개수
    - id: 유저 아이디
    '''
    cur = con.cursor()
    cur.execute(
        "SELECT amount FROM user_item WHERE id = %s AND name = %s ORDER BY trade ASC", (id, name))
    items = cur.fetchall()
    if len(items) == 2:
        if items[0][0]+items[1][0] < amount:
            return False
        if items[0][0] <= amount:
            cur.execute(
                "UPDATE user_item SET amount = 0 WHERE id = %s AND trade = 0 AND name = %s", (id, name))
            cur.execute("UPDATE user_item SET amount = amount - %s WHERE id = %s AND trade = 1 AND name = %s ",
                        (amount-items[0][0], id, name))
        else:
            cur.execute(
                "UPDATE user_item SET amount = amount - %s WHERE id = %s AND trade = 0 AND name = %s", (amount, id, name))
    else:
        if len(items) == 1 and items[0][0] >= amount:
            cur.execute(
                "UPDATE user_item SET amount = amount - %s WHERE id = %s AND name = %s", (amount, id, name))
        else:
            return False
    con.commit()
    cur.close()
    return True


def block_exp(rebirth: int, level: int, exp: int):
    '''
    경험치바 렌더러
    --------------
    - level: 유저 레벨
    - exp: 유저 경험치

    `return 경험치바, 필요 경험치`
    '''
    guild = client.get_guild(884259665964314655)
    name = ["0_", "1_", "2_", "3_", "4_", "5_", "6_", "7_", "8_", "9_", "10"]
    block = [discord.utils.get(guild.emojis, name=i) for i in name]
    level_info: dict = getJson('./json/level.json')
    if rebirth == MAX_REBIRTH:
        percent = 100
    else:
        percent = round(exp/level_info[str(rebirth)][str(level)]*100)
    if percent > 100:
        percent = 100
    string = ''
    cnt = 0
    for _ in range(int(percent/10)):
        string += str(block[10])
        cnt += 1
    if cnt != 10:
        string += str(block[int(percent % 10)])
        cnt += 1
    for _ in range(10-cnt):
        string += str(block[0])
        cnt += 1
    return string, level_info[str(rebirth)][str(level)]


def filter_name(name: str):
    filtering = ["gm", '운영', '영자', '시발', 'tlqkf', '병신', 'qudtls', '미친',
                 'alcls', '운영자']
    if not name.isalpha():
        return False
    if name.lower() in filtering:
        return False
    cur = con.cursor()
    cur.execute("SELECT nickname FROM user_info")
    names = cur.fetchall()
    for i in names:
        if i[0] == name:
            return False
    return True


def is_levelup(rebirth: int, level: int, exp: int, id: int):
    '''
    레벨업 했을때
    ------------
    - rebirth: 유저 환생
    - level: 유저 레벨
    - exp: 유저 경험치
    - id: 유저 아이디

    `return 레벨업한 숫자`
    '''
    if rebirth == MAX_REBIRTH:
        return 0
    level_info = getJson('./json/level.json')
    num = 0
    cur = con.cursor()
    while level_info[str(rebirth)][str(level+num)] <= exp:
        exp -= level_info[str(rebirth)][str(level+num)]
        num += 1
        if level+num >= MAX_LEVEL+1 and rebirth != MAX_REBIRTH:
            cur.execute(
                "UPDATE user_info SET exp = %s, rebirth=rebirth+1 WHERE id = %s", (exp, id))
            cur.execute(
                "UPDATE user_stat SET point = point + %s WHERE id = %s", (STAT_PER_REBIRTH, id))
            getItem(8, id, 1)
            cur.close()
            con.commit()
            return MAX_LEVEL+1
    if num > 0:
        cur.execute(
            "UPDATE user_info SET level = level + %s , exp = %s WHERE id = %s", (num, exp, id))
        cur.execute(
            "UPDATE user_stat SET point = point + %s WHERE id = %s", (num*STAT_PER_LEVEL, id))
    cur.close()
    con.commit()

    return num


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
    power = hp = str = crit = damage = 0
    if option:
        for i in option.split(" "):
            number = int(i[1:])
            if i[0] == 'p':
                power += number
            elif i[0] == 'h':
                hp += number
            elif i[0] == 'a':
                hp += number
                str += number
                power += number
            elif i[0] == "c":
                crit += number
            elif i[0] == "d":
                damage += number
    return {'power': power, 'hp': hp, 'str': str, 'crit': crit, 'damage': damage/100}


def authorize(id: int):
    '''
    유저 정보 있는지 확인
    ----------------------
    유저 정보가 있으면 True

    - id: 유저 아이디

    `return True | False`
    '''
    cur = con.cursor()
    cur.execute("SELECT * FROM user_info WHERE id = %s", id)
    value = cur.fetchone() != None
    cur.close()
    return value


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
        "SELECT SUM(power),SUM(hp),SUM(str/10) FROM user_wear WHERE id=%s AND wear = 1 ", id)
    wear = makeDictionary(['power', 'hp', 'str'], cur.fetchone())
    cur.execute("""
                SELECT SUM(A.hp),SUM(A.power),SUM(A.str),SUM(A.crit),SUM(A.crit_damage/100),SUM(A.damage/100) FROM
                collection_effect A JOIN (SELECT collection as col,COUNT(collection) as cnt FROM user_wear WHERE wear=1 AND id=%s GROUP BY collection) B
                ON B.col = A.collection WHERE B.cnt>=A.value""", id)
    collection = makeDictionary(
        ['hp', 'power', 'str', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT name,SUM(hp), SUM(power),SUM(`str`),SUM(crit),SUM(crit_damage/100),SUM(damage/100) FROM user_title WHERE id = %s AND wear = 1", id)
    title = makeDictionary(
        ['title', 'hp', 'power', 'str', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT power,damage/100,`option` FROM user_weapon WHERE id=%s AND wear = 1", id)
    weapon = makeDictionary(['power', 'damage', 'option'], cur.fetchone())
    if weapon:
        option = getOption(weapon['option'])
    else:
        option = {}
    cur.execute(
        "SELECT power,hp*5,str/10,crit,crit_damage/50,point FROM user_stat WHERE id=%s", id)
    stat = makeDictionary(['power', 'hp', 'str', 'crit',
                          'crit_damage', 'point'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0, "str_stat": 0, "power_stat": 0, "power_else": 0, "hp_stat": 0, "crit_damage_stat": 0,
             'damage': 0, 'crit': 0, 'crit_damage': 0, 'maxhp': 0, 'point': 0, 'title': ''}
    for key, value in chain(wear.items(), weapon.items(), option.items(), stat.items(), collection.items(), title.items()):
        if value:
            final[key] += value
    final['maxhp'] = final['hp']
    final['hp_stat'] = stat['hp']
    final['str_stat'] = stat['str']
    final['power_stat'] = stat['power']
    final['crit_damage_stat'] = stat['crit_damage']
    final['power_else'] = final['power']
    if final['damage'] != 0:
        final['power'] *= final['damage']
    cur.close()
    return final


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


def getMoney(id: int):
    '''
    유저 골드 확인하는 함수
    ----------------------
    - id: 유저 아이디
    '''
    if not authorize(id):
        return False
    cur = con.cursor()
    cur.execute("SELECT money FROM user_info WHERE id = %s", id)
    return cur.fetchone()[0]


def setup():
    '''
    데이터베이스 테이블 생성
    ----------------------
    '''
    cur = con.cursor()  # 유저 데이터 테이블 생성
    # user_info 유저 정보(이름,경험치,레벨,돈,역할,생성일자)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_info
                (nickname TEXT,id TEXT,exp INT,level INT,rebirth INT,money INT,role INT,create_at DATE)""")
    # user_stat 유저 스텟(아이디,힘,체력,무게,치명타,치명타데미지,포인트)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_stat 
                (id TEXT,power INT,hp INT,str INT,crit INT,crit_damage INT,point INT)""")
    # user_weapon 유저 무기(아이템아이디,이름,강화,등급,레벨,힘,데미지,옵션,착용여부,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_weapon 
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,upgrade INT,`rank` TEXT,level INT, power INT,damage INT,`option` TEXT,wear BOOLEAN,trade BOOLEAN,id TEXT,url TEXT)""")
    # user_wear 유저 갑옷(아이템아이디,이름,강화,등급,레벨,힘,체력,무게,컬렉션,착용부위,착용여부,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_wear 
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,upgrade INT,`rank` TEXT,level INT,power INT,hp INT,str INT,collection TEXT , part INT,wear BOOLEAN, trade BOOLEAN,id TEXT,url TEXT)""")
    # user_item 유저 아이템(아이템아이디,이름,등급,가격,설명,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_item
                (item_id INT, name TEXT,`rank` TEXT, price INT,description TEXT,trade BOOLEAN,amount INT,id TEXT)""")
    # enemy 광석(이름,힘,체력,층,드롭아이템코드,드롭아이템확률,드롭아이템개수,유틸아이템코드,유틸아이템드롭확률,유틸아이템드롭개수,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS enemy
                (name TEXT,power INT,hp INT,floor INT,exp INT,item_code TEXT,item_percent TEXT,item_amount TEXT,util_code TEXT,util_percent TEXT,util_amount TEXT,url TEXT)""")
    # collection_effect 컬렉션효과(컬렉션,체력,무게,크리티컬 확률,힘,크리티컬 데미지,데미지,개수)
    cur.execute("""CREATE TABLE IF NOT EXISTS collection_effect
                (collection TEXT, hp INT, `str` INT, crit INT, power INT,crit_damage INT,damage INT, value INT)""")
    # user_title 유저 칭호(아이템아이디,이름,등급,레벨,체력,무게,크리티컬,힘,크리티컬 데미지,데미지,설명,착용여부,거래여부,아이디)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_title
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,`rank` TEXT,level INT, hp INT, `str` INT, crit INT,power INT, crit_damage INT, damage INT,description TEXT,wear BOOLEAN,trade BOOLEAN,id TEXT)""")
    # shop 상점(아이템1,아이템2,아이템3,아이템4,아이템5,아이템6,아이디)
    cur.execute("""CREATE TABLE IF NOT EXISTS shop
                (item1 TEXT,item2 TEXT,item3 TEXT,item4 TEXT, item5 TEXT,item6 TEXT, id TEXT)""")
    # boss 보스(아이디,이름,힘,체력,층,골드,유틸아이템코드,유틸아이템드롭확률,유틸아이템드롭개수,경매아이템코드,경매아이템드롭확률,경매아이템드롭개수,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS boss
                (id INT PRIMARY KEY,name TEXT,power INT,hp INT,gold INT, util_code TEXT,util_percent TEXT,util_amount TEXT,auction_code TEXT, auction_percent TEXT, auction_amount TEXT,url TEXT)""")
    cur.close()


@tree.command(name="레이드초기화", description="레이드초기화")
async def raid_clear(interaction: Interaction, 유저: str):
    if interaction.user.id == 432066597591449600:
        raid_dic[int(유저)] = False


@tree.command(name="지식의서", description="지식의 서 사용이 가능하다.")
async def int_book(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message(f"`회원가입` 명령어로 먼저 회원가입을 해주세요.", ephemeral=True)
    amount = isExistItem(interaction.user.id, 16)
    if amount <= 0:
        await interaction.response.send_message(f"지식의 서가 없습니다.", ephemeral=True)
        await asyncio.sleep(3)
        return await interaction.delete_original_response()
    cur = con.cursor()
    cur.execute(
        "UPDATE user_info SET exp = exp + (level+rebirth*10)*750 WHERE id = %s", interaction.user.id)
    con.commit()
    cur.execute(
        "SELECT level,rebirth,exp FROM user_info WHERE id = %s", interaction.user.id)
    level, rebirth, exp = cur.fetchone()
    num = is_levelup(rebirth, level, exp, interaction.user.id)
    if num == MAX_LEVEL+1:
        await interaction.response.send_message(f"{rebirth+1}차 환생 달성!", ephemeral=True)
    elif num > 0:
        await interaction.response.send_message(f"{level+num}레벨 달성!", ephemeral=True)
    else:
        await interaction.response.send_message("성공적으로 사용 되었습니다!", ephemeral=True)
    getItem(16, interaction.user.id, -1)
    await asyncio.sleep(3)
    cur.close()
    return await interaction.delete_original_response()


@tree.command(name="레이드", description="레이드")
async def raid(interaction: Interaction, 보스: bossEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message(f"`회원가입` 명령어로 먼저 회원가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    cur.execute("SELECT level FROM user_info WHERE id = %s",
                interaction.user.id)
    if cur.fetchone()[0] < 보스.value['level']:
        return await interaction.response.send_message(f"최소 {보스.value['level']}레벨을 달성해야 합니다.", ephemeral=True)
    try:
        raid_dic[interaction.user.id]
    except KeyError:
        raid_dic[interaction.user.id] = True
    else:
        if raid_dic[interaction.user.id]:
            return await interaction.response.send_message("이미 레이드에 참여 중입니다.", ephemeral=True)
        raid_dic[interaction.user.id] = True
    cur.execute(
        f"SELECT boss{보스.value['boss']} FROM user_boss WHERE id = %s", interaction.user.id)
    isboss = cur.fetchone()
    if isboss and isboss[0]:
        raid_dic[interaction.user.id] = False
        return await interaction.response.send_message("이미 레이드를 클리어 했습니다.", ephemeral=True)
    matcher = interaction
    party_info = {interaction.user.id: {}}
    sign = [interaction.user.id]

    async def sign_in(interaction: Interaction):
        if interaction.user.id == matcher.user.id or not authorize(interaction.user.id) or interaction.user.id in sign:
            return
        cur.execute("SELECT level,mooroong FROM user_info WHERE id = %s",
                    interaction.user.id)
        level, mooroong = cur.fetchone()
        if level < 보스.value['level']:
            return await interaction.response.send_message(f"최소 {보스.value['level']}레벨을 달성해야 합니다.", ephemeral=True)
        try:
            raid_dic[interaction.user.id]
        except KeyError:
            raid_dic[interaction.user.id] = True
        else:
            if raid_dic[interaction.user.id]:
                return await interaction.response.send_message("이미 레이드에 참여 중입니다.", ephemeral=True)
        cur.execute(
            f"SELECT boss{보스.value['boss']} FROM user_boss WHERE id = %s", interaction.user.id)
        isboss = cur.fetchone()
        if isboss and isboss[0]:
            raid_dic[interaction.user.id] = False
            return await interaction.response.send_message("이미 레이드를 클리어 했습니다.", ephemeral=True)
        sign.append(interaction.user.id)
        signer = interaction
        stat = getStatus(interaction.user.id)
        embed = discord.Embed(
            title=f"Lv.{level} {getName(interaction.user.id)}")
        embed.add_field(
            name=f"{stat['power']}⛏ {stat['hp']}❤", value=f"{mooroong}층")
        view = ui.View(timeout=600)
        yes = ui.Button(label="수락하기", style=ButtonStyle.green,
                        custom_id=str(interaction.user.id))
        no = ui.Button(label="거절하기", style=ButtonStyle.red)

        async def yes_callback(interaction: Interaction):
            if len(party_info.keys()) == 보스.value['user']:
                return await interaction.response.send_message("파티가 가득 찼습니다.", ephemeral=True)
            party_info[int(interaction.data['custom_id'])] = {}
            embed, view = match_setup()
            await interaction.response.edit_message(content="")
            await interaction.delete_original_response()
            await matcher.edit_original_response(embed=embed, view=view)

        async def no_callback(interaction: Interaction):
            sign.remove(signer.user.id)
            await signer.edit_original_response(content="거절당했습니다.")
            await interaction.response.edit_message(content="거절", embed=None, view=None)
            await interaction.delete_original_response()
            await asyncio.sleep(7)
            await signer.delete_original_response()
        view.add_item(yes)
        view.add_item(no)
        yes.callback = yes_callback
        no.callback = no_callback
        await matcher.followup.send(embed=embed, view=view, ephemeral=True)
        await interaction.response.send_message("성공적으로 지원했습니다.", ephemeral=True)

    async def kick_select_callback(interaction: Interaction):
        id = interaction.data['values'][0]
        del party_info[id]
        sign.remove(id)
        del raid_dic[id]
        await interaction.response.edit_message(content="")
        await interaction.delete_original_response()
        embed, view = match_setup()
        await matcher.edit_original_response(embed=embed, view=view)

    async def kick_callback(interaction: Interaction):
        if interaction.user.id != matcher.user.id:
            return await interaction.response.send_message("파티장이 아니면 사용할 수 없습니다.", ephemeral=True)
        view = ui.View()
        options = []
        for i in party_info:
            if i != matcher.user.id:
                options.append(SelectOption(label=getName(i), value=i))
        select = ui.Select(placeholder="강퇴할 유저를 선택해주세요.", options=options)
        view.add_item(select)
        select.callback = kick_select_callback
        await interaction.response.send_message(view=view, ephemeral=True)

    async def exit_callback(interaction: Interaction):
        if interaction.user.id in party_info:
            del party_info[interaction.user.id]
            sign.remove(interaction.user.id)
            raid_dic[interaction.user.id] = False
            await matcher.followup.send(content=f"{getName(interaction.user.id)} 유저님이 나갔습니다.", ephemeral=True)
        if not party_info:
            await matcher.delete_original_response()
            return
        if interaction.user.id == matcher.user.id:
            for i in party_info:
                sign.remove(i)
                raid_dic[interaction.user.id] = False
                del party_info[i]
            await matcher.delete_original_response()

    async def matching(interaction: Interaction):
        embed, view = match_setup()
        await interaction.response.send_message(embed=embed, view=view)

    async def go_callback(interaction: Interaction):
        ready = {}
        for i in sign:
            ready[i] = False
        cur.execute(
            "SELECT name,power,hp,gold,util_code,util_percent,util_amount,auction_code,auction_percent,auction_amount,url FROM boss WHERE id = %s", 보스.value['id'])
        boss = makeDictionary(['name', 'power', 'hp', 'gold', 'util_code',
                              'util_percent', 'util_amount', 'auction_code', 'auction_percent', 'auction_amount', 'url'], cur.fetchone())
        embed = discord.Embed(title=f"{boss['name']}")
        embed.add_field(name=f"{format(boss['hp'],',')}❤", value='\u200b')
        embed.add_field(name=f"{format(boss['power'],',')}⚡", value='\u200b')
        embed.add_field(name="\u200b", value='\u200b', inline=False)
        embed.set_image(url=boss['url'])
        view = ui.View()
        meet = ui.Button(label="⛏", style=ButtonStyle.green, custom_id="First")
        view.add_item(meet)

        async def win():
            util_code = boss['util_code'].split(" ")
            util_percent = boss['util_percent'].split(" ")
            util_amount = boss['util_amount'].split(" ")
            embed = discord.Embed(title="토벌 성공!")
            embed.add_field(
                name=f"{format( boss['gold'],',')}골드 획득!", value="\u200b", inline=False)
            util = getJson('./json/util.json')
            for i in party_info:
                text = ''
                raid_dic[i] = False
                cur.execute(
                    "UPDATE user_info SET money = money + %s WHERE id = %s", (boss['gold'], i))
                for idx in range(len(util_code)):
                    if not util_amount[idx] or not util_code[idx] or not util_percent[idx]:
                        break
                    if getSuccess(float(util_percent[idx]), 100):
                        code = int(util_code[idx])
                        value = getRandomValue2(util_amount[idx])
                        getItem(code, i, value)
                        text += f'[{code}] {util[str(code)]["name"]} {value}개 획득!\n'
                embed.add_field(name=f"{getName(i)}님",
                                value=text, inline=False)
                cur.execute("SELECT COUNT(*) FROM user_boss WHERE id = %s", i)
                if cur.fetchone()[0]:
                    cur.execute(
                        f"UPDATE user_boss SET boss{보스.value['boss']}=1 WHERE id = %s", i)
                else:
                    cur.execute(
                        f"INSERT INTO user_boss(id,boss{보스.value['boss']}) VALUES(%s,%s)", (i, 1))
            con.commit()

            auction_code: list = boss['auction_code'].split(" ")
            auction_percent: list = boss['auction_percent'].split(" ")
            auction_amount: list = boss['auction_amount'].split(" ")
            for i in range(len(auction_code)):
                if not getSuccess(float(auction_percent[i]), 100):
                    auction_code.pop(i)
                    auction_amount.pop(i)
            embed.add_field(name="\u200b", value='\u200b', inline=False)
            embed.add_field(name="잠시 후 경매 화면으로 넘어갑니다.", value="\u200b")
            await matcher.edit_original_response(content="", embed=embed, view=None)
            await asyncio.sleep(9)
            is_up = {}

            async def up_callback(interaction: Interaction):
                auctioner, price, index = interaction.data['custom_id']\
                    .split(" ")
                money = getMoney(interaction.user.id)
                if int(price) > money:
                    await interaction.response.send_message(f"돈이 부족합니다. {money}골드 보유중", ephemeral=True)
                    await asyncio.sleep(2)
                    return await interaction.delete_original_response()
                if int(auctioner) == interaction.user.id:
                    await interaction.response.send_message("이미 입찰중 입니다.", ephemeral=True)
                    await asyncio.sleep(2)
                    return await interaction.delete_original_response()
                await interaction.response.send_message("성공적으로 입찰했습니다.", ephemeral=True)
                await interaction.delete_original_response()
                try:
                    is_up[matcher.user.id]
                except KeyError:
                    is_up[matcher.user.id] = 1
                else:
                    is_up[matcher.user.id] += 1
                await auction_callback(interaction, interaction.user.id, int(price)+500, int(index))

            async def auction_callback(interaction: Interaction, auctioner: int, price: int, index: int):
                embed = discord.Embed(title="경매")
                util = getJson('./json/util.json')
                embed.add_field(name="경매 물품", value="\u200b", inline=False)
                for i in range(len(auction_code)):
                    if type(auction_amount[i]) is str:
                        auction_amount[i] = getRandomValue2(auction_amount[i])
                    embed.add_field(
                        name=f"[{auction_code[i]}]{util[str(auction_code[i])]['name']} {auction_amount[i]}개", value='\u200b')
                name = getName(auctioner)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name=f"[{auction_code[index]}]{util[str(auction_code[index])]['name']} {auction_amount[index]}개", value="\u200b")
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name=f"입찰가 : {format(price,',')} 골드", value='\u200b')
                embed.add_field(
                    name=f"구매자 : {name if name else '없음'}", value="\u200b")
                embed.add_field(name="10초 후 낙찰됩니다.",
                                value='\u200b', inline=False)
                up_button = ui.Button(style=ButtonStyle.green,
                                      label="입찰하기", custom_id=f"{auctioner} {price} {index}")
                view = ui.View()
                view.add_item(up_button)
                up_button.callback = up_callback
                await matcher.edit_original_response(embed=embed, view=view)
                await asyncio.sleep(10)
                try:
                    is_up[matcher.user.id]
                except KeyError:
                    if len(auction_amount)-1 > index:
                        await matcher.edit_original_response(embed=None, view=None, content="경매가 종료 되었습니다.")
                        await asyncio.sleep(5)
                        cur.close()
                        del is_up[matcher.user.id]
                        return await matcher.delete_original_response()
                    return await auction_callback(interaction, 0, 3000, index+1)
                if is_up[matcher.user.id]:
                    is_up[matcher.user.id] -= 1
                    return
                if len(auction_amount)-1 > index:
                    getItem(
                        auction_code[index], auctioner, auction_amount[index])
                    cur.execute(
                        "UPDATE user_info SET money = money - %s WHERE id = %s", (price, auctioner))
                    await auction_callback(interaction, 0, 3000, index+1)
                else:
                    getItem(
                        auction_code[index], auctioner, auction_amount[index])
                    cur.execute(
                        "UPDATE user_info SET money = money - %s WHERE id = %s", (price, auctioner))
                    await matcher.edit_original_response(embed=None, view=None, content="경매가 종료 되었습니다.")
                    await asyncio.sleep(5)
                    await matcher.delete_original_response()
                    cur.close()
                    del is_up[matcher.user.id]
            await auction_callback(interaction, 0, 3000, 0)

        async def lose():
            if len(ready) == 0:
                embed = discord.Embed(title="토벌실패")
                await matcher.edit_original_response(
                    embed=embed, view=None, content="")
                await asyncio.sleep(10)
                await matcher.delete_original_response()
                for i in party_info:
                    raid_dic[i] = False

        async def die(id: int):
            del ready[id]
            print(ready)
            await lose()

        async def attack_callback(interaction: Interaction):
            if not interaction.user.id in ready.keys():
                return
            ready[interaction.user.id] = True
            isready = len(ready.keys()) == Counter(ready.values())[True]
            keys = list(ready.keys())
            if isready:
                string = ''
                for i in keys:
                    if getSuccess(party_info[i]['stat']['crit'], 100):
                        damage = party_info[i]['stat']['power']+party_info[i]['stat']['power'] * \
                            party_info[i]['stat']['crit_damage']
                    else:
                        damage = party_info[i]['stat']['power']
                    party_info[i]['stat']['hp'] -= boss['power']
                    if party_info[i]['stat']['hp'] < 0:
                        await die(i)
                        if len(ready.keys()) == 0:
                            return
                    boss['hp'] -= damage
                    string += f'{i}/{damage} '
                    ready[i] = False
                if boss['hp'] < 0:
                    return await win()
                interaction.data['custom_id'] = string
                await meet_callback(interaction)
            else:
                interaction.data['custom_id'] = "ready"
                await meet_callback(interaction)

        async def meet_callback(interaction: Interaction):
            bosshp = format(round(boss['hp'], 2),  ",")
            bosspower = format(boss['power'], ',')
            embed = discord.Embed(title=boss['name'])
            embed.add_field(name=f"{bosshp}❤", value="\u200b")
            embed.add_field(name=f"{bosspower}⚡", value="\u200b")
            embed.add_field(name="\u200b", value='\u200b')
            for i in party_info:
                myhp = format(party_info[i]['stat']['hp'], ',')
                mypower = format(round(party_info[i]['stat']['power'], 2), ',')
                try:
                    ready[i]
                except KeyError:
                    embed.add_field(
                        name=f"{getName(i)}\n{mypower}⛏ {myhp}❤", value="전투불능")
                else:
                    embed.add_field(
                        name=f"{getName(i)}\n{mypower}⛏ {myhp}❤", value="준비완료" if ready[i] else "\u200b")

            if interaction.data['custom_id'] != "ready":
                data = interaction.data['custom_id'].split(" ")
                if data.count("/") != 0:
                    for i in data:
                        user, damage = i.split("/")
                        embed.add_field(
                            name=f"{getName(user)}님이 {format(round(float(damage),2),',')}⛏를 입혔습니다.", value='\u200b', inline=False)
            view = ui.View()
            attack = ui.Button(label="⛏", style=ButtonStyle.green)
            view.add_item(attack)
            attack.callback = attack_callback
            if interaction.data['custom_id'] == "First":
                await interaction.response.send_message(content="\u200b", ephemeral=True)
                await interaction.delete_original_response()
            else:
                await interaction.response.send_message(content="준비완료 되었습니다.", ephemeral=True)
                await interaction.delete_original_response()
            await matcher.edit_original_response(embed=embed, view=view)
        meet.callback = meet_callback
        if interaction.data['custom_id'] == "First":
            await interaction.response.send_message(content="\u200b", ephemeral=True)
            await interaction.delete_original_response()
        await matcher.edit_original_response(embed=embed, view=view)

    def match_setup():
        embed = discord.Embed(
            title=f"Lv.{보스.value['level']} {보스.value['name']} ({len(party_info.keys())}/{보스.value['user']})")
        for i in party_info:
            if not party_info[i]:
                cur.execute(
                    "SELECT level,nickname,rebirth,mooroong FROM user_info WHERE id = %s", i)
                level, nickname, rebirth, mooroong = cur.fetchone()
                party_info[i]['rebirth'] = rebirth
                party_info[i]['nickname'] = nickname
                party_info[i]['level'] = level
                party_info[i]['mooroong'] = mooroong
                party_info[i]['stat'] = getStatus(i)
            party = party_info[i]
            embed.add_field(
                name=f"{party['rebirth']}차 환생 Lv.{party['level']} {party['nickname']}[{party['mooroong']}층]", value=f"{round(party['stat']['power'],2)}⛏ {party['stat']['hp']}❤", inline=False)
        view = ui.View(timeout=None)
        button = ui.Button(label="지원하기", style=ButtonStyle.green, disabled=len(
            party_info.keys()) == 보스.value['user'])
        go = ui.Button(label="출발하기", style=ButtonStyle.red,
                       disabled=len(party_info.keys()) != 보스.value['user'], custom_id="First")
        exit = ui.Button(label="탈퇴하기", style=ButtonStyle.red, row=2)
        kick = ui.Button(label="강퇴하기", style=ButtonStyle.red,
                         row=2, disabled=len(party_info.keys()) == 1)
        view.add_item(button)
        view.add_item(go)
        view.add_item(exit)
        view.add_item(kick)
        button.callback = sign_in
        exit.callback = exit_callback
        kick.callback = kick_callback
        go.callback = go_callback
        return embed, view
    await matching(interaction)


@tree.command(name="데이터베이스싱크", description="제작자 전용 명령어")
async def db_sync(interaction: Interaction):
    if interaction.user.id == 432066597591449600:
        global con
        con.close()
        con = pymysql.connect(host=os.environ['host'], password=os.environ['password'],
                              user=os.environ['user'], port=int(os.environ['port']), database=os.environ['database'], charset='utf8')
        await interaction.response.send_message("성공!", ephemeral=True)


@tree.command(name="커맨드싱크", description="제작자 전용 명령어")
async def sync(interaction: Interaction):
    if interaction.user.id == 432066597591449600:
        if not interaction.guild:
            guild = None
        else:
            guild = discord.Object(id=interaction.guild.id)
        tree.clear_commands(
            guild=guild, type=discord.AppCommandType.chat_input)
        await tree.sync(guild=guild)
        await tree.sync()


@tree.command(name="닉네임변경", description="닉네임 변경권 필요")
async def changeName(interaction: Interaction, 닉네임: str):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("닉네임을 변경할 아이디가 없어요!", ephemeral=True)
    if isExistItem(interaction.user.id, 9):
        if filter_name(닉네임):
            getItem(9, interaction.user.id, -1)
            cur = con.cursor()
            cur.execute("UPDATE user_info SET nickname= %s WHERE id = %s",
                        (닉네임, interaction.user.id))
            con.commit()
            cur.close()
            await interaction.response.send_message(f"{닉네임}닉네임으로 변경되었어요!", ephemeral=True)
        else:
            await interaction.response.send_message(f"{닉네임}은 사용이 불가능합니다!", ephemeral=True)
    else:
        await interaction.response.send_message("닉네임 변경권이 없어요!", ephemeral=True)


@tree.command(name="세트효과", description="현재 적용받는 세트효과를 보여줍니다.")
async def show_collection(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    # 착용중인 아이템의 컬렉션들의 개수를 출력해 collection_effect의 value보다 크면 값 불러오기.
    cur.execute("""SELECT A.collection,A.value,A.hp,A.power,A.str,A.crit,A.crit_damage,A.damage FROM 
                collection_effect A JOIN 
                (SELECT collection as col,COUNT(collection) as cnt FROM user_wear
                WHERE wear=1 AND id=%s GROUP BY collection)
                B ON B.col = A.collection WHERE B.cnt>=A.value""", interaction.user.id)
    embed = discord.Embed(title="세트효과")
    values = cur.fetchall()
    cur.close()
    for i in values:  # 설명 embed 작성
        text = ''
        item = makeDictionary(
            ['collection', 'value', 'hp', 'power', 'str', 'crit', 'crit_damage', 'damage'], i)
        for j in ['hp', 'power', 'str', 'crit', 'crit_damage', 'damage']:
            if item[j] != 0:
                if j == "crit" or j == 'crit_damage' or j == 'damage':
                    text += f"{translateName(j)} {'+' if item[j]>0 else ''}{item[j]}%  "
                else:
                    text += f"{translateName(j)} {'+' if item[j]>0 else ''}{item[j]}  "
        embed.add_field(
            name=f"{item['collection']} {item['value']}세트", value=text, inline=False)
    if not values:
        embed.add_field(name="세트효과를 받지 않고 있어요!", value='\u200b', inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="스텟초기화", description="스텟초기화")
async def reset_stat(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    cur.execute("SELECT amount FROM user_item WHERE id = %s AND item_id = %s",
                (interaction.user.id, 8))
    amount = cur.fetchone()
    if not amount:  # db에 스크롤이 없을때
        cur.close()
        return await interaction.response.send_message("`스텟 초기화 스크롤`이 없습니다.", ephemeral=True)
    else:
        if not amount[0]:  # 스크롤 개수가 0 개 일때
            return await interaction.response.send_message("`스텟 초기화 스크롤`이 없습니다.", ephemeral=True)
        # 스크롤이 있을때
        cur.execute(
            "UPDATE user_item SET amount = amount - 1 WHERE id = %s AND item_id = %s", (interaction.user.id, 8))
        cur.execute("SELECT level,rebirth FROM user_info WHERE id = %s",
                    interaction.user.id)
        level, rebirth = cur.fetchone()
        cur.execute("UPDATE user_stat SET power = 3, str = 5, hp = 10, crit_damage=50 ,point = %s WHERE id = %s",
                    (level*STAT_PER_LEVEL+rebirth*STAT_PER_REBIRTH, interaction.user.id))
        cur.close()
        con.commit()
        await interaction.response.send_message("성공적으로 스텟을 초기화 했습니다.", ephemeral=True)


@tree.command(name="제작소", description="아이템 제작소")
async def makeItem(interaction: Interaction, 종류: makeItemEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    items: dict = getJson("./json/makeItem.json")
    utils: dict = getJson("./json/util.json")
    category = 종류.value
    page = {}
    page[interaction.user.id] = 0
    cnt = {}
    cnt[interaction.user.id] = 1

    async def setup(interaction: Interaction):  # 아이템 select 하는 함수
        cur = con.cursor()
        embed = discord.Embed(title=f"{종류.name} 제작소")
        view = ui.View(timeout=None)
        options = []
        # 페이지당 10개씩 만들기
        for index in range(page[interaction.user.id]*10, (page[interaction.user.id]+1)*10):
            if len(items[category]) <= index:  # 만약 인덱스가 현재 아이템 갯수보다 많으면 break
                break
            item = items[category][index]
            for i in item:  # 아이템 하나인데 포문임(고쳐야됨)
                if category == "wear":
                    option = SelectOption(
                        label=f"Lv.{item[i]['level']} {i}", description=f"{item[i]['collection']} 세트", value=index)
                elif category == "item":
                    option = SelectOption(
                        label=f"{i} {item[i]['amount']}개", description=f"{'거래가능' if utils[item[i]['code']]['trade'] else '거래불가'}", value=index)
                elif category == "title":
                    option = SelectOption(
                        label=f"Lv.{item[i]['level']} {i}", description=item[i]['description'], value=index)
                else:
                    option = SelectOption(
                        label=f"Lv.{item[i]['level']} {i}", value=index)
                options.append(option)
        if len(items[category]) > (page[interaction.user.id]+1)*10:
            options.append(SelectOption(label="다음페이지", value=-1))
        if not page[interaction.user.id] == 0:
            options.append(SelectOption(label="이전페이지", value=-2))
        select = ui.Select(placeholder="아이템을 선택해주세요.", options=options)

        async def select_callback(interaction: Interaction):  # 아이템을 선택했을때.
            index = int(select.values[0])
            if index == -1:
                page[interaction.user.id] += 1
                await interaction.response.edit_message(content="")
                return await setup(interaction)
            if index == -2:
                page[interaction.user.id] -= 1
                await interaction.response.edit_message(content="")
                return await setup(interaction)

            async def makeDetail(interaction: Interaction):  # 아이템 제작 정보 함수
                disabled = False
                req_items = []
                req_amounts = []

                for i in items[category][index]:  # 여기도 고칠필요 있음.
                    item = items[category][index][i]
                    name = i
                    text = f"{i}[{item['rank']}]"
                    if category == "item":
                        text += f" {item['amount']}개"
                    embed = discord.Embed(title=text)
                    if not category == "item" and not category == "title":
                        embed.set_thumbnail(url=item['url'])
                    if category == "title":
                        for j in ['level', 'power', 'hp', 'str', 'crit', 'crit_damage', 'damage']:
                            if item[j] != 0:
                                embed.add_field(
                                    name=f"{translateName(j)} {item[j]}", value='\u200b')
                    elif category == "wear":
                        for j in ['level', 'power', 'hp', 'str', 'collection']:
                            if j == 'level':
                                embed.add_field(
                                    name=f'{translateName(j)} {item[j]}', value="\u200b")
                            elif j == "collection":
                                embed.add_field(
                                    name=f"{translateName(j)} {item[j]}", value='\u200b')
                            else:
                                value1, value2 = item[j].split(" ")
                                embed.add_field(
                                    name=f"{translateName(j)} {value1}~{value2}", value="\u200b")
                    elif category == "weapon":
                        for j in ['level', 'power', 'damage']:
                            if j == 'level':
                                embed.add_field(
                                    name=f'{translateName(j)} {item[j]}', value="\u200b")
                            elif j == 'damage':
                                value1, value2 = item[j].split(" ")
                                embed.add_field(
                                    name=f"{translateName(j)} {value1}%~{value2}%", value='\u200b')
                            else:
                                value1, value2 = item[j].split(" ")
                                embed.add_field(
                                    name=f"{translateName(j)} {value1}~{value2}", value="\u200b")
                    embed.add_field(
                        name="\u200b", value='\u200b', inline=False)
                    req_text = ""
                    for j in item['required']:
                        if j == "money":
                            req_items.append("골드")
                        else:
                            req_items.append(utils[j]['name'])
                        req_amounts.append(
                            item['required'][j])
                        req_text += f"{req_items[-1]} {format(item['required'][j]*cnt[interaction.user.id],',')} 개\n"
                        if req_items[-1] == "골드":
                            cur.execute(
                                "SELECT money FROM user_info WHERE id = %s", interaction.user.id)
                        else:
                            cur.execute(
                                "SELECT SUM(amount) FROM user_item WHERE name = %s AND id = %s", (utils[j]['name'], interaction.user.id))
                        allitem = cur.fetchone()
                        if allitem[0] == None:
                            disabled = True
                        else:
                            if allitem[0] < item['required'][j]*cnt[interaction.user.id]:
                                disabled = True
                    embed.add_field(name="재료", value=req_text)
                    percent = item['percent']
                    embed.set_footer(
                        text=f"성공확률 : {item['percent']}%")
                view = ui.View(timeout=None)
                makebutton = ui.Button(
                    label="제작하기", style=ButtonStyle.green, disabled=disabled)
                backbutton = ui.Button(label="제작취소", style=ButtonStyle.red)

                view.add_item(makebutton)
                view.add_item(backbutton)

                async def back_callback(interaction: Interaction):  # 제작 취소시
                    await interaction.response.edit_message(content="")
                    await setup(interaction)

                # 기타아이템일때 아이템 개수변경
                async def amount_callback(interaction: Interaction):
                    class amountModal(ui.Modal, title=f"개수변경"):
                        answer = ui.TextInput(
                            label="제작할 숫자를 적어주세요.",
                            style=TextStyle.short,
                            placeholder="숫자만 적어주세요.",
                            max_length=3)

                        async def on_submit(self, interaction: Interaction):
                            try:
                                value = int(self.answer.value)
                            except:
                                pass
                            if value < 0:
                                pass
                            cnt[interaction.user.id] = value
                            await makeDetail(interaction)
                    await interaction.response.send_modal(amountModal())

                async def make_callback(interaction: Interaction):  # 제작하기 눌렀을때
                    for i in range(len(req_amounts)):
                        if req_items[i] == "골드":
                            cur.execute(
                                "UPDATE user_info SET money = money - %s WHERE id = %s", (req_amounts[i]*cnt[interaction.user.id], interaction.user.id))
                            con.commit()
                        elif not useNotTradeFirst(
                                req_items[i], req_amounts[i]*cnt[interaction.user.id], interaction.user.id):
                            return await interaction.response.edit_message(content="예기치 못한 오류!", embed=None, view=None)
                    if category != "item":
                        cur.close()
                        if getSuccess(percent, 100):
                            if category == "wear":
                                getWear(item, interaction.user.id)
                            if category == "weapon":
                                getWeapon(item, interaction.user.id)
                            if category == "title":
                                getTitle(item, interaction.user.id)
                            await interaction.response.edit_message(content=f"{item['name']} 제작 성공!")
                            await setup(interaction)
                        else:
                            await interaction.response.edit_message(content=f"{item['name']} 제작 실패...")
                            await setup(interaction)
                    else:
                        real_cnt = 0
                        for i in range(cnt[interaction.user.id]):
                            if getSuccess(percent, 100):
                                real_cnt += 1

                        getItem(item['code'], interaction.user.id,
                                real_cnt*item['amount'])
                        await interaction.response.edit_message(content=f"{item['name']}제작 {cnt[interaction.user.id]}회 중 {real_cnt}번 성공!")
                        await setup(interaction)

                makebutton.callback = make_callback
                backbutton.callback = back_callback
                if category == "item":  # 아이템일때 개수변경 버튼 추가
                    embed.add_field(
                        name=f"제작개수 : {cnt[interaction.user.id]*item['amount']}개", value='\u200b', inline=False)
                    amountbutton = ui.Button(label="개수 변경", row=2)
                    view.add_item(amountbutton)
                    amountbutton.callback = amount_callback
                await interaction.response.edit_message(embed=embed, view=view)
            await makeDetail(interaction)

        select.callback = select_callback
        view.add_item(select)
        try:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(embed=embed, view=view)

    await setup(interaction)


@tree.command(name="캐릭터삭제", description="캐릭터 삭제")
async def deleteUser(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)

    class deleteModal(ui.Modal, title="캐릭터삭제"):  # 캐릭터 삭제 묻는 설문지
        answer = ui.TextInput(label="캐릭터를 한번 삭제하면 되돌릴 수 없어요.",
                              placeholder="'캐릭터삭제' 라고 적어주세요.")

        async def on_submit(self, interaction: Interaction):  # 제출했을때
            if self.answer.value == "캐릭터삭제":
                cur = con.cursor()
                cur.execute("DELETE FROM user_info WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_stat WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_wear WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_weapon WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_item WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_title WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM shop WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_boss WHERE id = %s",
                            interaction.user.id)
                cur.close()
                con.commit()
                return await interaction.response.send_message("성공적으로 캐릭터를 삭제했습니다.", ephemeral=True)
            else:
                return await interaction.response.send_message("캐릭터 삭제 실패", ephemeral=True)
    await interaction.response.send_modal(deleteModal())


@tree.command(name="기타아이템넣기", description="개발자전용명령어")
async def put_util(interaction: Interaction, 코드: int, 개수: int, 유저: discord.Member):
    if not interaction.user.id == 432066597591449600:  # 제작자인지 확인하기
        return
    cur = con.cursor()
    cur.execute("SELECT nickname FROM user_info WHERE id = %s", 유저.id)

    if 유저.id == 874615001527234560:  # 리뉴얼 선택했을때 모든 유저에게 아이템 지급
        cur.execute("SELECT id FROM user_info")
        users = cur.fetchall()
        for i in users:
            isExistItem(i[0], 코드)
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s",
            (개수, 코드))
        con.commit()
        cur.close()
        return await interaction.response.send_message(f"모든 유저에게 {코드} 아이템 {개수} 개를 성공적으로 넣었습니다", ephemeral=True)
    elif not cur.fetchone():
        cur.close()
        return
    else:
        isExistItem(유저.id, 코드)
        cur.execute("UPDATE user_item SET amount = amount+ %s WHERE id = %s AND item_id = %s",
                    (개수, 유저.id, 코드))
    con.commit()
    cur.close()
    return await interaction.response.send_message(f"{유저}에게 {코드} 아이템 {개수} 개를 성공적으로 넣었습니다", ephemeral=True)


@tree.command(name="강화", description="아이템강화")
async def reinforce_weapon(interaction: Interaction, 종류: reinEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    # 이미 강화중이면 강화 불가능
    try:
        if weapon_rein_dic[interaction.user.id]:
            return await interaction.response.send_message("강화할 수 없습니다.", ephemeral=True)
    except KeyError:
        weapon_rein_dic[interaction.user.id] = True
    else:
        weapon_rein_dic[interaction.user.id] = True
    if not authorize(interaction.user.id):
        weapon_rein_dic[interaction.user.id] = False
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    reinforce_info = getJson('./json/reinforce.json')
    category = 'weapon' if 종류.value == 0 else 'wear'

    async def setup(interaction: Interaction):  # 기본 강화 embed 함수
        disabled = False
        try:  # 강화 처음 들어올때.
            item['upgrade']
        except:
            if 종류.name == "무기":
                cur.execute("SELECT upgrade,`rank`,name,url FROM user_weapon WHERE id = %s AND wear = 1",
                            interaction.user.id)
                item = makeDictionary(
                    ['upgrade', 'rank', 'name', 'url'], cur.fetchone())
            else:
                cur.execute("SELECT upgrade,`rank`,name,url FROM user_wear WHERE id = %s AND wear = 1 AND part = %s",
                            (interaction.user.id, 종류.value))
                item = makeDictionary(
                    ['upgrade', 'rank', 'name', 'url'], cur.fetchone())
            if not item:
                weapon_rein_dic[interaction.user.id] = False
                return await interaction.response.send_message("아이템을 장착하지 않았습니다.", ephemeral=True)
        if item['upgrade'] == 25:  # 25강화면 나가게하기
            con.commit()
            weapon_rein_dic[interaction.user.id] = False
            try:
                await interaction.response.send_message("이미 25강화를 완료한 아이템입니다.", ephemeral=True)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(content="25강화를 완료 했습니다.")
            return
        # embed 설정 및 재료 확인
        embed = discord.Embed(
            title=f"{item['name']}[{item['rank']}] +{item['upgrade']} > +{item['upgrade']+1} 강화")
        embed.set_thumbnail(url=item['url'])
        req_percent = reinforce_info['percent'][str(item["upgrade"]+1)]
        req_money = reinforce_info['money'][item['rank']][str(
            item['upgrade']+1)]
        req_item = reinforce_info['item'][item['rank']][str(item['upgrade']+1)]
        stat = reinforce_info[category][item['rank']][str(item['upgrade']+1)]
        embed.add_field(
            name=f"강화 확률 : {req_percent}%", value="\u200b")
        embed.add_field(
            name=f"강화 비용 : {req_money}💰", value="\u200b")
        cur.execute("SELECT money FROM user_info WHERE id = %s",
                    interaction.user.id)
        money = cur.fetchone()[0]
        if money < req_money:
            disabled = True
        utils = []
        names = []
        amounts = []
        embed.add_field(name='\u200b', value='\u200b')
        for i in req_item.split(","):  # 기타아이템 보유중인지 확인
            util, amount = i.split("/")
            embed.add_field(name=f"강화재료 : {util} {amount}개", value="\u200b")
            cur.execute("SELECT amount FROM user_item WHERE id = %s AND name = %s ORDER BY trade ASC",
                        (interaction.user.id, util))
            names.append(util)
            amounts.append(int(amount))
            user_amount = 0
            dump = []
            for j in cur.fetchall():
                user_amount += j[0]
                dump.append(j[0])
            utils.append(dump)
            if user_amount < amounts[-1]:
                disabled = True
        stat_name = getPartRein(종류.value)
        stat *= 5 if stat_name == "체력" else 2 if stat_name == "중량" else 1
        embed.set_footer(
            text=f"강화 성공시 {stat_name} + {stat}")
        view = ui.View(timeout=None)
        button = ui.Button(label="강화하기", disabled=disabled,
                           style=ButtonStyle.green)
        if disabled:
            weapon_rein_dic[interaction.user.id] = False
        view.add_item(button)
        back = ui.Button(label="끝내기", style=ButtonStyle.red)
        view.add_item(back)

        async def back_callback(interacation: Interaction):  # 끝내기 버튼 클릭시
            cur.close()
            weapon_rein_dic[interaction.user.id] = False
            await interacation.response.edit_message(content=".", embed=None, view=None)
            await interacation.delete_original_response()

        async def button_callback(interaction: Interaction):  # 강화하기 버튼 클릭시
            cur = con.cursor()
            for i in range(len(names)):
                if not useNotTradeFirst(names[i], amounts[i], interaction.user.id):
                    return await interaction.response.edit_message(content="강화시도에 실패했습니다.", view=None, embed=None)
            cur.execute("UPDATE user_info SET money = money - %s WHERE id = %s",
                        (req_money, interaction.user.id))
            if getSuccess(req_percent, 100):  # 성공하면
                if 종류.name == "무기":  # 무기일때
                    cur.execute("UPDATE user_weapon SET upgrade = upgrade + 1 , power = power + %s WHERE id = %s AND wear = 1 ",
                                (stat, interaction.user.id))
                else:  # 방어구일때
                    real_name = translateName(stat_name)
                    cur.execute(
                        f"UPDATE user_wear SET upgrade = upgrade +1, {real_name} = {real_name} + {stat} WHERE id = {interaction.user.id} AND wear = 1 AND part = {종류.value} ")
                item['upgrade'] += 1
                if item["upgrade"] >= 20:  # 20강 이상 성공 했을때 해당 채널에 메시지 출력
                    await interaction.channel.send(f"`{interaction.user.display_name}`님이 `{item['name']} +{item['upgrade']}` 강화에 성공했습니다!")
                await interaction.response.edit_message(content="강화에 성공했습니다!", view=None, embed=None)
            else:
                await interaction.response.edit_message(content="강화에 실패했습니다!", view=None, embed=None)
            con.commit()
            await asyncio.sleep(2)
            await setup(interaction)
        back.callback = back_callback
        button.callback = button_callback
        try:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await setup(interaction)


@tree.command(name="상점", description="상점")
async def shop(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    buy_item = {}
    sell_item = {}
    resd = {}
    value = {}
    resd[interaction.user.id] = False
    cur = con.cursor()
    history = []
    utils = getJson('./json/util.json')
    cur.execute(
        "SELECT item1,item2,item3,item4,item5,item6 FROM shop WHERE id = %s", interaction.user.id)
    items = cur.fetchone()
    if not items:
        cur.execute("INSERT INTO shop(item1,id) VALUES(%s,%s)",
                    ('3 -1 250', interaction.user.id))
        con.commit()
        items = ['3 -1 250']
    for item in items:  # 아이템 불러오기
        item: str
        if item != None:
            code, amount, price = item.split(" ")
            buy_item[code] = {"amount": int(
                amount), "price": int(price)}

    async def sell_embed(interaction: Interaction, item: dict):
        embed = discord.Embed(title="판매하기")
        utils = getJson('./json/util.json')
        prices = 0
        for i in item:
            util: dict = utils[str(i)]
            price = util['price']*item[i]
            prices += price
            embed.add_field(
                name=f"[{i}]{util['name']} {item[i]}개", value=f"{format(price,',')} 골드", inline=False)
        embed.set_footer(text=f"총 : {format(prices,',')} 골드")

        async def submit_callback(interaction: Interaction):
            cur.execute("UPDATE user_info SET money = money + %s WHERE id = %s",
                        (prices, interaction.user.id))
            for i in item:
                cur.execute("UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s",
                            (item[i], interaction.user.id, i))
            con.commit()
            embed = discord.Embed(title=f"{prices}골드 획득.")
            view = ui.View()
            shop = ui.Button(label="더 둘러보기", style=ButtonStyle.green)
            shop.callback = setup
            view.add_item(shop)
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def undo_callback(interaction: Interaction):
            item[history[-1][0]] -= history[-1][1]
            if item[history[-1][0]] <= 0:
                del item[history[-1][0]]
            history.pop()
            await sell_embed(interaction, item)
        resd[interaction.user.id] = True
        view = ui.View()
        sell = ui.Button(label="추가하기", style=ButtonStyle.blurple)
        undo = ui.Button(label="되돌리기", disabled=not item,
                         style=ButtonStyle.red)
        submit = ui.Button(label="판매하기", row=2,
                           disabled=not item, style=ButtonStyle.green)
        back = ui.Button(label="돌아가기", row=2, style=ButtonStyle.red)
        sell.callback = sell_callback
        undo.callback = undo_callback
        back.callback = setup
        submit.callback = submit_callback
        view.add_item(sell)
        view.add_item(undo)
        view.add_item(submit)
        view.add_item(back)
        try:
            await interaction.response.edit_message(content="", embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)

    async def buy_submit_callback(interaction: Interaction):
        item_info = interaction.data['custom_id']
        cur.execute(
            "SELECT item1,item2,item3,item4,item5,item6 FROM shop WHERE id = %s", interaction.user.id)
        items = cur.fetchone()
        isNew = False
        for idx, item in enumerate(items):
            if item == item_info:
                isNew = idx+1
                break
        if not isNew:
            await interaction.response.edit_message(content="아이템이 예전 정보 입니다.", view=None, embed=None)
        else:
            code, dump, price = item_info.split(" ")
            getItem(code, interaction.user.id, value[interaction.user.id])
            text = f"{code} {int(dump)-value[interaction.user.id]} {price}"
            cur.execute("UPDATE user_info SET money = money - %s WHERE id = %s",
                        (value[interaction.user.id]*int(price), interaction.user.id))
            if int(dump) != -1:
                cur.execute(
                    f"UPDATE shop SET item{isNew} = %s WHERE id = %s", (text, interaction.user.id))
                buy_item[code]['amount'] = int(dump)-value[interaction.user.id]
            con.commit()
            embed = discord.Embed(title="구매완료!")
            embed.add_field(
                name=f"{utils[code]['name']} {value[interaction.user.id]}개 구매 성공!", value='\u200b')
            view = ui.View()
            button = ui.Button(label="상점 더 둘러보기", style=ButtonStyle.green)

            button.callback = setup
            view.add_item(button)
            await interaction.response.edit_message(embed=embed, view=view)

    async def buy_embed(interaction: Interaction):
        embed = discord.Embed(title=f"아이템 구매")
        code = interaction.data['custom_id']
        left = '∞' if buy_item[code]['amount'] <= -1 \
            else f'{buy_item[code]["amount"]}개'
        money = getMoney(interaction.user.id)
        embed.add_field(
            name=f"{utils[code]['name']} {format(buy_item[code]['price'],',')}골드", value=f"남은개수 : {left}")
        embed.add_field(
            name=f"구매개수 : {value[interaction.user.id]}", value='\u200b')
        price = value[interaction.user.id]*buy_item[code]['price']
        embed.add_field(
            name=f"가격 : {format(price,',')}골드", value='\u200b', inline=False)
        embed.set_footer(text=f"보유중 : {format(money,',')}골드")
        view = ui.View()
        buy = ui.Button(label="구매하기", style=ButtonStyle.blurple,
                        disabled=money < price, custom_id=f"{code} {buy_item[code]['amount']} {buy_item[code]['price']}")
        back = ui.Button(label="돌아가기", style=ButtonStyle.red)
        view.add_item(buy)
        view.add_item(back)

        async def amount_callback(interaction: Interaction):
            id = interaction.data['custom_id']
            if id == "최대":
                if buy_item[code]['amount'] == -1:
                    value[interaction.user.id] += 100
                else:
                    value[interaction.user.id] = buy_item[code]['amount']
            elif id == "0":
                value[interaction.user.id] = 0
            else:
                if value[interaction.user.id]+int(id) >= buy_item[code]['amount'] and buy_item[code]['amount'] != -1:
                    value[interaction.user.id] = buy_item[code]['amount']
                elif value[interaction.user.id]+int(id) < 0:
                    value[interaction.user.id] = 0
                else:
                    value[interaction.user.id] += int(id)
            interaction.data['custom_id'] = code
            await buy_embed(interaction)
        for idx, i in enumerate(['+1', "+5", "+10", "최대", "-1", "-5", "-10", "0"]):
            amount = ui.Button(label=i, custom_id=i, row=1+idx//4,
                               style=ButtonStyle.red if idx//4 else ButtonStyle.green)
            view.add_item(amount)
            amount.callback = amount_callback
        buy.callback = buy_submit_callback
        back.callback = buy_callback

        resd[interaction.user.id] = True
        await interaction.response.edit_message(embed=embed, view=view)

    async def buy_callback(interaction: Interaction):  # 구매하기 눌렀을때
        view = ui.View()
        value[interaction.user.id] = 1
        money = getMoney(interaction.user.id)
        embed = discord.Embed(title="상점")
        embed.add_field(name="진열된 아이템", value="\u200b", inline=False)
        for idx, i in enumerate(buy_item):
            left = '∞' if buy_item[i]['amount'] <= -1 \
                else f'{buy_item[i]["amount"]}개'
            embed.add_field(name=f"{idx+1}.[{i}]{utils[i]['name']} {format(buy_item[i]['price'],',')}골드",
                            value=f"남은 개수: {left}", inline=False)
            disabled = buy_item[i]['amount'] == 0 or money < buy_item[i]['price']
            button = ui.Button(
                label=idx+1, style=ButtonStyle.green, disabled=disabled, row=idx//3, custom_id=str(i))
            view.add_item(button)
            button.callback = buy_embed
        back = ui.Button(label="돌아가기", style=ButtonStyle.red, row=3)
        view.add_item(back)
        resd[interaction.user.id] = True
        back.callback = setup

        await interaction.response.edit_message(embed=embed, view=view)

    async def sell_callback(interaction: Interaction):  # 판매하기 눌렀을때
        class SellModal(ui.Modal, title="판매하기"):
            code = ui.TextInput(
                label="아이템코드", placeholder="아이템 코드를 적어주세요.", max_length=3)
            value = ui.TextInput(label="아이템개수", placeholder="아이템 개수를 적어주세요.")

            async def on_submit(self, interaction: Interaction):
                try:
                    code = int(self.code.value)
                    value = int(self.value.value)
                    if value < 0:
                        return await interaction.response.edit_message(content="0보다 작은 숫자는 판매가 불가능합니다.")
                except:
                    pass
                else:
                    amount = isExistItem(interaction.user.id, code)
                    try:
                        sell_item[code]
                    except KeyError:
                        sell_item[code] = 0
                    if amount >= value+sell_item[code]:
                        if len(sell_item.keys()) >= 21:
                            return await interaction.response.edit_message(content="더이상 판매할 수 없습니다.")
                        sell_item[code] += value
                        history.append((code, value))
                        await sell_embed(interaction, sell_item)
                    else:
                        up = amount-value-sell_item[code]
                        return await interaction.response.edit_message(content=f"아이템 개수가 모자랍니다.\n현재 {f'{up}개 추가 가능' if up>=0 else f'{amount}개 보유중'}")

        await interaction.response.send_modal(SellModal())

    async def setup(interaction: Interaction):
        sell_item.clear()
        embed = discord.Embed(title="상점")
        embed.add_field(name="진열된 아이템", value="\u200b", inline=False)
        for i in buy_item:
            left = '∞' if buy_item[i]['amount'] <= -1 \
                else f'{buy_item[i]["amount"]}개'
            embed.add_field(name=f"{utils[i]['name']} {format(buy_item[i]['price'],',')}골드",
                            value=f"남은 개수: {left}", inline=False)
        money = getMoney(interaction.user.id)
        embed.set_footer(text=f"보유중 : {format(money,',')}골드")
        view = ui.View(timeout=None)
        buy = ui.Button(label="구매하기", style=ButtonStyle.green)
        sell = ui.Button(label="판매하기", style=ButtonStyle.red)
        sell.callback = sell_callback
        buy.callback = buy_callback
        view.add_item(buy)
        view.add_item(sell)
        try:
            if resd[interaction.user.id]:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(embed=embed, view=view)
    await setup(interaction)


@tree.command(name="아이템교환", description="아이템 교환")
async def auction(interaction: Interaction, 상대: discord.Member):
    if not authorize(interaction.user.id) or not authorize(상대.id):
        return await interaction.response.send_message("본인 혹은 상대방이 회원가입 되어있지 않습니다.", ephemeral=True)
    본인 = interaction.user
    if 본인.id == 상대.id:
        return await interaction.response.send_message("본인이 본인에게 거래요청을 할 수 없습니다.", ephemeral=True)
    item = {}
    item[본인.id] = {'ready': False, 'page': 0, 'final': False, 'length': 0}
    item[상대.id] = {'ready': False, "page": 0, 'final': False, 'length': 0}
    global_interaction = interaction

    async def back_callback(interaction: Interaction):
        await interaction.response.edit_message(content="")
        await interaction.delete_original_response()

    async def confirm_callback(interaction: Interaction):
        if interaction.user.id not in [본인.id, 상대.id]:
            return await interaction.response.send_message("당사자가 아니면 버튼을 클릭할 수 없습니다.", ephemeral=True)
        item[interaction.user.id]['ready'] = not item[interaction.user.id]['ready']
        await setup(global_interaction)
        await interaction.response.send_message("거래 확정 버튼을 다시 클릭하면 취소 할 수 있습니다.", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.delete_original_response()

    async def last_callback(interaction: Interaction):
        if interaction.user.id not in [본인.id, 상대.id]:
            return
        item[interaction.user.id]['final'] = not item[interaction.user.id]['final']
        if item[본인.id]['final'] and item[상대.id]['final']:
            cur = con.cursor()

            def check_item(id):
                for i in item[id]:
                    if i not in ['ready', 'page', 'final', 'length']:
                        if i == "money":
                            if item[id][i] >= getMoney(id):
                                return f'오래된 정보!! {getName(id)}님 {translateName(i)} {item[id][i]}에서 에러!'
                        else:
                            for j in item[id][i]:
                                if i == 'item':
                                    cur.execute(
                                        "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (id, j[0]))
                                    amount = cur.fetchone()[0]
                                    if j[1] >= amount:
                                        return f"오래된 정보!! {getName(id)}님 {translateName(i)} {j[0]}에서 에러!"
                                else:
                                    cur.execute(
                                        f"SELECT COUNT(*) FROM user_{i} WHERE id = %s AND item_id = %s", (id, j[0]))
                                    if not cur.fetchone()[0]:
                                        return f"오래된 정보!! {getName(id)}님 {translateName(i)} {j[0]}에서 에러!"
                return True
            message1 = check_item(본인.id)
            message2 = check_item(상대.id)
            if message1 == True and message2 == True:
                for i in item[본인.id]:
                    if i not in ['ready', 'page', 'final', 'length']:
                        if i == "money":
                            cur.execute(
                                "UPDATE user_info SET money = money - %s WHERE id = %s", (item[본인.id][i], 본인.id))
                            cur.execute(
                                "UPDATE user_info SET money = money + %s WHERE id = %s", (item[본인.id][i], 상대.id))
                        else:
                            for j in item[본인.id][i]:
                                if i == 'item':
                                    cur.execute(
                                        "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (j[1], 본인.id, j[0]))
                                    getItem(j[0], 상대.id, j[1])
                                else:
                                    cur.execute(
                                        f"UPDATE user_{i} SET id = %s, wear=0 WHERE id = %s AND item_id = %s", (상대.id, 본인.id, j[0]))
                for i in item[상대.id]:
                    if i not in ['ready', 'page', 'final', 'length']:
                        if i == 'money':
                            cur.execute(
                                "UPDATE user_info SET money = money - %s WHERE id = %s", (item[상대.id][i], 상대.id))
                            cur.execute(
                                "UPDATE user_info SET money = money + %s WHERE id = %s", (item[상대.id][i], 본인.id))
                        else:
                            for j in item[상대.id][i]:
                                if i == 'item':
                                    cur.execute(
                                        "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (j[1], 상대.id, j[0]))
                                    getItem(j[0], 본인.id, j[1])
                                else:
                                    cur.execute(
                                        f"UPDATE user_{i} SET id = %s, wear=0 WHERE id = %s AND item_id = %s", (본인.id, 상대.id, j[0]))
                await interaction.response.edit_message(content="거래 성공!", embed=None, view=None)
                con.commit()
                cur.close()
            else:
                if message1 == True:
                    return await interaction.response.edit_message(content=message2, embed=None, view=None)
                elif message2 == True:
                    return await interaction.response.edit_message(content=message1, embed=None, view=None)
                else:
                    return await interaction.response.edit_message(content=f"{message1}\n{message2}", embed=None, view=None)
        else:
            await final_callback(interaction)

    async def final_callback(interaction: Interaction):
        embed = discord.Embed(title="최종 확인")
        embed.add_field(
            name=f"{getName(본인.id)}님 {'최종확인' if item[본인.id]['final'] else ''}", value='\u200b', inline=False)
        item_maker(id=본인.id, embed=embed)
        embed.add_field(
            name=f"{getName(상대.id)}님 {'최종확인' if item[상대.id]['final'] else ''}", value='\u200b', inline=False)
        item_maker(id=상대.id, embed=embed)
        view = ui.View()
        last = ui.Button(label="최종확인", style=ButtonStyle.green)
        view.add_item(last)
        last.callback = last_callback
        await interaction.response.edit_message(embed=embed, view=view)

    async def money_callback(interaction: Interaction):
        money = int(interaction.data['custom_id'])

        class MoneyModal(ui.Modal, title=f"보유 골드 : {money}"):
            answer = ui.TextInput(
                label="골드", placeholder="여기에 골드를 적어주세요.", max_length=10)

            async def on_submit(self, interaction: Interaction):
                try:
                    value = int(self.answer.value)
                except:
                    pass
                else:
                    if money >= value and value > 0:
                        item[interaction.user.id]['money'] = value
                        item[interaction.user.id]['length'] += 1
                    else:
                        if 'money' in item[interaction.user.id].keys():
                            del item[interaction.user.id]['money']
                            item[interaction.user.id]['length'] -= 1
                    item[본인.id]['ready'] = False
                    item[상대.id]['ready'] = False
                    await interaction.response.edit_message(content="")
                    await interaction.delete_original_response()
                    await setup(global_interaction)
        await interaction.response.send_modal(MoneyModal())

    async def item_callback(interaction: Interaction):
        id, amount = interaction.data['values'][0].split(" ")
        id = int(id)
        amount = int(amount)
        category = interaction.data['custom_id']
        if id == -1:
            await interaction.response.edit_message(content="")
            await interaction.delete_original_response()
            item[interaction.user.id]['page'] = 0
            await setup(global_interaction)
        elif id == -2:
            await interaction.response.edit_message(content="")
            await interaction.delete_original_response()
            item[interaction.user.id]['page'] += 1
            await category_callback(interaction)
        elif id == -3:
            await interaction.response.edit_message(content="")
            await interaction.delete_original_response()
            item[interaction.user.id]['page'] -= 1
            await category_callback(interaction)
        else:
            utils = getJson('./json/util.json')

            class AmountModal(ui.Modal, title=f"{utils[str(id)]['name']} {amount}개"):
                answer = ui.TextInput(
                    label="아이템 갯수", placeholder="아이템 개수를 적어주세요.", max_length=5)

                async def on_submit(self, interaction: Interaction):
                    try:
                        value = int(self.answer.value)
                    except:
                        pass
                    else:
                        if amount >= value:
                            interaction.data['values'] = [f'{id} {value}']
                            interaction.data["custom_id"] = category
                            await select_callback(interaction)

            await interaction.response.send_modal(AmountModal())

    async def select_callback(interaction: Interaction):
        id, name = interaction.data['values'][0].split(" ")
        id = int(id)
        await interaction.response.edit_message(content="")
        await interaction.delete_original_response()
        if id == -1:
            item[interaction.user.id]['page'] = 0
            await setup(global_interaction)
        elif id == -2:
            item[interaction.user.id]['page'] += 1
            await category_callback(interaction)
        elif id == -3:

            item[interaction.user.id]['page'] -= 1
            await category_callback(interaction)
        else:
            category = interaction.data['custom_id']
            try:
                item[interaction.user.id][category]
            except KeyError:
                item[interaction.user.id][category] = []
            if category == "item":
                found = True
                for i in range(len(item[interaction.user.id][category])):
                    if id == int(item[interaction.user.id][category][i][0]):
                        item[interaction.user.id][category][i] = (
                            id, int(name))
                        found = False
                        if int(name) <= 0:
                            idx = item[interaction.user.id][category].index(
                                (id, int(name)))
                            del item[interaction.user.id][category][idx]
                            item[interaction.user.id]['length'] -= 1
                        break

                if found:
                    item[interaction.user.id][category].append((id, int(name)))
                    item[interaction.user.id]['length'] += 1
            elif (id, name) in item[interaction.user.id][category]:
                idx = item[interaction.user.id][category].index((id, name))
                del item[interaction.user.id][category][idx]
                item[interaction.user.id]['length'] -= 1

            else:
                item[interaction.user.id][category].append((id, name))
                item[interaction.user.id]['length'] += 1

            item[본인.id]['ready'] = False
            item[상대.id]['ready'] = False
            item[interaction.user.id]['page'] = 0
            await setup(global_interaction)

    async def category_callback(interaction: Interaction):
        if interaction.user.id not in [본인.id, 상대.id]:
            return await interaction.response.send_message("당사자가 아니면 버튼을 클릭할 수 없습니다.", ephemeral=True)
        category = interaction.data['values'][0]
        if category == "money":
            money = getMoney(interaction.user.id)

            embed = discord.Embed(
                title=f"보유 골드 : {money}")
            view = ui.View()
            button = ui.Button(label="골드 보내기", custom_id=str(
                money), disabled=item[interaction.user.id]['length'] >= 10)
            back = ui.Button(label="돌아가기")
            button.callback = money_callback
            back.callback = back_callback
            view.add_item(button)
            view.add_item(back)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            cur = con.cursor()
            options = [SelectOption(label="종료하기", value="-1 dump")]
            if category == "item":
                cur.execute("SELECT item_id,name,amount,description FROM user_item WHERE id = %s AND trade = 1 AND amount > 0 ORDER BY item_id LIMIT %s,10 ",
                            (interaction.user.id, item[interaction.user.id]['page']*10))
                user_item = cur.fetchall()
                cur.execute(
                    "SELECT COUNT(*) FROM user_item WHERE id = %s AND trade = 1 AND amount > 0", interaction.user.id)
                length = cur.fetchone()[0]
                for i in user_item:
                    options.append(SelectOption(
                        label=f"[{i[0]}] {i[1]} {i[2]}개", value=f"{i[0]} {i[2]}", description=i[3]))

            else:
                if category == "title":
                    cur.execute(
                        "SELECT item_id,name,rank,level,description FROM user_title WHERE id = %s AND trade = 1 ORDER BY item_id LIMIT %s,10",
                        (interaction.user.id, item[interaction.user.id]['page']*10))
                    user_title = cur.fetchall()
                    cur.execute(
                        "SELECT COUNT(*) FROM user_title WHERE id = %s AND trade = 1", interaction.user.id)
                    length = cur.fetchone()[0]
                    for i in user_title:
                        options.append(SelectOption(
                            label=f"[{i[0]}] Lv.{i[3]} {i[1]}[{i[2]}]", value=f"{i[0]} {i[1]}", description=i[4]))
                if category == "wear":
                    cur.execute(
                        "SELECT item_id,name,upgrade,rank,level,collection FROM user_wear WHERE id = %s AND trade = 1 ORDER BY item_id LIMIT %s,10",
                        (interaction.user.id, item[interaction.user.id]['page']*10))
                    user_wear = cur.fetchall()
                    cur.execute(
                        "SELECT COUNT(*) FROM user_wear WHERE id = %s AND trade = 1", interaction.user.id)
                    length = cur.fetchone()[0]
                    for i in user_wear:
                        options.append(SelectOption(
                            label=f"[i[0]] Lv.{i[4]} {i[1]}[{i[3]}] +{i[2]}", value=f"{i[0]} {i[1]}", description=i[5]))
                if category == "weapon":
                    cur.execute(
                        "SELECT item_id,name,upgrade,rank,level FROM user_weapon WHERE id = %s AND trade = 1 ORDER BY item_id LIMIT %s,10",
                        (interaction.user.id, item[interaction.user.id]['page']*10))
                    user_weapon = cur.fetchall()
                    cur.execute(
                        "SELECT COUNT(*) FROM user_weapon WHERE id = %s AND trade = 1", interaction.user.id)
                    length = cur.fetchone()[0]
                    for i in user_weapon:
                        options.append(SelectOption(
                            label=f"[{i[0]}] Lv.{i[4]} {i[1]}[{i[3]}] +{i[2]}", value=f"{i[0]} {i[1]}"))
            if length > (item[interaction.user.id]['page']+1)*10:
                options.append(SelectOption(label="다음으로", value="-2 dump"))
            if item[interaction.user.id]['page'] > 0:
                options.append(SelectOption(label="이전으로", value="-3 dump"))
            select = ui.Select(
                placeholder=f"{translateName(category)}아이템 선택하기", custom_id=category, options=options, disabled=item[interaction.user.id]['length'] >= 10)
            view = ui.View()
            view.add_item(select)
            if category == "item":
                select.callback = item_callback
            else:
                select.callback = select_callback
            await interaction.response.send_message(view=view, ephemeral=True)

    def item_maker(id, embed):
        utils = getJson('./json/util.json')
        for i in item[id]:
            value = ''
            if i == "ready" or i == 'page' or i == 'final' or i == 'length':
                continue
            elif i == 'money':
                value = f'{format(item[id][i],",")}골드'
                embed.add_field(name=f"{translateName(i)}",
                                value=value, inline=False)
            else:
                for j in item[id][i]:
                    if i == "item":
                        value = f'{utils[str(j[0])]["name"]} {j[1]}개'
                    else:
                        value = f'[{j[0]}] {j[1]}'
                    embed.add_field(name=f"{translateName(i)}",
                                    value=value, inline=False)
        return embed

    async def setup(interaction: Interaction):
        embed = discord.Embed(title="교환창")
        embed.add_field(name=f"{getName(본인.id)}님 {item[본인.id]['length']}개 {'[거래완료]' if item[본인.id]['ready'] else ''}",
                        value="\u200b", inline=False)
        embed = item_maker(본인.id, embed)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"{getName(상대.id)}님 {item[상대.id]['length']}개 {'[거래완료]' if item[상대.id]['ready'] else ''}",
                        value='\u200b', inline=False)
        embed = item_maker(상대.id, embed)
        embed.set_footer(text="한번의 거래에는 각 10개씩 아이템을 올릴 수 있어요.")
        view = ui.View(timeout=None)
        options = [SelectOption(label="돈", value="money", description="기본적인 화폐단위."),
                   SelectOption(label="무기", value="weapon",
                                description="무기 아이템"),
                   SelectOption(label="방어구", value="wear",
                                description="방어구 아이템"),
                   SelectOption(label="칭호", value='title',
                                description="칭호 아이템"),
                   SelectOption(label="기타", value="item", description="기타 아이템")]
        category = ui.Select(
            placeholder="거래할 종류의 아이템을 골라주세요.", options=options)
        confirm = ui.Button(label="거래 완료", row=2, style=ButtonStyle.green)

        final = ui.Button(
            label="거래 확정", style=ButtonStyle.blurple, disabled=not (item[본인.id]['ready'] and item[상대.id]['ready']), row=2)
        view.add_item(confirm)
        view.add_item(category)
        view.add_item(final)
        confirm.callback = confirm_callback
        final.callback = final_callback
        category.callback = category_callback
        try:
            await interaction.response.edit_message(content="", embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)

    await interaction.response.send_message("로딩중...")
    await setup(interaction)


@tree.command(name="랭킹", description="랭킹")
async def ranking(interaction: Interaction, 종류: rankingEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    embed = discord.Embed(title=f'{종류.name} 랭킹')
    if 종류.value == "level":  # 레벨기준 랭킹
        cur.execute(
            "SELECT nickname,level,exp,rebirth FROM user_info ORDER BY rebirth DESC, level DESC, exp DESC, create_at ASC LIMIT 0,20 ")
        for i in cur.fetchall():
            block, require = block_exp(i[3], i[1], i[2])
            embed.add_field(
                name=f"{i[0]} {i[3]}차환생 Lv.{i[1]} ({format(i[2],',')}/{format(require,',')})", value=block, inline=False)
        cur.execute(
            "SELECT RANKING FROM (SELECT *,RANK() OVER (ORDER BY rebirth DESC, `level` DESC, `exp` DESC, create_at ASC) RANKING FROM user_info) AS ranked_user_info WHERE id = %s", interaction.user.id)
    elif 종류.value == "money":  # 자산기준 랭킹
        cur.execute(
            "SELECT nickname,money FROM user_info ORDER BY money DESC, create_at ASC LIMIT 0,20")
        for i in cur.fetchall():
            money = format(i[1], ",")
            embed.add_field(name=f"{i[0]} {money}💰",
                            value="\u200b", inline=False)
        cur.execute(
            "SELECT RANKING FROM (SELECT *,RANK() OVER (ORDER BY money DESC, create_at ASC) RANKING FROM user_info) AS ranked_user_info WHERE id= %s", interaction.user.id)
    elif 종류.value == "mooroong":  # 무릉기준 랭킹
        cur.execute(
            "SELECT nickname,mooroong FROM user_info ORDER BY mooroong DESC, create_at ASC LIMIT 0,20")
        for i in cur.fetchall():
            embed.add_field(name=f"{i[0]} {i[1]}층",
                            value='\u200b', inline=False)
        cur.execute(
            "SELECT RANKING FROM (SELECT *,RANK() OVER (ORDER BY mooroong DESC, create_at ASC) RANKING FROM user_info) AS ranked_user_info WHERE id= %s", interaction.user.id)

    embed.set_footer(text=f"내 순위 : {cur.fetchone()[0]}위")
    cur.close()
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="아이템거래", description="거래")
async def trade(interaction: Interaction, 유저: discord.Member, 종류: makeItemEnum, 코드: int, 개수: int):
    authorized = authorize(interaction.user.id) and authorize(유저.id)
    if not authorized:
        return await interaction.response.send_message("`회원가입`이 필요하거나 상대방이 가입하지 않았습니다. ", ephemeral=True)
    cur = con.cursor()
    category = 종류.value
    item_data: dict = getJson('./json/util.json')
    if category == "item":  # 기타아이템 보유중인지 확인하기
        cur.execute("SELECT trade,amount FROM user_item WHERE id = %s AND item_id = %s",
                    (interaction.user.id, 코드))
        try:
            canTrade, amount = cur.fetchone()
        except:
            cur.close()
            return await interaction.response.send_message("아이템이 없습니다", ephemeral=True)
    else:  # 아이템 보유중인지 확인하기
        cur.execute(
            f"SELECT trade FROM {'user_'+category} WHERE id = %s AND item_id = %s", (interaction.user.id, 코드))
        try:
            canTrade = cur.fetchone()[0]
        except:
            cur.close()
            return await interaction.response.send_message("아이템이 없습니다.", ephemeral=True)
    if canTrade:  # 거래가능시
        if category == "item":  # 기타아이템 거래
            if amount >= 개수:  # 개수가 충분하면
                cur.execute(
                    "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (개수, interaction.user.id, 코드))
                isExistItem(유저.id, 코드)
                cur.execute(
                    "UPDATE user_item SET amount = amount + %s WHERE id = %s AND item_id = %s", (개수, 유저.id, 코드))
                cur.close()
                con.commit()
                return await interaction.response.send_message(f"`{유저.display_name}`님에게 `{item_data[str(코드)]['name']}`를 `{개수}` 개 전달했습니다.", ephemeral=True)
            else:
                cur.close()
                return await interaction.response.send_message("아이템이 부족합니다.", ephemeral=True)
        elif category != "item":  # 아이템 거래
            cur.execute(
                f"UPDATE {'user_'+category} SET id = %s, wear=0 WHERE item_id = %s", (유저.id, 코드))
            con.commit()
            cur.execute(
                f"SELECT name FROM {'user_'+category} WHERE item_id = %s",  코드)
            cur.close()
            return await interaction.response.send_message(f"`{유저.display_name}`님에게 `{cur.fetchone()[0]}`를 전달했습니다.", ephemeral=True)
    else:  # 거래불가시
        cur.close()
        return await interaction.response.send_message("거래할 수 없는 아이템 입니다.", ephemeral=True)


@tree.command(name="스텟", description="스테이터스")
async def status(interaction: Interaction, 스텟: statusEnum, 포인트: int):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    message = ''
    if 0 >= 포인트:  # 포인트가 0 보다 작으면
        message = '포인트는 `0`보다 큰 숫자여야 합니다.'
    else:
        cur = con.cursor()
        cur.execute("SELECT point FROM user_stat WHERE id = %s",
                    interaction.user.id)
        point = cur.fetchone()[0]
        if point < 포인트:  # 포인트 보유량이 더 적으면
            message = f'포인트는 `현재 보유 포인트: {point}` 보다 작은 숫자여야 합니다.'
        else:
            cur.execute(f"""UPDATE user_stat SET
            point = point - {포인트} , 
            {스텟.value.replace("'","")} = {스텟.value.replace("'","")} + {포인트} 
            WHERE id = {interaction.user.id}""",)
            cur.close()
            con.commit()
            message = f'`{스텟.name} +{포인트}`'
    await interaction.response.send_message(message, ephemeral=True)
    await asyncio.sleep(3)
    return await interaction.delete_original_response()


@tree.command(name="강화초기화", description="운영자를 부르세요.")
async def reinforceReset(interaction: Interaction, 유저: discord.Member):
    if interaction.user.id == 432066597591449600:  # 강화에 예기치못한 에러가 생겼을때.
        weapon_rein_dic[유저.id] = False
    else:
        author = await client.fetch_user(432066597591449600)
        await author.send(f"{interaction.user}님의 호출이에요.")


@tree.command(name="회원가입", description="회원가입입니다.")
async def register(interaction: Interaction, 닉네임: str):
    cur = con.cursor()
    if authorize(interaction.user.id):
        await interaction.response.send_message("아이디가 있습니다.", ephemeral=True)
    elif not filter_name(닉네임):
        await interaction.response.send_message(f"{닉네임}닉네임은 사용 불가능합니다.", ephemeral=True)
    else:
        # 정보 생성
        cur.execute("""INSERT INTO user_info(nickname,id,exp,level,rebirth,money,role,create_at,mooroong) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (닉네임, interaction.user.id, 0, 1, 0, 100, 0, datetime.datetime.today(), 0))
        cur.execute("INSERT INTO user_stat(id,power,hp,str,crit,crit_damage,point) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (interaction.user.id, 3, 10, 5, 25, 25, 2))
        cur.execute("""INSERT INTO user_weapon(name,upgrade,`rank`,level,power,damage,wear,trade,id,url)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    ('기본 곡괭이', 0, 'F', 1, 5, 100, 1, 0, interaction.user.id, "https://cdn.discordapp.com/attachments/988424121878741022/1040198148661973022/pickaxe1.png"))
        cur.execute("INSERT INTO user_boss(id) VALUES(%s)",
                    interaction.user.id)
        con.commit()
        cur.close()
        await interaction.response.send_message("아이디가 생성되었습니다.", ephemeral=True)


@tree.command(name="정보", description="정보")
async def info(interaction: Interaction, 유저: discord.Member = None):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    if 유저:
        if not authorize(유저.id):  # 유저가 없으면
            return await interaction.response.send_message("해당 유저는 회원가입 하지 않았습니다.", ephemeral=True)

    async def setting(interaction: Interaction):  # 정보 함수
        cur = con.cursor()
        id = interaction.user.id if not 유저 else 유저.id  # 유저 값이 없으면 본인 정보 불러오기
        cur.execute(
            "SELECT nickname,exp,level,rebirth,money,create_at,mooroong FROM user_info WHERE id=%s", id)
        user = makeDictionary(
            ['nickname', 'exp', 'level', 'rebirth', 'money', 'create_at', 'moorong'], cur.fetchone())
        cur.close()
        stat = getStatus(id)
        # embed 생성
        view = ui.View(timeout=None)
        button = ui.Button(label="새로고침")
        view.add_item(button)
        button.callback = setting
        embed = discord.Embed(
            title=f"{user['nickname']}[{'칭호없음' if not stat['title'] else stat['title'] }] {user['rebirth']}차환생")
        string_block, level_info = block_exp(
            user['rebirth'], user['level'], user['exp'])
        money = format(user['money'], ",")
        exp = format(user['exp'], ",")
        level_info_comma = format(level_info, ",")
        if level_info == 0:
            percent = 100
        else:
            percent = round(user['exp']/level_info*100)
        embed.add_field(
            name=f"Lv. {user['level']} {exp}/{level_info_comma}({percent}%)", value=string_block, inline=True)
        embed.add_field(name=f"돈 : \n{money}💰", value="\u200b", inline=True)
        embed.add_field(
            name=f"무릉 : \n{user['moorong']}층", value="\u200b", inline=True)
        embed.add_field(
            name=f"데미지 : \n{format(round(stat['power'],2),',')}", value='\u200b')
        embed.add_field(
            name=f"힘 : \n{format(stat['power_stat']+stat['power_else'],',')}({format(stat['power_stat'],',')}+{format(stat['power_else'],',')})", value='\u200b')
        # embed.add_field(
        #     name=f"데미지배수 : \nx{round(stat['damage'],2)}", value="\u200b")
        embed.add_field(
            name=f"체력 : \n{format(stat['hp'],',')}({format(stat['hp_stat'],',')}+{format(stat['hp']-stat['hp_stat'],',')})", value='\u200b')
        embed.add_field(
            name=f"중량 : \n{format(round(stat['str'],1),',')}({format(round(stat['str_stat'],1),',')}+{format(round(stat['str']-stat['str_stat'],1),',')})", value='\u200b')
        embed.add_field(
            name=f"크리티컬 확률 : \n{format(round(stat['crit']),',')}%", value='\u200b')
        embed.add_field(
            name=f"크리티컬 데미지 : \n{format(round(stat['crit_damage']*100),',')}({format(round(stat['crit_damage_stat']*100),',')}+{format(round(stat['crit_damage']*100-stat['crit_damage_stat']*100),',')})%", value='\u200b')
        embed.add_field(
            name=f"스텟 포인트 : {stat['point']}", value='\u200b', inline=False)
        embed.set_footer(text=f"생성일자 : {user['create_at']}")
        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await interaction.response.send_message("정보 로딩중...", ephemeral=True)
    await setting(interaction)


@tree.command(name="아이템정보", description="아이템정보")
async def items(interaction: Interaction, 유저: discord.Member = None):
    if not 유저:
        id = interaction.user.id
    else:
        id = 유저.id
    cur = con.cursor()
    cur.execute(
        "SELECT name,rank,upgrade,part FROM user_wear WHERE id = %s AND wear = 1", (id))
    user_item = cur.fetchall()
    cur.execute(
        "SELECT name,rank,upgrade FROM user_weapon WHERE id = %s AND wear = 1", (id))
    user_weapon = cur.fetchone()
    embed = discord.Embed(title="유저 아이템")
    embed.add_field(
        name=f"무기", value=f"{user_weapon[0]}[{user_weapon[1]}] +{user_weapon[2]}")
    for name, rank, upgrade, part in user_item:
        embed.add_field(name=f"{getPart(part)}",
                        value=f"{name}[{rank}] +{upgrade}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="인벤토리", description="인벤토리")
async def inventory(interaction: Interaction, 종류: makeItemEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    page = {}
    category: str = 종류.value
    page[interaction.user.id] = 0
    index = {}
    cur = con.cursor()

    async def next_callback(interaction: Interaction):  # 다음으로 버튼 클릭시
        page[interaction.user.id] += 1
        await setup(interaction)

    async def previous_callback(interaction: Interaction):  # 이전으로 버튼 클릭시
        page[interaction.user.id] -= 1
        await setup(interaction)

    async def detail_callback(interaction: Interaction):  # 선택완료시

        if category == "wear":  # 방어구일때
            # 해당 방어구 불러오기
            cur.execute(
                "SELECT item_id,name,upgrade,`rank`,level,power,hp,str,collection,part,wear,trade,url FROM user_wear WHERE id=%s ORDER BY item_id ASC LIMIT %s, 1",
                (interaction.user.id, page[interaction.user.id]*10+index[interaction.user.id]))
            wear: dict = makeDictionary(['item_id', 'name', 'upgrade', 'rank', 'level', 'power',
                                         'hp', 'str', 'collection', 'part', 'wear', 'trade', 'url'], cur.fetchone())
            # 현재 착용 중인 방어구 불러오기
            cur.execute(
                "SELECT power,hp,str FROM user_wear WHERE id=%s AND part=%s AND wear=1", (interaction.user.id, wear['part']))
            gap = {'power': 0, "hp": 0, "str": 0}
            check = cur.fetchone()
            if check:
                gap['power'] = check[0]
                gap['hp'] = check[1]
                gap['str'] = check[2]
            # 레벨 불러오기
            cur.execute("SELECT level FROM user_info WHERE id = %s",
                        interaction.user.id)
            level = cur.fetchone()[0]
            # embed 생성
            embed = discord.Embed(
                title=f"Lv.{wear['level']} {wear['name']}[{wear['rank']}] +{wear['upgrade']} ({'거래가능' if wear['trade'] else '거래불가'}) {'착용중' if wear['wear'] else ''}")
            embed.add_field(
                name=f"힘 : {format(wear['power'],',')}({'+' if wear['power']-gap['power']>0 else ''}{format(wear['power']-gap['power'],',')})", value="\u200b")
            embed.add_field(
                name=f"체력 : {format(wear['hp'],',')}({'+' if wear['hp']-gap['hp']>0 else ''}{format(wear['hp']-gap['hp'],',')})", value='\u200b')
            embed.add_field(
                name=f"중량 : {format(wear['str'],',')}({'+' if wear['str']-gap['str']>0 else ''}{format(wear['str']-gap['str'],',')})", value='\u200b')
            embed.add_field(
                name=f"착용부위 : {getPart(wear['part'])}", value='\u200b')
            embed.add_field(name=f"{wear['collection']} 세트", value='\u200b')
            embed.set_thumbnail(url=wear['url'])
            embed.set_footer(text=f"아이템 코드 : {wear['item_id']}")

        elif category == "weapon":  # 무기일때
            # 무기 불러오기
            cur.execute(
                "SELECT item_id,name,upgrade,`rank`,level,power,damage/100,`option`,wear,trade,url FROM user_weapon WHERE id = %s ORDER BY item_id ASC LIMIT %s,1 ",
                (interaction.user.id, page[interaction.user.id]*10+index[interaction.user.id]))
            weapon = makeDictionary(['item_id', 'name', 'upgrade', 'rank', 'level',
                                    'power', 'damage', 'option', 'wear', 'trade', 'url'], cur.fetchone())
            # 현재 착용중인 무기 불러오기
            cur.execute(
                "SELECT power,damage/100 FROM user_weapon WHERE id=%s AND wear=1", (interaction.user.id))
            gap = {'power': 0, "damage": 0}
            check = cur.fetchone()
            if check:
                gap['power'] = check[0]
                gap['damage'] = check[1]
            # 레벨 불러오기
            cur.execute("SELECT level FROM user_info WHERE id = %s",
                        interaction.user.id)
            level = cur.fetchone()[0]
            # embed 생성하기
            embed = discord.Embed(
                title=f"Lv.{weapon['level']} {weapon['name']}[{weapon['rank']}] +{weapon['upgrade']} ({'거래가능' if weapon['trade'] else '거래불가'}) {'착용중' if weapon['wear'] else ''}")
            embed.set_footer(text=f"아이템코드 : {weapon['item_id']}")
            embed.set_thumbnail(url=weapon['url'])
            embed.add_field(
                name=f"힘 : {format(weapon['power'],',')}({'+' if weapon['power']-gap['power']>0 else ''}{format(weapon['power']-gap['power'],',')})", value="\u200b")
            embed.add_field(
                name=f"데미지 : {round(weapon['damage'],2)}({'+' if weapon['damage']-gap['damage']>0 else ''}{format(round(weapon['damage']-gap['damage'],2),',')})", value='\u200b')
            embed.add_field(name=f"옵션 : {weapon['option']}", value='\u200b')

        elif category == "title":  # 칭호일때
            # 칭호 불러오기
            cur.execute(
                "SELECT item_id,name,`rank`,level,power,hp,`str`,crit,crit_damage/100,damage/100,wear,trade FROM user_title WHERE id = %s ORDER BY item_id ASC LIMIT %s,1 ",
                (interaction.user.id, page[interaction.user.id]*10+index[interaction.user.id]))
            title = makeDictionary(['item_id', 'name', 'rank', 'level', 'power', 'hp', 'str',
                                   'crit', 'crit_damage', 'damage', 'wear', 'trade'], cur.fetchone())
            # 현재 착용중인 칭호 불러오기
            cur.execute(
                "SELECT power,hp,`str`,crit,crit_damage,damage FROM user_title WHERE id = %s AND wear = 1", interaction.user.id)
            check = cur.fetchone()
            gap = {'power': 0, "hp": 0, "str": 0,
                   "crit": 0, "crit_damage": 0, "damage": 0}
            if check:
                gap['power'] = check[0]
                gap['hp'] = check[1]
                gap['str'] = check[2]
                gap['crit'] = check[3]
                gap['crit_damage'] = check[4]
                gap['damage'] = check[5]
            # 레벨 불러오기
            cur.execute("SELECT level FROM user_info WHERE id = %s",
                        interaction.user.id)
            level = cur.fetchone()[0]
            # embed 생성
            embed = discord.Embed(
                title=f"Lv.{title['level']} {title['name']}[{title['rank']}] ({'거래가능' if title['trade'] else '거래불가'}) {'착용중' if title['wear'] else ''}")
            embed.set_footer(text=f"아이템코드 : {title['item_id']}")
            for i in [{"name": "힘", "value": "power"}, {"name": "체력", "value": "hp"}, {"name": "중량", "value": "str"}, {"name": "크리티컬 확률", "value": "crit"}, {"name": "크리티컬 데미지", "value": "crit_damage"}, {"name": "데미지", "value": "damage"}]:
                if i['value'] == "crit_damage" or i['value'] == "damage":
                    value = round(title[i['value']]*100, 0)
                    display_value = format(value, ',')
                    embed.add_field(
                        name=f"{i['name']} : {f'{display_value}%'}({'+' if title[i['value']]-gap[i['value']]>0 else ''}{format(round(value-gap[i['value']],0),',')}%)", value="\u200b")
                elif i['value'] == "crit":
                    embed.add_field(
                        name=f"{i['name']} : {format(title[i['value']],',')}%({'+' if title[i['value']]-gap[i['value']]>0 else ''}{format(title[i['value']]-gap[i['value']],',')}%)", value="\u200b")

                else:
                    embed.add_field(
                        name=f"{i['name']} : {format(title[i['value']],',')}({'+' if title[i['value']]-gap[i['value']]>0 else ''}{format(title[i['value']]-gap[i['value']],',')})", value="\u200b")

        async def delete_callback(interaction: Interaction):
            class is_delete(ui.Modal, title="아이템버리기"):
                answer = ui.TextInput(
                    label="아이템을 정말로 버리겠습니까?", placeholder="아무 글자나 하나 적어주세요.", max_length=1)

                async def on_submit(self, interaction: Interaction):
                    if self.answer.value:
                        if category == "wear":
                            id = wear['item_id']
                        elif category == "weapon":
                            id = weapon['item_id']
                        elif category == "title":
                            id = title["item_id"]
                        cur.execute(
                            f"DELETE FROM user_{category} WHERE item_id=%s", (id))
                        con.commit()
                        await interaction.response.send_message("성공적으로 아이템이 삭제되었습니다.", ephemeral=True)
                        await asyncio.sleep(5)
                        await interaction.delete_original_response()
            await interaction.response.send_modal(is_delete())

        async def equip_callback(interaction: Interaction):  # 착용하기 버튼 클릭시
            if category == "wear":
                cur.execute("UPDATE user_wear SET wear = 0 WHERE part = %s AND wear = 1 AND id = %s",
                            (wear['part'], interaction.user.id))
                cur.execute(
                    "UPDATE user_wear SET wear = 1 WHERE item_id = %s", wear['item_id'])
            if category == "weapon":
                cur.execute("UPDATE user_weapon SET wear = 0 WHERE wear = 1 AND id = %s",
                            (interaction.user.id))
                cur.execute(
                    "UPDATE user_weapon SET wear = 1 WHERE item_id = %s", weapon['item_id'])
            if category == "title":
                cur.execute(
                    "UPDATE user_title SET wear = 0 WHERE wear =1 AND id = %s ", (interaction.user.id))
                cur.execute(
                    "UPDATE user_title SET wear = 1 WHERE item_id = %s", title['item_id'])
            con.commit()
            await detail_callback(interaction)
        # view 생성
        view = ui.View(timeout=None)
        # 레벨이 낮으면 착용불가 표시
        if category == "weapon":
            equip = ui.Button(label="착용하기", style=ButtonStyle.green,
                              disabled=level < weapon['level'])
        elif category == "wear":
            equip = ui.Button(label="착용하기", style=ButtonStyle.green,
                              disabled=level < wear['level'])
        elif category == "title":
            equip = ui.Button(label="착용하기", style=ButtonStyle.green,
                              disabled=level < title['level'])
        back = ui.Button(label="돌아가기")
        delete_button = ui.Button(label="버리기", style=ButtonStyle.red, row=2)
        view.add_item(equip)
        view.add_item(back)
        view.add_item(delete_button)
        equip.callback = equip_callback
        back.callback = setup
        delete_button.callback = delete_callback
        await interaction.response.edit_message(embed=embed, view=view)

    async def checkout_callback(interaction: Interaction):  # 선택하기 버튼 클릭시
        class checkoutModal(ui.Modal, title="아이템을 선택해주세요."):
            answer = ui.TextInput(
                label="번호", placeholder="현재 페이지 첫번째는 1입니다. 범위는 1~10까지만 가능합니다.", default=1, required=True, max_length=2)

            async def on_submit(self, interaction: Interaction, /):
                try:
                    value = int(self.answer.value[0])
                except:
                    pass
                else:
                    if value > 10:
                        pass
                    elif value <= 0:
                        pass
                    else:
                        index[interaction.user.id] = value-1
                        await detail_callback(interaction)
        await interaction.response.send_modal(checkoutModal())

    async def setup(interaction: Interaction):  # 유저 아이템 불러오는 함수
        embed = discord.Embed(title="인벤토리")
        cur.execute(
            f"SELECT COUNT(*) FROM {'user_'+category} WHERE id = %s", (interaction.user.id))
        count = cur.fetchone()[0]
        if category == "item":
            cur.execute("SELECT name,description,`rank`,price,trade,amount,item_id FROM user_item WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                        (interaction.user.id, page[interaction.user.id] * 10))
            for i in cur.fetchall():
                if i[5] > 0:
                    embed.add_field(
                        name=f"[{i[-1]}] {i[0]}[{i[2]}]({'거래가능' if i[4] else '거래불가'}) {i[5]}개", value=i[1], inline=False)
        elif category == "wear":
            cur.execute(
                "SELECT name,upgrade,`rank`,level,collection,part,wear,trade FROM user_wear WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                (interaction.user.id, page[interaction.user.id] * 10))
            for j, i in enumerate(cur.fetchall()):
                embed.add_field(
                    name=f"{j+1}. Lv.{i[3]} {i[0]}[{i[2]}] +{i[1]} ({'거래가능' if i[-1] else '거래불가'}) {'착용중' if i[-2] else ''}", value=f"{i[4]} 세트", inline=False)
        elif category == "title":
            cur.execute(
                "SELECT name,`rank`,level,wear,trade FROM user_title WHERE id = %s ORDER BY item_id ASC LIMIT %s,10", (interaction.user.id, page[interaction.user.id]*10))
            for j, i in enumerate(cur.fetchall()):
                embed.add_field(
                    name=f"{j+1}. Lv.{i[2]} {i[0]}[{i[1]}] ({'거래가능' if i[-1] else '거래불가'}) {'착용중' if i[-2] else ''}", value='\u200b', inline=False)
        else:
            cur.execute("SELECT name,upgrade,`rank`,level,wear,trade FROM user_weapon WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                        (interaction.user.id, page[interaction.user.id]*10))
            for j, i in enumerate(cur.fetchall()):
                embed.add_field(
                    name=f"{j+1}. Lv.{i[3]} {i[0]}[{i[2]}] +{i[1]} ({'거래가능' if i[-1] else '거래불가'}) {'착용중' if i[-2] else ''}", value='\u200b', inline=False)

        embed.set_footer(text=f"{page[interaction.user.id]+1} 페이지")
        view = ui.View(timeout=None)
        previous = ui.Button(
            label="이전으로", disabled=not page[interaction.user.id] > 0)
        next = ui.Button(label="다음으로", disabled=not (
            page[interaction.user.id]+1)*10 < count)
        reset = ui.Button(label="새로고침")
        view.add_item(previous)
        view.add_item(next)
        view.add_item(reset)
        if category != 'item':
            checkout = ui.Button(label="선택하기", style=ButtonStyle.green, row=2)
            view.add_item(checkout)
            checkout.callback = checkout_callback
        previous.callback = previous_callback
        next.callback = next_callback
        reset.callback = setup
        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await interaction.response.send_message("아이템을 가져오는 중입니다.", ephemeral=True)
    await setup(interaction)


@tree.command(name="채광초기화", description="채광이 버그가 나서 초기화가 필요할때 쓰세요.")
async def miningReset(interaction: Interaction, 아이디: int = 0):
    try:
        cnt[interaction.user.id]
    except KeyError:
        pass
    if cnt[interaction.user.id] > 0:  # 주간광산, 일간광산 등 특수던전 클리어 못했을 시
        if interaction.user.id == 432066597591449600:
            try:
                cnt[아이디]
            except:
                pass
            else:
                cnt[아이디] = -1
            cnt[interaction.user.id] = -1
            return await interaction.response.send_message("초기화 성공.", ephemeral=True)
        await interaction.response.send_message("초기화 할 수 없습니다.", ephemeral=True)
    else:
        mining_dic[interaction.user.id] = False
        await interaction.response.send_message("성공적으로 초기화 했습니다.", ephemeral=True)


@tree.command(name="무릉", description="무릉")
async def mooroong(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    floor = {}
    floor[interaction.user.id] = 1
    stat = getStatus(interaction.user.id)
    stat['power'] = round(stat['power'], 2)
    cur = con.cursor()

    async def go_callback(interaction: Interaction):  # 도전하기
        enemy = makeDictionary(['name', 'power', 'hp'], ("시련의 광석",
                               floor[interaction.user.id]*5, floor[interaction.user.id]*50))

        async def end_win_callback(interaction: Interaction):  # 전투 끝날때
            await interaction.response.edit_message(content="재정비...")
            await start(interaction)

        async def win(interaction: Interaction):  # 이겼을때
            embed = discord.Embed(title="승리!")
            view = ui.View(timeout=None)
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback

            view.add_item(end_win)
            floor[interaction.user.id] += 1
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def lose(interaction: Interaction):  # 졌을때
            embed = discord.Embed(
                title=f"기절했습니다. {floor[interaction.user.id]}층 도달.")
            cur.execute(
                "SELECT mooroong FROM user_info WHERE id = %s", interaction.user.id)
            if floor[interaction.user.id] > cur.fetchone()[0]:
                cur.execute("UPDATE user_info SET mooroong = %s WHERE id = %s",
                            (floor[interaction.user.id], interaction.user.id))
                con.commit()
            cur.close()
            try:
                await interaction.response.edit_message(content="", embed=embed, view=None)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(content="", embed=embed, view=None)

        async def attack_callback(interaction: Interaction):  # 공격했을때
            if getSuccess(stat['crit'], 100):
                enemy['hp'] -= stat['power']+stat['power']*stat['crit_damage']
                interaction.data['custom_id'] = 'True'
            else:
                enemy['hp'] -= stat['power']
                interaction.data['custom_id'] = "False"
            stat['hp'] -= enemy['power']
            if enemy['hp'] <= 0:
                if stat['hp'] >= enemy['hp']:
                    await win(interaction)
                else:
                    await lose(interaction)
            elif stat['hp'] <= 0:
                await lose(interaction)
            await try_callback(interaction)

        async def try_callback(interaction: Interaction):  # 도전하기
            enemyhp = format(enemy['hp'], ",")
            myhp = format(stat['hp'], ",")
            enemypower = format(enemy['power'], ",")
            mypower = format(round(stat['power'], 2), ",")

            embed = discord.Embed(title=enemy['name'])
            embed.add_field(name=f"{enemyhp}❤", value="\u200b")
            embed.add_field(name=f"{enemypower}⚡", value="\u200b")
            embed.add_field(name=f"나", value="\u200b", inline=False)
            embed.add_field(name=f"{myhp}❤", value='\u200b')
            embed.add_field(name=f"{mypower}⛏", value='\u200b')
            view = ui.View(timeout=None)
            attack = ui.Button(emoji="⛏", style=ButtonStyle.green)
            view.add_item(attack)
            attack.callback = attack_callback
            try:
                await interaction.response.edit_message(content="", embed=embed, view=view)
            except discord.errors.InteractionResponded:
                pass
        if stat['hp'] <= 0:
            return await lose(interaction)
        await try_callback(interaction)

    async def start(interaction: Interaction):  # 기본 정비 함수
        if stat['hp'] <= 0:
            return await go_callback(interaction)
        rest = discord.Embed(title="정비")
        rest.add_field(
            name=f"남은 체력 : {stat['hp']}", value="\u200b", inline=False)
        rest.add_field(
            name=f"현재 층 : {floor[interaction.user.id]}", value="\u200b", inline=False)
        view = ui.View(timeout=None)
        go = ui.Button(label="도전하기", emoji='⛏', style=ButtonStyle.green)
        go.callback = go_callback
        view.add_item(go)
        try:
            await interaction.response.send_message(embed=rest, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=rest, view=view)
    await start(interaction)


@tree.command(name="채광", description="채광")
async def mining(interaction: Interaction, 광산: miningEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    try:
        mining_dic[interaction.user.id]
    except KeyError:
        mining_dic[interaction.user.id] = True
    else:
        if mining_dic[interaction.user.id]:
            return await interaction.response.send_message("이미 광산에 들어와 있습니다.", ephemeral=True)
    cnt[interaction.user.id] = -1
    cur = con.cursor()
    if 광산.value <= 0:  # 특수 던전 일때
        utils = getJson('./json/util.json')
        if not useNotTradeFirst(utils[str(ticket[광산.value]['code'])]['name'], 1, interaction.user.id):
            mining_dic[interaction.user.id] = False
            return await interaction.response.send_message("입장권이 없습니다.", ephemeral=True)
        cnt[interaction.user.id] = ticket[광산.value]['cnt']
    stat = getStatus(interaction.user.id)
    stat['power'] = round(stat['power'], 2)
    adventrue_inventory[interaction.user.id] = makeDictionary(
        ['weight', 'items', 'names'], (0.0, [], []))

    async def remove_callback(interaction: Interaction):  # 아이템버리기
        view = ui.View(timeout=None)
        options = [SelectOption(
            label="뒤로가기", description="혹시 취소버튼을 눌렀다면 이걸 누르세요.", value="bug-bug-bug")]
        for item in adventrue_inventory[interaction.user.id]['items']:
            options.append(SelectOption(
                label=f"{item['name']} {item['amount']}개 ({item['price']*item['amount']}💰)",
                description=f"개당 중량 : {item['weight']} 총 중량 : {round(item['weight']*item['amount'],2)}",
                value=f"{item['name']}-{item['amount']}-{item['weight']}"
            ))
        options.append(SelectOption(
            label="모두 버리기", description="현재 보유중인 광석을 모두 버립니다.", value="all-all-all"))
        items = ui.Select(placeholder="버릴 아이템을 골라주세요.",
                          options=options, disabled=not len(options))
        view.add_item(items)
        rest = discord.Embed(title="정비")
        weight = abs(
            round(adventrue_inventory[interaction.user.id]['weight'], 2))
        disabled = round(stat['str'], 2) < weight-0.001

        rest.add_field(
            name=f"가방(용량:{weight}/{round(stat['str'],2)})", value="\u200b",)
        rest.add_field(name=광산.name, value='\u200b', inline=False)
        if disabled:
            rest.set_footer(text="가방이 너무 무겁습니다!")
        if cnt[interaction.user.id] >= 0:
            rest.add_field(
                name=f"남은 횟수 : {cnt[interaction.user.id]}", value='\u200b')
            if cnt[interaction.user.id] == 0:
                rest.set_footer(text="횟수가 없습니다!")

        async def item_remove_callback(interaction: Interaction):
            name, amount, weight = items.values[0].split("-")
            if name == "bug":
                await interaction.response.edit_message(content="버그가 고쳐졌습니다.")
                return await start(interaction)
            if name == "all":
                adventrue_inventory[interaction.user.id]['items'] = []
                adventrue_inventory[interaction.user.id]['names'] = []
                adventrue_inventory[interaction.user.id]['weight'] = 0
                await interaction.response.edit_message(content="모든 광석을 버렸습니다.")
                return await start(interaction)

            class amountModal(ui.Modal, title=f"{name} {amount}개"):
                answer = ui.TextInput(
                    label="개수", placeholder="제거할 개수를 선택해주세요.", required=True, default=amount)

                async def on_submit(self, interaction: Interaction):
                    try:
                        int(self.answer.value)
                    except:
                        pass
                    if int(self.answer.value) > int(amount) or int(self.answer.value) < 0:
                        pass
                    else:
                        adventrue_inventory[interaction.user.id]['weight'] -= int(
                            self.answer.value)*float(weight)
                        for i in adventrue_inventory[interaction.user.id]['items']:
                            if i['name'] == name:
                                i['amount'] -= int(self.answer.value)
                                if i['amount'] == 0:
                                    adventrue_inventory[interaction.user.id]['items'].remove(
                                        i)
                                    adventrue_inventory[interaction.user.id]['names'].remove(
                                        name)
                                break
                        await interaction.response.edit_message(content=f"{name}을 {self.answer.value}개 버렸습니다.\n중량 -{round(int(self.answer.value)*float(weight),3)}")
                        await remove_callback(interaction)
            await interaction.response.send_modal(amountModal())
        items.callback = item_remove_callback
        try:
            await interaction.response.edit_message(view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(embed=rest, view=view)

    async def go_callback(interaction: Interaction):  # 탐험진행
        cnt[interaction.user.id] -= 1
        cur.execute(
            "SELECT name,power,hp,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,url FROM enemy WHERE floor=%s ORDER BY RAND() LIMIT 1", 광산.value)
        enemy = makeDictionary(['name', 'power', 'hp', 'exp', 'item_code', "item_percent",
                               "item_amount", "util_code", "util_percent", "util_amount", "url"], cur.fetchone())
        stat['hp'] = stat['maxhp']

        async def run_callback(interaction: Interaction):  # 도망치기
            await interaction.response.edit_message(content="도망쳤습니다.")
            return await start(interaction)

        async def end_win_callback(interaction: Interaction):  # 전투 끝날때
            await interaction.response.edit_message(content="재정비...")
            await start(interaction)

        async def win(interaction: Interaction):  # 이겼을때
            util_data = getJson('./json/util.json')
            stone_data = getJson('./json/stone.json')
            util_code = enemy['util_code'].split(" ")
            util_percent = enemy['util_percent'].split(" ")
            util_amount = enemy['util_amount'].split(" ")
            item_code = enemy['item_code'].split(" ")
            item_percent = enemy['item_percent'].split(" ")
            item_amount = enemy['item_amount'].split(" ")
            cur.execute("UPDATE user_info SET exp = exp + %s WHERE id = %s",
                        (enemy['exp'], interaction.user.id))
            con.commit()
            cur.execute(
                "SELECT rebirth,level,exp FROM user_info WHERE id = %s", interaction.user.id)
            rebirth, level, exp = cur.fetchone()
            num = is_levelup(rebirth, level, exp, interaction.user.id)
            embed = discord.Embed(title="보상 요약")
            embed.add_field(
                name=f"{format(int(enemy['exp']),',')} 경험치를 획득했습니다.", value="\u200b", inline=False)
            if num and num != -1:
                if num == MAX_LEVEL+1:
                    embed.add_field(
                        name=f"{rebirth+1}차 환생이 되었습니다.", value='\u200b', inline=False)
                else:
                    embed.add_field(
                        name=f"{level+num} 레벨이 되었습니다.", value="\u200b", inline=False)
            view = ui.View(timeout=None)
            embed.add_field(name="광석 :", value='\u200b', inline=False)
            for i in range(len(item_percent)):
                if getSuccess(float(item_percent[i]), 100):
                    stone: dict = stone_data[item_code[i]]
                    min, max = item_amount[i].split("~")
                    total = random.randint(int(min), int(max))
                    if stone['name'] in adventrue_inventory[interaction.user.id]['names']:
                        for i in adventrue_inventory[interaction.user.id]['items']:
                            if i['name'] == stone['name']:
                                i['amount'] += total
                                adventrue_inventory[interaction.user.id]['weight'] += total * \
                                    stone['weight']
                                break
                    else:
                        stone.update({"amount": total})
                        adventrue_inventory[interaction.user.id]['items'].append(
                            stone)
                        adventrue_inventory[interaction.user.id]['weight'] += total * \
                            stone['weight']
                        adventrue_inventory[interaction.user.id]['names'].append(
                            stone['name'])
                    embed.add_field(
                        name=f"{stone['name']} {total}개 획득!", inline=False, value="\u200b")
            embed.add_field(name="기타 :", value='\u200b', inline=False)
            for i in range(len(util_percent)):
                if getSuccess(float(util_percent[i]), 100):
                    util: dict = util_data[util_code[i]]
                    isExistItem(interaction.user.id, util_code[i])
                    min, max = util_amount[i].split("~")
                    total = random.randint(int(min), int(max))
                    cur.execute(
                        "UPDATE user_item SET amount = amount + %s WHERE id = %s AND item_id = %s", (total, interaction.user.id, util_code[i]))
                    con.commit()
                    embed.add_field(
                        name=f"{util['name']} {total}개 획득!", inline=False, value="\u200b")
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback
            view.add_item(end_win)
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def lose(interaction: Interaction):  # 졌을때
            embed = discord.Embed(title="기절했습니다.")
            embed.add_field(
                name="/스텟 명령어\n/강화 명령어\n/제작소 명령어\n등으로 강해질 수 있습니다.", value='\u200b', inline=False)
            for i in adventrue_inventory[interaction.user.id]['items']:
                total = random.randint(0, i['amount'])
                i['amount'] -= total
                adventrue_inventory[interaction.user.id]['weight'] -= total*i['weight']
                if i['amount'] <= 0:
                    adventrue_inventory[interaction.user.id]['names'].remove(
                        i['name'])
                    adventrue_inventory[interaction.user.id]['items'].remove(i)
                if total > 0:
                    embed.add_field(
                        name=f"{i['name']}을 {total}개 잃어버렸습니다..", value="\u200b", inline=False)
            view = ui.View(timeout=None)
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback
            view.add_item(end_win)
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def attack_callback(interaction: Interaction):  # 공격했을때
            if getSuccess(stat['crit'], 100):
                interaction.data["custom_id"] = "True"
                enemy['hp'] -= stat['power']+stat['power']*stat['crit_damage']
            else:
                interaction.data["custom_id"] = "False"
                enemy['hp'] -= stat['power']
            stat['hp'] -= enemy['power']
            if enemy['hp'] <= 0:
                if stat['hp'] >= enemy['hp']:
                    await win(interaction)
                else:
                    await lose(interaction)
            elif stat['hp'] <= 0:
                await lose(interaction)
            await try_callback(interaction)

        async def try_callback(interaction: Interaction):  # 도전하기
            enemyhp = format(round(enemy['hp'], 2), ",")
            enemypower = format(enemy['power'], ",")
            mypower = format(round(stat['power']), ",")
            myhp = format(stat['hp'], ",")
            embed = discord.Embed(title=enemy['name'])
            embed.add_field(name=f"{enemyhp}❤", value="\u200b")
            embed.add_field(name=f"{enemypower}⚡", value="\u200b")
            embed.add_field(name=f"나", value="\u200b", inline=False)
            embed.add_field(name=f"{myhp}❤", value='\u200b')
            embed.add_field(name=f"{mypower}⛏", value='\u200b')
            if interaction.data['custom_id'] == "True":
                embed.add_field(name="크리티컬!", value='\u200b', inline=False)
            embed.set_thumbnail(url=enemy['url'])
            view = ui.View(timeout=None)
            attack = ui.Button(emoji="⛏", style=ButtonStyle.green)
            view.add_item(attack)
            attack.callback = attack_callback
            try:
                await interaction.response.edit_message(content="", embed=embed, view=view)
            except discord.errors.InteractionResponded:
                pass

        async def meet_enemy():  # 적과 만났을때
            embed = discord.Embed(title=enemy['name'])
            hp = format(enemy['hp'])
            embed.add_field(name=f"{hp}❤", value="\u200b")
            embed.add_field(name=f"{enemy['power']}⚡", value="\u200b")
            embed.set_image(url=enemy['url'])
            view = ui.View(timeout=None)
            try_button = ui.Button(
                label='도전하기', emoji='⛏', style=ButtonStyle.green)
            run_button = ui.Button(
                label='도망치기', emoji="👟", style=ButtonStyle.red)
            view.add_item(try_button)
            view.add_item(run_button)
            try_button.callback = try_callback
            run_button.callback = run_callback
            await interaction.response.edit_message(embed=embed, view=view)
        await meet_enemy()

    async def stop_callback(interaction: Interaction):  # 탐험중단
        embed = discord.Embed(title="탐험 요약")
        result = 0
        for i in adventrue_inventory[interaction.user.id]['items']:
            result += i['amount']*i['price']
            embed.add_field(name=i['name'], value=f"{i['amount']}개")
        embed.set_footer(text=f"예상 수익 : {result}골드")
        cur.execute("UPDATE user_info SET money = money + %s WHERE id = %s",
                    (result, interaction.user.id))
        cur.close()
        con.commit()
        mining_dic[interaction.user.id] = False
        await interaction.response.edit_message(content="", embed=embed, view=None)
        await asyncio.sleep(4)
        return await interaction.delete_original_response()

    async def start(interaction: Interaction):  # 기본 정비 함수
        rest = discord.Embed(title="정비")
        weight = abs(
            round(adventrue_inventory[interaction.user.id]['weight'], 2))
        disabled = round(stat['str'], 2) < weight-0.001

        rest.add_field(
            name=f"가방(용량:{weight}/{round(stat['str'],2)})", value="\u200b",)
        rest.add_field(name=광산.name, value='\u200b', inline=False)
        if disabled:
            rest.set_footer(text="가방이 너무 무겁습니다!")
        if cnt[interaction.user.id] >= 0:
            rest.add_field(
                name=f"남은 횟수 : {cnt[interaction.user.id]}", value='\u200b')
            if cnt[interaction.user.id] == 0:
                rest.set_footer(text="횟수가 없습니다!")

        view = ui.View(timeout=None)
        remove = ui.Button(label="아이템버리기", emoji="🗑", style=ButtonStyle.gray,
                           disabled=(weight == 0.0), row=2)
        go = ui.Button(label="탐험진행", emoji='⛏',
                       disabled=disabled or cnt[interaction.user.id] == 0, style=ButtonStyle.green)
        stop = ui.Button(label="탐험중단", emoji="💨",
                         disabled=disabled, style=ButtonStyle.red)
        remove.callback = remove_callback
        go.callback = go_callback
        stop.callback = stop_callback
        for i in [remove, go, stop]:
            view.add_item(i)
        try:
            await interaction.response.send_message(embed=rest, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=rest, view=view)
    await start(interaction)
client.run(os.environ['token'])
