import pymysql
import os
import random
from dotenv import load_dotenv

load_dotenv()


con = pymysql.connect(host=os.environ['host'], password=os.environ['password'],
                      user=os.environ['user'], port=int(os.environ['port']), database=os.environ['database'], charset='utf8')

cur = con.cursor()
cur.execute("SELECT percent FROM enemy WHERE floor = 1")


def checkSuccess(probabilities: list | tuple):
    random_number = random.uniform(0, 1)
    cumulative_probability = 0
    for i, prob in enumerate(probabilities):
        cumulative_probability += prob
        if random_number <= cumulative_probability:
            return i
    return -1


a = cur.fetchall()
new_a = [value[0] for value in a]
print(checkSuccess(new_a))
