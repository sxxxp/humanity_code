from PIL import Image, ImageFont, ImageDraw
import pymysql
import os
from discord import Interaction, ui, ButtonStyle, app_commands
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
        "SELECT SUM(power),SUM(hp),SUM(str/10),SUM(def) FROM user_wear WHERE id=%s AND wear = 1 ", id)
    wear = makeDictionary(['power', 'hp', 'str', 'def'], cur.fetchone())
    cur.execute("""SELECT SUM(A.hp),SUM(A.power),SUM(A.str),SUM(A.def),SUM(A.crit),SUM(A.crit_damage/100),SUM(A.damage/100) FROM
                collection_effect A JOIN (SELECT collection as col,COUNT(collection) as cnt FROM user_wear WHERE wear=1 AND id=%s GROUP BY collection) B
                ON B.col = A.collection WHERE B.cnt>=A.value""", id)
    collection = makeDictionary(
        ['hp', 'power', 'str', 'def', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT SUM(hp), SUM(power),SUM(`str`),SUM('def'),SUM(crit),SUM(crit_damage/100),SUM(damage/100) FROM user_title WHERE id = %s AND wear = 1", id)
    title = makeDictionary(
        ['hp', 'power', 'str', 'def', 'crit', 'crit_damage', 'damage'], cur.fetchone())
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
                          'crit_damage'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0, 'def': 0, 'damage': 0, 'crit': 0,
             'crit_damage': 0, 'maxhp': 0}
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
    cur.close()
    final['str'] = float(final['str'])
    final['crit_damage'] = float(final['crit_damage'])

    print(final)
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
        print("로그인!")


intents = discord.Intents.all()
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)


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


