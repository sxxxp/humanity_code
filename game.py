from PIL import Image, ImageFont, ImageDraw
import pymysql
import os
from discord import Interaction, ui, ButtonStyle, app_commands
from discord.ext import tasks
import discord
import datetime
import json
import math
import asyncio
import random
from enum import Enum
from dotenv import load_dotenv
import io
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
    wear = makeDictionary(
        ['power', 'hp', 'str', 'def', 'mana'], cur.fetchone())
    cur.execute("""SELECT SUM(A.hp),SUM(A.power),SUM(A.str),SUM(A.def),SUM(A.mana),SUM(A.avoid),SUM(A.crit),SUM(A.crit_damage/100),SUM(A.damage/100) FROM
                collection_effect A JOIN (SELECT collection as col,COUNT(collection) as cnt FROM user_wear WHERE wear=1 AND id=%s GROUP BY collection) B
                ON B.col = A.collection WHERE B.cnt>=A.value""", id)
    collection = makeDictionary(
        ['hp', 'power', 'str', 'def', 'nama', 'avoid', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT SUM(hp), SUM(power),SUM(`str`),SUM(def),SUM(mana),SUM(avoid),SUM(crit),SUM(crit_damage/100),SUM(damage/100) FROM user_title WHERE id = %s AND wear = 1", id)
    title = makeDictionary(
        ['hp', 'power', 'str', 'def', 'mana', 'avoid', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT power,damage/100,`option`,mana FROM user_weapon WHERE id=%s AND wear = 1", id)
    weapon = makeDictionary(
        ['power', 'damage', 'option', 'mana'], cur.fetchone())
    if weapon:
        option = getOption(weapon['option'])
    else:
        option = {}
    cur.execute(
        "SELECT power,hp*5,str/10,crit,crit_damage/50,mana*2,avoid,point FROM user_stat WHERE id=%s", id)
    stat = makeDictionary(['power', 'hp', 'str', 'crit',
                          'crit_damage', 'mana', 'avoid', 'point'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0, 'def': 0, 'damage': 0, 'crit': 0, 'mana': 0, 'avoid': 0,
             'crit_damage': 0, 'maxhp': 0, 'point': 0}
    for key, value in chain(wear.items(), weapon.items(), option.items(), stat.items(), collection.items(), title.items()):
        if value:
            final[key] += value
    final['maxhp'] = final['hp']
    final['cur_power'] = final['power']
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
    cur.execute("SELECT name FROM user_title WHERE id = %s AND wear = 1", id)
    title = cur.fetchone()
    if title:
        info['title'] = title
    else:
        info['title'] = "칭호없음"
    return info


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
        draw.text((740, 355), str(
            self.stat['cur_def']), anchor="mm", font=level_font)
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
            await interaction.response.send_message(file=discord.File(fp=image_binary, filename="userInfo.png"), ephemeral=True)

    async def getExp(self, exp: int = 0):
        cur = con.cursor()
        cur.execute(
            "UPDATE user_info SET exp = exp + %s WHERE id = %s", (exp*EXP_EARN, self.id))
        cur.execute(
            "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = exp ", (exp*EXP_EARN, self.id))
        self.userInfo['exp'] += exp*EXP_EARN
        await self.is_levelup()
        con.commit()
        cur.close()

    async def getMoney(self, money: int = 0):
        cur = con.cursor()
        cur.execute(
            "UPDATE user_info SET money = money + %s WHERE id = %s", (money*MONEY_EARN, self.id))
        if money > 0:
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type` = 'get' AND code = 'money'", (money*MONEY_EARN, self.id))
        else:
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND `type`= spend AND code = 'money'", (-money, self.id))
        self.userInfo['money'] += money*EXP_EARN
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

    async def getItem(self, code: int, cnt: int):
        '''
        cnt 개 만큼 아이템 code에 담기
        ----------------------------
        - code: 아이템 코드
        - id: 유저 아이디
        - cnt: 넣을 아이템 갯수
        '''

        cur = con.cursor()
        await self.isExistItem(code)
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s AND id = %s", (cnt, code, self.id))
        if cnt > 0:
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

    async def isExistItem(self, code: int):
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
            utils[str(code)]
        except:
            return -1
        cur.execute(  # code에 해당하는 아이템이 있는지 확인
            "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (self.id, code))
        amount = cur.fetchone()
        if not amount:  # 없으면 아이템 insert
            cur.execute("INSERT INTO user_item VALUES(%s,%s,%s)",
                        (code, 0, self.id))
            con.commit()
            cur.close()
            return 0
        else:
            cur.close()
            return int(amount[0])

    async def is_levelup(self):
        '''
        레벨업 했을때
        ------------

        `return 레벨업한 숫자`
        '''
        if self.userInfo['rebirth'] == MAX_REBIRTH:
            return 0
        level_info = getJson('./json/level.json')
        num = 0
        cur = con.cursor()
        while level_info[str(self.userInfo['rebirth'])][str(self.userInfo['level']+num)] <= self.userInfo['exp']:
            self.userInfo['exp'] -= level_info[str(
                self.userInfo['rebirth'])][str(self.userInfo['level']+num)]
            num += 1
            if self.userInfo['level']+num >= MAX_LEVEL+1 and self.userInfo['rebirth'] != MAX_REBIRTH:
                cur.execute(
                    "UPDATE user_info SET exp = %s, rebirth=rebirth+1 WHERE id = %s", (self.userInfo['exp'], self.id))
                cur.execute(
                    "UPDATE user_stat SET point = point + %s WHERE id = %s", (STAT_PER_REBIRTH, self.id))
                self.getItem(8, 1)
                cur.close()
                con.commit()
                return MAX_LEVEL+1
        if num > 0:
            cur.execute(
                "UPDATE user_info SET level = level + %s , exp = %s WHERE id = %s", (num, self.userInfo['exp'], self.id))
            cur.execute(
                "UPDATE user_stat SET point = point + %s WHERE id = %s", (num*STAT_PER_LEVEL, self.id))
        cur.close()
        con.commit()

        return num


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

    def __init__(self, user: User, floor: int, interaction: Interaction):
        self.floor = floor
        self.user = user
        self.user.effect = {'🗡': 3, '🩸': 2, '🩹': 4}
        self.interaction = interaction
        self.exp = 0
        self.inventory = {'util': {}, 'use': {}, 'stone': {}}
        self.cnt = -1

    async def validity(self):
        if self.user.where:
            await self.interaction.response.send_message(f"이미 {self.user.where}에 있어요!", ephemeral=True)
        elif await self.haveTicket():
            self.user.where = "광산"
            await self.interaction.response.send_message("광산에 진입중...!", ephemeral=True)
            await self.setup(self.interaction)
        else:
            await self.interaction.response.send_message(f"**{util[str(Mining.ticket[self.floor]['code'])]['name']}**이 없습니다.", ephemeral=True)

    async def haveTicket(self):
        if self.floor in Mining.ticket.keys():
            floor = Mining.ticket[self.floor]
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
        def __init__(self, parent):
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
                if getSuccess(int(percent[i]), 100):
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
                if getSuccess(int(percent[i]), 100):
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
                    self.parent.enemy['hp'] -= damage * \
                        (1+self.parent.user.stat['crit_damage'])
                    text += f"**크리티컬!!!** **{round(damage * (1+self.parent.user.stat['crit_damage']),2)}** 피해를 입혔습니다!\n"
                else:
                    self.parent.enemy['hp'] -= damage
                    text += f"**{damage}** 피해를 입혔습니다!\n"

            else:
                text += f"적이 **회피** 했습니다!\n"
            if not getSuccess(self.parent.user.stat['avoid'], 100):
                e_damage = self.parent.enemy['power'] * \
                    (self.parent.enemy['damage'])
                self.parent.user.stat['hp'] -= e_damage
                text += f"**{round(e_damage,2)}** 피해를 받았습니다!\n"
            else:
                text += "공격을 **회피** 했습니다!\n"
            return text

        async def handle_win(self, interaction: Interaction):
            if self.parent.user.stat['hp'] <= 0:
                if self.parent.user.stat['hp'] >= self.parent.enemy['hp']:
                    return await self.win(interaction)
                else:
                    return await self.lose(interaction)
            if self.parent.enemy['hp'] <= 0:
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
        def __init__(self, parent):
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
        def __init__(self, parent):
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
                print(total_price, data, stone[item]['price'])
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
                    exp_text += f"{self.parent.user.userInfo['rebirth']+1}차 환생 달성!"
                else:
                    exp_text += f"{level+self.parent.user.userInfo['level']}레벨 달성!"
            embed.add_field(name=f"{exp_text}", value='\u200b', inline=False)
            stones, total_price = await self.stone_price()
            stone_text = ''
            for name, amount, price in stones:
                stone_text += f"**{name} {amount}**개 가격 **{price*amount*MONEY_EARN}({price}x{amount}x{MONEY_EARN})**\n"
            if stone_text:
                stone_text += f"\n**총 가격 {total_price*MONEY_EARN}({total_price}x{MONEY_EARN})**"
                embed.add_field(name="광석", value=stone_text, inline=False)
                await self.parent.user.getMoney(total_price)
            util_text = ''
            for key, value in self.parent.inventory['util'].items():
                util_text += f"{util[key]['name']} {value}개 획득!\n"
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

        @ui.button(label="아이템버리기", emoji="🗑", row=2, style=ButtonStyle.gray)
        async def throwItem(self, interaction: Interaction, button: ui.Button):
            pass

        def end_button(self):
            button = ui.Button(label="돌아가기", emoji="🏠",
                               row=2, style=ButtonStyle.danger, disabled=self.parent.stone_result() > self.parent.user.stat['str'])

            async def end(interaction: Interaction):
                self.parent.user.where = ''
                embed = await self.endEmbed()
                await interaction.response.edit_message(embed=embed, view=None)
                await asyncio.sleep(10)
                await interaction.delete_original_response()
            button.callback = end
            self.add_item(button)

    async def make_enemy(self):
        cur = con.cursor()
        cur.execute(
            "SELECT percent FROM enemy WHERE floor = %s", self.floor)
        percent = cur.fetchall()
        percent = [value[0] for value in percent]
        idx = checkSuccess(percent)
        if idx == -1:
            embed = discord.Embed(title=miningEnum(self.floor).name)
            embed.add_field(name="아무것도 만나지 못했습니다.",
                            value="\u200b", inline=False)
            await self.interaction.edit_original_response(embed=embed, view=None)
            await asyncio.sleep(3)
            await self.setup()
        else:
            cur.execute(
                "SELECT name,power,hp,def,avoid,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,use_code,use_percent,use_amount,url FROM enemy WHERE floor = %s  LIMIT %s, 1", (self.floor, idx))
            self.enemy = makeDictionary(['name', 'power', 'hp', 'def', 'avoid', 'exp', 'item_code', 'item_percent',
                                        'item_amount', 'util_code', 'util_percent', 'util_amount', 'use_code', 'use_percent', 'use_amount', 'url'], cur.fetchone())
            self.enemy['damage'] = 1
            self.enemy['maxhp'] = self.enemy['hp']
            self.enemy['effect'] = {}

    async def setup(self, interaction: Interaction):
        embed = discord.Embed(title=miningEnum(self.floor).name)
        if self.user.stat['hp'] < 0:
            self.user.stat['hp'] = 0
            embed.set_footer(text="체력이 없습니다!")
        embed.add_field(
            name=f"중량: {round(self.stone_result(),2)}/{self.user.stat['str']}\n❤{ round(self.user.stat['hp'],2)}", value='\u200b', inline=False)
        embed.add_field(name=f"얻은 경험치 : {self.exp}",
                        value="\u200b", inline=False)
        if self.cnt >= 0:
            embed.add_field(name=f"남은 탐험 기회 : {self.cnt}")
            if self.cnt == 0:
                embed.set_footer(text="탐험 기회가 없습니다!")
        if self.stone_result() > self.user.stat['str']:
            embed.set_footer(text="무게가 너무 무겁습니다!")
        try:
            await interaction.response.edit_message(content="", embed=embed, view=self.setupView(self))
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=self.setupView(self))


@tree.command(name="정보", description="정보")
async def info(interaction: Interaction):
    await User(interaction.user.id).Info(interaction)


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


@tree.command(name="채광", description="채광")
async def mining(interaction: Interaction, 광산: miningEnum):
    mine = Mining(User(interaction.user.id), 광산.value, interaction)
    await mine.validity()
client.run(os.environ['token'])
