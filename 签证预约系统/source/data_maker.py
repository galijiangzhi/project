import datetime
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import util.global_var as g
from ais import UnpaidAcct
from order_dic import order_dic
from time_maker import time_maker_ws_admin
from util.config import config
from util.db import db
from util.exception import ErrorException
from util.log import logger
import random

class DateMakerWsAdmin(object):
    def __init__(self):
        self.ws = []
        for second in range(g.DEFAULT_NUM_OF_DATE_MARK):
            self.ws.append(DateMakerWs(second))


lock_get_oldest_maker = threading.Lock()


class DateMakerWs(object):
    def __init__(self, second: int):
        logger.debug(f"启动DateMakerWs {second}")
        self.ws_name = str(second)
        self.second = second
        self.maker: DateMaker = None

        # 启动线程
        if not g.DEBUG:
            scheduler = BackgroundScheduler()
            clock = CronTrigger(second=self.second)
            scheduler.add_job(self.work, clock)
            scheduler.start()

    def __get_oldest_maker__(self):
        """查找最老的日期生产员，并且db更新为最新使用过
            最老： db.date_maker.last_use 正排序
            可用的日期生产员： db.acct.paid = 0 False
                            db.acct.chk_status = 0 未检查或者账户正常
            生产员的类型必须是系统指定类型：
                            db.
            不用判断是否已经load到系统，因为日期生产员数量一定保证>60人
        """

        # 加锁，避免get到同一个老生产员
        with lock_get_oldest_maker:
            # db查找最老的日期生产员
            sql = f'select date_maker.ivr FROM date_maker ' \
                  f'left join acct on date_maker.ivr = acct.ivr ' \
                  f'left join acct_type on ' \
                  f'    acct.country = acct_type.country ' \
                  f'    and acct.visa = acct_type.visa ' \
                  f'    and acct.is_tcn = acct_type.is_tcn' \
                  f'    and acct.is_doc_rtn = acct_type.is_doc_rtn' \
                  f'    and acct.ppl_cnt = acct_type.ppl_cnt ' \
                  f'where ' \
                  f'    acct.chk_status = 0 and acct.paid = 0 ' \
                  f'    and acct_type.acct_type_cd = \'{config.acct_type_cd}\' ' \
                  f'order BY date_maker.last_use limit 1'
            row_list = db.select(sql)
            if len(row_list) == 0:
                raise ErrorException(f"DB里面找不到可以使用的日期生产员")
            ivr = row_list[0][0]

            # db更新为最新使用过
            sql = f'UPDATE date_maker SET last_use=now() WHERE ivr=\'{ivr}\''
            db.update(sql)

            return ivr

    def work(self):
        """
        取日期
            工位上还没有安排datamaker的话，安排一个
            让datamaker取日期，并把task传给time mgr
        """

        logger.debug(f"日期工位 {self.ws_name} 被定时触发")

        # maker还没有设置的话，找一个maker，然后上线
        if self.maker is None:
            # 查找一个可以load的date maker
            ivr = self.__get_oldest_maker__()
            self.maker = DateMaker(ivr)
            self.maker.start()

        # 0分开始，每5分钟时间取日期
        try:
            # 从网站取最早可约日期
            earliest_date_list, history_create_timestamp = self.maker.get_dates(auto_login=True)

            # lock的话，关闭本生产员
            #   end这个生产员，并通知下次需要换生产员
            if len(earliest_date_list) == 0:  # 自己没找到日期，可能被lock了
                if self.maker.is_locked():  # 如果别人能看到数据，那就真的被lock了
                    # end这个生产员
                    self.maker.stop()
                    # 通知下次需要换生产员
                    self.maker = None

            # 如果有消费者需要某个日期，就把task传给时间生产员
            # todo：还没有测试，等消费者上线
            for (city_cd, earliest_date) in earliest_date_list:
                acpt_appl_list = order_dic.get_appl_list(city_cd, earliest_date)
                if acpt_appl_list is not None:
                    time_maker_ws_admin.find_multi_maker_to_sche(city_cd, earliest_date, acpt_appl_list)


        except ErrorException as e:
            # todo:如果是账户检查的错误，需要保存数据库
            pass

        except Exception as e:
            print(e)
            # end这个生产员(logout并关闭激活线程)
            self.maker.stop()
            # 通知下次需要换生产员
            self.maker = None