async def isActive(interaction: Interaction):
    await interaction.response.send_message("")


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
        draw.text((585, 385), format(
            int(self.stat['cur_power']), ','), anchor="mm", font=power_font)
        draw.text((740, 385), str(
            self.stat['cur_def']), anchor="mm", font=level_font)
        hp_font = ImageFont.truetype(
            "malgunbd.ttf", 40-len(str(self.stat['maxhp'])))
        draw.text((895, 385), format(
            self.stat['maxhp'], ','), anchor="mm", font=hp_font)
        draw.text(
            (585, 530), f"{self.stat['crit']}%", anchor="mm", font=level_font)
        draw.text(
            (740, 530), f"{int(self.stat['crit_damage']*100)}%", anchor="mm", font=level_font)
        draw.text(
            (895, 530), f"{int(self.stat['cur_damage']*100)}%", anchor="mm", font=level_font)
        user_avater = interaction.user.display_avatar.with_size(256)
        data = io.BytesIO(await user_avater.read())
        user_avater = Image.open(data)
        image.paste(im=user_avater, box=(130, 200, 130+256, 200+256))
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.response.send_message(file=discord.File(fp=image_binary, filename="userInfo.png"), ephemeral=True)

    def getExp(self, exp: int):
        cur = con.cursor()
        cur.execute(
            "UPDATE user_info SET exp = exp + %s WHERE id = %s", (exp, self.id))
        cur.execute(
            "UPDATE quest SET now = now + %s WHERE id = %s AND type = get AND code = exp ", (exp, self.id))
        self.userInfo['exp'] += exp
        self.is_levelup()
        con.commit()
        cur.close()

    def getMoney(self, money: int):
        cur = con.cursor()
        cur.execute(
            "UPDATE user_info SET money = money + %s WHERE id = %s", (money, self.id))
        if money > 0:
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND type = get AND code = money", (money, self.id))
        self.userInfo['money'] += money
        con.commit()
        cur.close()

    def getItem(self, code: int, cnt: int):
        '''
        cnt 개 만큼 아이템 code에 담기
        ----------------------------
        - code: 아이템 코드
        - id: 유저 아이디
        - cnt: 넣을 아이템 갯수
        '''

        cur = con.cursor()
        self.isExistItem(code)
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s AND id = %s", (cnt, code, self.id))
        if cnt > 0:
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND type = get AND code = item", (cnt, self.id))
            cur.execute(
                "UPDATE quest SET now = now + %s WHERE id = %s AND type = get AND code = %s", (cnt, self.id, code))
        con.commit()
        cur.close()

    def setItem(self, code: int, cnt: int):
        '''
        아이템 code를 cnt값으로 바꾸기
        ----------------------------
        - code: 아이템 코드
        - id: 유저 아이디
        - cnt: 넣을 아이템 갯수
        '''
        cur = con.cursor()
        self.isExistItem(self.id, code)
        cur.execute(
            "UPDATE user_item SET amount = %s WHERE item_id = %s AND id = %s", (cnt, code, self.id))
        con.commit()
        cur.close()

    def isExistItem(self, code: int):
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

    def is_levelup(self):
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
        self.user.effect = {'🗡': 3, '🩸': 2}
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
            amount = self.user.isExistItem(floor['code'])
            if amount >= floor['value']:
                self.user.getItem(floor['code'], -floor['value'])
                self.cnt = floor['cnt']
                return True
            else:
                return False
        return True

    def stone_result(self):
        total_weight = 0
        for item, data in self.inventory['stone'].items():
            total_weight += data["amount"] * data["weight"]
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
                dam = maxhp/20
                if name == 'user':
                    self.parent.user.stat['hp'] -= dam
                else:
                    self.parent.enemy['hp'] -= dam
                return 'dam', -dam
            if effect == "🗡":
                damage = 0.1
                if name == 'user':
                    self.parent.user.stat['damage'] += damage
                else:
                    self.parent.enemy['damage'] += damage
                return 'damage', damage
            return 'None', None

        async def handel_effect(self):
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
            self.parent.user.effect = {
                key: value for key, value in self.parent.user.effect.items() if value != 0}
            for item, data in self.parent.enemy['effect'].items():
                self.parent.enemy['effect'][item] -= 1
                effect_type, value = await self.classify_effect(item, 'enemy')
                if effect_type == 'damage':
                    text += f"{item} 데미지가 상승합니다. **+{value}%**\n"
                if effect_type == 'dam':
                    text += f"{item} 데미지를 입습니다. **-{value}**\n"
            self.parent.enemy['effect'] = {
                key: value for key, value in self.parent.enemy['effect'].items() if value != 0}
            return text

        @ui.button(label="⛏", row=1, style=ButtonStyle.green)
        async def attack(self, interaction: Interaction, button: ui.Button):
            text = await self.handel_effect()
            damage = self.parent.user.stat['power'] * \
                self.parent.user.stat['damage']
            if getSuccess(self.parent.user.stat['crit'], 100):
                self.parent.enemy['hp'] -= damage * \
                    (1+self.parent.user.stat['crit_damage'])
                text += f"**크리티컬!!!** **{round(damage * (1+self.parent.user.stat['crit_damage']),2)}** 피해를 입혔습니다!\n"
            else:
                self.parent.enemy['hp'] -= damage
                text += f"**{damage}** 피해를 입혔습니다!\n"
            e_damage = self.parent.enemy['power'] * \
                (self.parent.enemy['damage'])
            self.parent.user.stat['hp'] -= e_damage
            text += f"**{round(e_damage,2)}** 피해를 받았습니다!\n"
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
        embed.add_field(
            name=self.enemy['name'],
            value=f"""
            ❤ **{round(self.enemy['hp'],2)}**
            ⚡ **{self.enemy['power']}**
            🗡 **{round(self.enemy['damage'],2)}**
            🛡 **{self.enemy['def']}**
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

        @ui.button(label="채광하러가기", emoji="⛏", row=1, style=ButtonStyle.green)
        async def go(self, interaction: Interaction, button: ui.Button):
            await self.parent.make_enemy()
            self.parent.enemy['effect'] = {}
            enemy = self.parent.enemy
            embed = discord.Embed(title=enemy['name'])
            embed.add_field(
                name=f"⚡{enemy['power']}\n❤{enemy['hp']}\n🛡{enemy['def']}", value='\u200b')
            embed.set_thumbnail(url=enemy['url'])
            await interaction.response.edit_message(embed=embed, view=self.parent.meetView(self.parent))

        @ui.button(label="회복하기", emoji="🩹", row=1, style=ButtonStyle.red)
        async def heal(self, interaction: Interaction, button: ui.Button):
            self.parent.user.stat['hp'] = self.parent.user.stat['maxhp']
            await self.parent.setup(interaction)

        @ui.button(label="아이템버리기", emoji="🗑", row=2, style=ButtonStyle.gray, disabled=True)
        async def throwItem(interaction: Interaction, button: ui.Button):
            pass

        @ui.button(label="돌아가기", emoji="🏠", row=2, style=ButtonStyle.danger)
        async def back(self, interaction: Interaction, button: ui.Button):
            self.parent.user.where = ''
            await interaction.response.edit_message(content="돌아갔습니다.", embed=None, view=None)
            await interaction.delete_original_response()

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
                "SELECT name,power,hp,def,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,url FROM enemy WHERE floor = %s  LIMIT %s, 1", (self.floor, idx))
            self.enemy = makeDictionary(['name', 'power', 'hp', 'def', 'exp', 'item_code', 'item_percent',
                                        'item_amount', 'util_code', 'util_percent', 'util_amount', 'url'], cur.fetchone())
            self.enemy['damage'] = 1
            self.enemy['maxhp'] = self.enemy['hp']

    async def setup(self, interaction: Interaction):
        embed = discord.Embed(title=miningEnum(self.floor).name)
        embed.add_field(
            name=f"중량: {self.stone_result()}/{self.user.stat['str']}\n❤{ round(self.user.stat['hp'],2)}", value='\u200b', inline=False)
        if self.cnt >= 0:
            embed.add_field(name=f"남은 탐험 기회 : {self.cnt}")
        try:
            await interaction.response.edit_message(content="", embed=embed, view=self.setupView(self))
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=self.setupView(self))


@tree.command(name="정보", description="정보")
async def info(interaction: Interaction):
    await User(interaction.user.id).Info(interaction)


@tree.command(name="채광", description="채광")
async def mining(interaction: Interaction, 광산: miningEnum):
    mine = Mining(User(interaction.user.id), 광산.value, interaction)
    await mine.validity()
client.run(os.environ['token'])
