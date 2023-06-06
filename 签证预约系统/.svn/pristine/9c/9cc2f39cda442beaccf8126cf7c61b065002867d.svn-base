import datetime
import random
import threading


from apscheduler.triggers.cron import CronTrigger

from ais import PrepaidAcct
from appl_order import ApplOrder
from util import global_var as g
from util import db
from util.db import *


class TimeMaker(PrepaidAcct):
    def __init__(self, ivr: str):
        # 从db load指定ivr
        row_list = db.select(f"select ivr, user_name, password, country, "
                             f"visa, is_tcn, is_doc_rtn, ppl_cnt, "
                             f"paid, can_be_time_maker, chk_status, chk_desc, "
                             f"create_timestamp, update_datetime"
                             f" from `acct` where ivr = {ivr}")
        if len(row_list) == 0:
            raise ErrorException(f"DB的账号表里面找不到时间生产员ivr {ivr}的账号")
        for row in row_list:
            ivr, user_name, password, country, \
            visa, is_tcn, is_doc_rtn, ppl_cnt, \
            self.paid, self.can_be_time_maker, self.chk_status, self.chk_desc, \
            self.create_timestamp, self.update_datetime = row
        super(TimeMaker, self).__init__(country, user_name, password, ivr, visa, is_tcn, is_doc_rtn, ppl_cnt)

    def fw_sche_to_appl(self, city_cd: str, appt_date: str, appl_list: list):
        """
        把可以预约的信息传给申请人
          对每个申请人启动一个线程
          每个申请人给的时间是动态的，而不是固定的
        不管是否成功，我们只负责转发。
        申请人自己决定
          成功还是失败
          怎么通知到使用者
        """

        # 取得所有可以预约的时间
        valid_time_list = self.get_times(city_cd, appt_date)
        if valid_time_list is None:
            dblog.error(f"时间生产员IVR {self.ivr}获取城市{city_cd}日期{appt_date}的可预约时间时候，出现不明系统错误")
        if len(valid_time_list) == 0:
            dblog.error(f"时间生产员IVR {self.ivr}获取城市{city_cd}日期{appt_date}的可预约时间时候，可能慢了一拍，未能拿到任何时间")

        # 把取到的时间在db里面记录一下履历
        def save_history_to_db(city_cd, appt_date, valid_time_list):
            now_dt = datetime.datetime.now()
            now_dt_str = datetime.datetime.strftime(now_dt, "%Y-%m-%d %H:%M:%S.%f")

            def insert(ivr, now_dt_str, city_cd, valid_date, valid_time_str, rslt_sts, err_msg):
                sql = f'insert into time_prod_history (ivr, create_timestamp, city_cd, valid_date, valid_time_list, rslt_sts, err_msg) ' \
                      f'values (\'{ivr}\', \'{now_dt_str}\', \'{city_cd}\', \'{valid_date}\', \'{valid_time_str}\', {rslt_sts}, \'{err_msg}\')'
                db.insert(sql)

            if len(valid_time_list) == 0:
                insert(self.ivr, now_dt_str, city_cd, appt_date, valid_time_list="", rslt_sts="2", err_msg="")
            else:
                insert(self.ivr, now_dt_str, city_cd, appt_date, ', '.join(valid_time_list), rslt_sts="1", err_msg="")

        save_history_to_db(city_cd, appt_date, valid_time_list)

        # 启动申请人去预约
        appl: ApplOrder
        for appl in appl_list:
            valid_time = random.choice(valid_time_list)
            if not g.DEBUG:
                # 启动线程约位置
                t = threading.Thread(target=appl.schedule, args=(city_cd, appt_date, valid_time, ), daemon=True)
                t.start()


lock_get_oldest_maker = threading.Lock()


