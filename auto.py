from updater import Updater
from db_maker import DB_Maker
from datetime import datetime
import json


if __name__ == '__main__':
    current_year = datetime.now().year
    my_updater = Updater()
    my_db_maker = DB_Maker()
    my_db_maker.load_model()

    recent_year_dict = json.load(open('./data/recent_year_dict.json'))
    for conf, dblp in my_updater.get_conf2dblp().items():
        fromyear = recent_year_dict[conf] + 1
        toyear = current_year
        my_updater.update_conf(conf, dblp, fromyear, toyear)
        my_db_maker.make_conf_db(conf, fromyear, toyear)

    my_db_maker.make_configuration(1960, current_year)

