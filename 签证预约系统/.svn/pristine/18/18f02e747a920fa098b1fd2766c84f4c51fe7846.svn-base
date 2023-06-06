import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import util.global_var
import workstation
from ais import *
from util.exception import *
from util.log import logger
from util import global_var as g
from util import utils
from workstation import *
import threading
import apscheduler
import time
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import threading
import appl_order

if __name__ == '__main__':
    #创建数据库接口
    #mysql = utils.Mysql(g.MYSQL['db'], g.MYSQL['passwd'], g.MYSQL['host'], g.MYSQL['port'], g.MYSQL['user'], g.MYSQL['charset'])
    # list1 = mysql.accountuser('select ivr from `date_maker`')
    # print(list1)
    #list2 = mysql.accountuser('select * from `date_maker` where last_use >= now()- limit 1')
    #print(list2)
    for i in range(util.global_var.DEFAULT_NUM_OF_DATE_MARK):
        t = threading.Thread(target=workstation.open_date_maker, args=(i,))
        t.start()
    while True:
        time.sleep(1)


    #datamaker = workstation.DateMakerWorkstation()
    #timemaker = workstation.TimeMakerWorkstation()
