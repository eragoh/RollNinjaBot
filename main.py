import os
from dotenv import load_dotenv

from bot import RollNinja

if __name__ == '__main__':

    load_dotenv()
    token = os.getenv('TOKEN')
    RollNinja.fight(token)