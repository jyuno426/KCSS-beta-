import traceback
from updater import Updater
from db_maker import DB_Maker
from datetime import datetime
from utils import webhook
import json
import traceback


if __name__ == '__main__':
    try:
        webhook("Update start!")
        current_year = datetime.now().year
        my_updater = Updater()
        my_db_maker = DB_Maker()
        my_db_maker.load_model()

        recent_year_dict = json.load(open('./data/recent_year_dict.json'))
        for conf, dblp in my_updater.get_conf2dblp().items():
            fromyear = recent_year_dict[conf] + 1
            toyear = current_year
            print(conf, fromyear, toyear)
            success_years = my_updater.update_conf(conf, dblp, fromyear, toyear)
            for year in success_years:
                while not my_db_maker.make_conf_year_db(conf, year):
                    pass
            #if len(success_years) == 0:
            #    webhook(conf + " is already updated")
        
        # For manual update
        # while not my_db_maker.make_conf_year_db('iclr', 2020):
        #     pass

        my_db_maker.make_configuration(1960, current_year)
        webhook("Update finished")
    except Exception as e:
        webhook('Error occurred while updating')
        trace = traceback.format_exc()
        webhook(str(trace))