class TimeMakerWs(object):
    def __init__(self, idx):
        logger.debug(f"启动TimeMakerWs {idx}")
        self.ws_name = idx
        self.second = idx
        self.maker: TimeMaker = None

        # 启动线程, 专门控制4小时换maker
        if not g.DEBUG:
            scheduler = BackgroundScheduler()
            # todo:从现在开始，每间隔4小时触发一次，并且第一次必须被触发
            clock = CronTrigger(second=self.second)
            scheduler.add_job(self.work, clock)
            scheduler.start()

    def work(self):
        logger.debug(f"时间工位 {self.ws_name} 被定时触发，开始更换生产员")

        # maker如果被创建出来了的话，让他stop
        # stop出错的话，也必须当做下线
        try:
            if self.maker is not None:
                self.maker.stop()
        except Exception as e:
            self.maker = None
            logger.debug(e, exc_info=True)

        # 如果失败的话，会努力尝试更换3个生产员
        errmsg = ""
        for i in range(3):
            try:
                # maker如果被创建出来了的话，让他stop
                if self.maker is not None:
                    self.maker.stop()

                # 查找一个可以load的time maker
                #   虽然有可能time maker本身就不够，有可能找到的是已经load到工位的其他maker
                #   但是这儿不考虑这种case。
                #   因为，time maker管理员启动时候就会检查一下maker是否充足
                #   保证了：maker数量 > 3 * 工位数量
                ivr = self.__get_oldest_maker__()
                self.maker = TimeMaker(ivr)
                self.maker.start()
                break

            except ErrorException as e:
                # todo:如果是账户检查的错误，需要保存数据库
                pass

            except Exception as e:
                print(e)
                errmsg = str(e)

                # end这个生产员(logout并关闭激活线程)
                if self.maker is not None:
                    self.maker.stop()

                # 通知下次需要换生产员
                self.maker = None

        # 连续更换了3次，还是没有成功更换，极有可能是系统问题
        if self.maker is None:
            dblog.critical(f"时间工位 {self.ws_name} 连续更换3次生产员都失败了，可能不是生产员问题，而是系统问题。 Errmsg{errmsg}")
            return

    def fw_sche_to_maker(self, city_cd: str, appt_date: str, appl_list: list):
        # todo: 如果maker正在换其他人，或者maker正在激活，已经logout。考虑清楚怎么对策
        if self.maker is None:
            raise ErrorException("时间工位管理员准备要把预约工作转交给自己的maker，但是maker是个None")
        self.maker.fw_sche_to_appl(city_cd, appt_date, appl_list)


    def __get_oldest_maker__(self):
        """查找最老的时间生产员，并且db更新为最新使用过
            最老： db.time_maker.last_use 正排序
            可用的时间生产员： db.acct.paid = 1 False
                            db.acct.chk_status = 0 未检查或者账户正常
                            db.acct.can_be_time_maker = 1 允许
            生产员的类型必须是系统指定类型：
        """

        # 加锁，避免get到同一个老生产员
        with lock_get_oldest_maker:
            # db查找最老的日期生产员
            sql = f'select time_maker.ivr FROM time_maker ' \
                  f'left join acct on time_maker.ivr = acct.ivr ' \
                  f'left join acct_type on ' \
                  f'    acct.country = acct_type.country ' \
                  f'    and acct.visa = acct_type.visa ' \
                  f'    and acct.is_tcn = acct_type.is_tcn' \
                  f'    and acct.is_doc_rtn = acct_type.is_doc_rtn' \
                  f'    and acct.ppl_cnt = acct_type.ppl_cnt ' \
                  f'where ' \
                  f'    acct.chk_status = 0 and acct.paid = 1 and acct.can_be_time_maker = 1 ' \
                  f'    and acct_type.acct_type_cd = \'{config.acct_type_cd}\' ' \
                  f'order by time_maker.last_use limit 1'
            row_list = db.select(sql)
            if len(row_list) == 0:
                raise CriticalException(f"DB里面找不到可以使用的时间生产员")
            ivr = row_list[0][0]

            # db更新为最新使用过
            sql = f'UPDATE time_maker SET last_use=now() WHERE ivr=\'{ivr}\''
            db.update(sql)

            return ivr



class TimeMakerWsAdmin(object):
    """时间生产管理员
    启动指定数量的工位（工位数量不变）
    接受取时间的请求，并转发给时间生产员继续完成约位置的工作（取时间，并叫醒消费者约位置）
        避免过于集中在某些时间生产员身上
    """

    def __init__(self):
        self.__chk_maker_enough__()
        self.ws = []
        for second in range(5):
            self.ws.append(TimeMakerWs(second))

    def __chk_maker_enough__(self):
        """
          为了避免time maker不足导致的load重复的maker到系统，必须保证：maker数量 > 3 * 工位数量
        """
        # todo: 细枝末节，以后做
        pass

    def find_multi_maker_to_sche(self, city_cd: str, appt_date: str, appl_list: list):

        # 任意找3个工位，让相应的时间生产员继续去预约
        assigned_ws_list = random.sample(self.ws, 4)
        for ws in assigned_ws_list:
            ws.fw_sche_to_maker(city_cd, appt_date, appl_list)


time_maker_ws_admin = TimeMakerWsAdmin()



if __name__ == '__main__':
    # dm = TimeMaker("31015075") # lock
    # dm = TimeMaker("92740922") # 未lock
    # dm.start()
    # dm.fw_sche_to_appl("94", "2024-03-01", ["ApplOrder(1)"])
    # dm.stop()

    # tm_ws = TimeMakerWs(1)
    # tm_ws.work()

    tm_ws_admin = TimeMakerWsAdmin()
    tm_ws_admin.ws[0].maker = TimeMaker("92740922")
    tm_ws_admin.ws[1].maker = TimeMaker("31015075")
    tm_ws_admin.ws[2].maker = TimeMaker("92740922")
    tm_ws_admin.ws[3].maker = TimeMaker("31015075")
    tm_ws_admin.ws[4].maker = TimeMaker("31015075")
    tm_ws_admin.ws[0].maker.start()
    tm_ws_admin.ws[1].maker.start()
    tm_ws_admin.find_multi_maker_to_sche("94", "2024-03-01", ["ApplOrder(1)"])
    logger.debug("over")