class DateMaker(UnpaidAcct):
    continue_get_null_date_cnt = 0

    def __init__(self, ivr: str):
        # 从db load指定ivr
        row_list = db.select(f"select ivr, user_name, password, country, "
                             f"visa, is_tcn, is_doc_rtn, ppl_cnt, "
                             f"paid, can_be_time_maker, chk_status, chk_desc, "
                             f"create_timestamp, update_datetime"
                             f" from `acct` where ivr = {ivr}")
        if len(row_list) == 0:
            raise ErrorException(f"DB的账号表里面找不到日期生产员ivr {ivr}的账号")
        for row in row_list:
            ivr, user_name, password, country, \
            self.visa, self.is_tcn, self.is_doc_rtn, self.ppl_cnt, \
            self.paid, self.can_be_time_maker, self.chk_status, self.chk_desc, \
            self.create_timestamp, self.update_datetime = row
        super(DateMaker, self).__init__(country, user_name, password, ivr)

    def get_dates(self, auto_login: bool = False):
        """ 从网站爬取日期信息。
            如果没有爬到
                别人如果能爬到，就是自己被lock了，就要raise Exception
                别人也爬不到，那就不一定是lock。得随机决定自己是否按照lock处理
        """

        # 取得日期信息
        date_list = super(DateMaker, self).get_dates(auto_login = False)

        # 记录数据库履历信息
        def save_history_to_db(date_list):
            now_dt = datetime.datetime.now()
            now_dt_str = datetime.datetime.strftime(now_dt, "%Y-%m-%d %H:%M:%S.%f")

            def insert(ivr, now_dt_str, city_cd, valid_date, rslt_sts, err_msg):
                sql = f'insert into date_prod_history (' \
                      f'    ivr, create_timestamp, city_cd, valid_date, rslt_sts, err_msg) ' \
                      f'values (' \
                      f'    \'{ivr}\', \'{now_dt_str}\', \'{city_cd}\', \'{valid_date}\', {rslt_sts}, \'{err_msg}\')'
                db.insert(sql)

            if len(date_list) == 0:
                insert(self.ivr, now_dt_str, city_cd="", valid_date="", rslt_sts=2, err_msg="")
            else:
                for city_cd, rslt_date in date_list:
                    insert(self.ivr, now_dt_str, city_cd, valid_date=rslt_date, rslt_sts=1, err_msg="")

            return now_dt_str

        save_history_to_db(date_list)

        def __is_others_can_get_date__():
            """
            判断同类型的其他人是否在最近可以get网站上的日期
                最近指最近15分钟
            """
            row_list = db.select(f"select date_prod_history.ivr from date_prod_history "
                                 f" left join acct on date_prod_history.ivr = acct.ivr "
                                 f" where date_prod_history.city_cd != \'\' and not isnull(date_prod_history.city_cd) "
                                 f" and acct.country = \'{self.country}\' and acct.visa = \'{self.visa}\' "
                                 f" and acct.is_tcn = {self.is_tcn} and acct.is_doc_rtn = {self.is_doc_rtn} "
                                 f" and acct.ppl_cnt = {self.ppl_cnt} "
                                 f" and date_prod_history.create_timestamp > DATE_ADD(NOW(), INTERVAL -15 MINUTE)")

            return False if len(row_list) == 0 else True

        # 如果过去15分钟，3次都没取到信息，则检查是否被lock了
        self.continue_get_null_date_cnt = self.continue_get_null_date_cnt + 1 if len(date_list) == 0 else 0
        if self.continue_get_null_date_cnt >= 3:  # 连续lock3次
            if __is_others_can_get_date__():
                raise ErrorException(f"日期生产员 {self.ivr}被lock了。因为连续三次都没法取得日期信息，并且其他生产员能取到信息")
            else:
                if random.choice([True, False]):
                    raise ErrorException(
                        f"日期生产员 {self.ivr}可能被lock了。虽然自己连续三次都没法取得日期信息，但是别人最近也没有取到。最终随机决定这个生产员lock了，以便换一个生产员")
                else:  # 如果随机决定结果是未被lock，计数器减1
                    self.continue_get_null_date_cnt -= 1

        return date_list

if __name__ == '__main__':
    # dm = DateMaker("10363851")
    # dm = DateMaker("72981645")  # lock了
    # dm.get_dates(auto_login=True)

    dm_ws = DateMakerWs(1)
    dm_ws.work()

    date_maker_ws_admin = DateMakerWsAdmin()
