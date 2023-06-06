import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from ais import *
from util.exception import *
from util.log import logger


def pressure_test():
    """ 专业压力测试
    """
    # 创建多个未付费账户
    acct_list = [
        UnpaidAcct("ca", "acomasvu25@hotmail.com", "ggxvisa!", "90207107"),
        UnpaidAcct("ca", "adellewlol38@hotmail.com", "ggxvisa!", "71508532"),
        UnpaidAcct("ca", "aleshakarcz2nbv@hotmail.com", "ggxvisa!", "72520229"),
        UnpaidAcct("ca", "alexar0roen@hotmail.com", "ggxvisa!", "89307271"),
        UnpaidAcct("ca", "alfholesxp@hotmail.com", "Usavisa!", "23740532"),
        UnpaidAcct("ca", "anderamx1qt@hotmail.com", "Usavisa!", "18666806"),
        UnpaidAcct("ca", "anglawoxod@hotmail.com", "ggxvisa!", "46614194"),
        UnpaidAcct("ca", "anima21wslowe@hotmail.com", "Usavisa!", "31068715"),
        UnpaidAcct("ca", "antfk1duce@hotmail.com", "ggxvisa!", "11708124"),
        UnpaidAcct("ca", "aricruse22@hotmail.com", "Usavisa!", "48997415"),
        UnpaidAcct("ca", "austinva2k@hotmail.com", "Usavisa!", "71050605"),
        UnpaidAcct("ca", "averytqs@hotmail.com", "Usavisa!", "81230885"),
        UnpaidAcct("ca", "avilatbgm@hotmail.com", "ggxvisa!", "83628965"),
        UnpaidAcct("ca", "beatagabmljz@hotmail.com", "Usavisa!", "69956092"),
        UnpaidAcct("ca", "benjlsxxhaaby@hotmail.com", "ggxvisa!", "49144381"),
        UnpaidAcct("ca", "bentleykix0m@hotmail.com", "Usavisa!", "25658456"),
        UnpaidAcct("ca", "biffmarionpc39@hotmail.com", "Usavisa!", "76775155"),
        UnpaidAcct("ca", "billyecaep@hotmail.com", "Usavisa!", "40685212"),
        UnpaidAcct("ca", "bl62faraj@hotmail.com", "Usavisa!", "36862366"),
        UnpaidAcct("ca", "brandaj7beckey@hotmail.com", "ggxvisa!", "12198303"),
        UnpaidAcct("ca", "brianafpn@hotmail.com", "Usavisa!", "95699573"),
        UnpaidAcct("ca", "brooksx7tredo@hotmail.com", "Usavisa!", "82013546"),
        UnpaidAcct("ca", "bryony4sde@hotmail.com", "Usavisa!", "62260697"),
        UnpaidAcct("ca", "c46enciso@hotmail.com", "Usavisa!", "83693325"),
        UnpaidAcct("ca", "caelie86ra@hotmail.com", "Usavisa!", "41832542"),
        UnpaidAcct("ca", "calleighsvme@hotmail.com", "ggxvisa!", "53024318"),
        UnpaidAcct("ca", "candisgvbrm@hotmail.com", "Usavisa!", "21758169"),
        UnpaidAcct("ca", "catgarney62m@hotmail.com", "ggxvisa!", "71253909"),
        UnpaidAcct("ca", "cathypex@hotmail.com", "Usavisa!", "94948607"),
        UnpaidAcct("ca", "ceislerzmqh@hotmail.com", "Usavisa!", "19471124"),
        UnpaidAcct("ca", "celinad8wr@hotmail.com", "Usavisa!", "29884507"),
        UnpaidAcct("ca", "chaddehaasq8e6@hotmail.com", "Usavisa!", "67971256"),
        UnpaidAcct("ca", "chagrederlqm3@hotmail.com", "Usavisa!", "91412965"),
        UnpaidAcct("ca", "charleydinmox0@hotmail.com", "Usavisa!", "18728662"),
        UnpaidAcct("ca", "chelsieu5gda@hotmail.com", "ggxvisa!", "82489664"),
        UnpaidAcct("ca", "cherinzasz@hotmail.com", "ggxvisa!", "93307471"),
        UnpaidAcct("ca", "cherylrowe8w7@hotmail.com", "Usavisa!", "21951668"),
        UnpaidAcct("ca", "cherystyler6zuh@hotmail.com", "ggxvisa!", "99107601"),
        UnpaidAcct("ca", "chhayse43@hotmail.com", "ggxvisa!", "43744001"),
        UnpaidAcct("ca", "chtozkoenig@hotmail.com", "ggxvisa!", "25417691"),
        UnpaidAcct("ca", "ciras4gdir@hotmail.com", "ggxvisa!", "87299047"),
        UnpaidAcct("ca", "claudettebar9lag@hotmail.com", "Usavisa!", "41672257"),
        UnpaidAcct("ca", "clematismisdd@hotmail.com", "Usavisa!", "82185157"),
        UnpaidAcct("ca", "clemfarugtt2s@hotmail.com", "ggxvisa!", "69767211"),
        UnpaidAcct("ca", "clorakf4mi@hotmail.com", "Usavisa!", "51350145"),
        UnpaidAcct("ca", "col6zlafler@hotmail.com", "Usavisa!", "32107450"),
        UnpaidAcct("ca", "connellt1l@hotmail.com", "Usavisa!", "95989685"),
        UnpaidAcct("ca", "cordelian2mi@hotmail.com", "Usavisa!", "96291699"),
        UnpaidAcct("ca", "cordiekvatmirsch@hotmail.com", "Usavisa!", "48497712"),
        UnpaidAcct("ca", "cristykatschmgvd@hotmail.com", "Usavisa!", "21200294"),
        UnpaidAcct("ca", "cwilsonwkh@hotmail.com", "ggxvisa!", "38998562"),
        UnpaidAcct("ca", "cxkbyrne@hotmail.com", "Usavisa!", "27103219"),
        UnpaidAcct("ca", "dalilakedwb@hotmail.com", "Usavisa!", "16293156"),
        UnpaidAcct("ca", "danmynearjqwt@hotmail.com", "Usavisa!", "10109920"),
        UnpaidAcct("ca", "dawsonmurin6fk@hotmail.com", "Usavisa!", "47067896"),
        UnpaidAcct("ca", "delight1bhpie@hotmail.com", "Usavisa!", "46849970"),
        UnpaidAcct("ca", "delphineha0x@hotmail.com", "Usavisa!", "11082771"),
        UnpaidAcct("ca", "dene9fbl@hotmail.com", "Usavisa!", "60208472"),
        UnpaidAcct("ca", "denesewi7f2@hotmail.com", "ggxvisa!", "35883406"),
        UnpaidAcct("ca", "derekcfhi@hotmail.com", "Usavisa!", "25446731")
    ]

    # 为所有账户login并创建线程
    sche = BackgroundScheduler(job_defaults={'max_instances': 100, 'misfire_grace_time': 5 * 60})
    sec = 0
    for acct in acct_list:
        # 以5分钟为节点，从0秒开始，每隔1秒，启动一个线程取日期(取日期同时让他自动login)
        sche.add_job(acct.get_dates,  'interval', minutes=5,
                          start_date='2022-01-01 00:00:%02d' % sec,
                          end_date='2023-10-25 23:10:00', args=[True, ])
        sec = sec + 1

    # 启动线程
    sche.start()

    time.sleep(1*60*60)


def start_date_maker():
    """ 日期生产员功能测试
    """
    # 初始化日期生产员
    date_maker = UnpaidAcct("ca", "alexar0roen@hotmail.com", "ggxvisa!", "89307271")

    # 关于with
    #   enter时候会自动login（约12秒）
    #   exit时候会自动logout
    # 关于激活线程
    #   如果不激活，这个账户在半小时后就因为session timeout被大使馆强制logout
    with date_maker:
        # 等待4小时（4小时后，日期生产员就被lock，失去取日期的能力了）
        # for i in range(0, 4*60):
        #     time.sleep(60)
        #
        #     # 每隔29分钟，激活一次。且第一次不做激活
        #     if (i+1) % 29 == 0:
        #         date_maker.activate()

        # # 等待过程中收到其他人的取日期的请求
        dates = date_maker.get_dates(auto_login=False)  # 约0.4秒


def start_time_maker():
    """ 时间生产员怎么用
    """

    # 初始化时间生产员
    time_maker = PrepaidAcct("ca", "2273383946@qq.com", "liusihan12345", "92740922", "B1", 0, 0, 1)

    # 关于with
    #   enter时候会自动login（约14秒）
    #   exit时候会自动logout
    # 关于激活线程
    #   如果不激活，这个账户在半小时后就因为session timeout被大使馆强制logout
    with time_maker:
        # 等待4小时（4小时后，时间生产员就被lock，失去取时间的能力了）
        for i in range(0, 4*60):
            time.sleep(60)

            # 每隔29分钟，激活一次。且第一次不做激活
            if (i+1) % 29 == 0:
                time_maker.activate()

        # # 等待过程中收到其他人的取时间的请求
        # times = time_maker.get_times("94", "2024-02-01")  # 约0.4秒


def start_applicant():
    """ 面试申请人（消费者）怎么用
    """
    # 初始化申请人
    applicant = PrepaidAcct("ca", "2273383946@qq.com", "liusihan12345", "92740922", "B1", 0, 0, 1) # 1人
    # applicant = PrepaidAcct("ca", "evadeng1115@hotmail.com", "Dyy9090787", "40966650", "B1", 0, 0, 2) # 2人
    with applicant:
        applicant.get_times("95", "2022-11-20")


    # 关于with
    #   enter时候会自动login（约14秒）
    #   exit时候会自动logout
    # 关于激活线程
    #   如果不激活，这个账户在半小时后就因为session timeout被大使馆强制logout
    with applicant:
        # 一直等待， 即使4小时后账户被锁也没事。因为账户被锁并不影响约位置。
        for i in range(0, 99999 * 60):
            time.sleep(60)

            # 每隔29分钟，激活一次。且第一次不做激活
            if (i + 1) % 29 == 0:
                applicant.activate()

        # # 等待过程中收到其他人的预约命令
        # # todo: 预约成功的话，怎样让上面那个循环退出？
        # applicant.schedule("94", "2022-11-26", "15:15")


if __name__ == '__main__':
    try:
        # 日期生产员启动
        #start_date_maker()

        # 时分生产员启动
        #start_time_maker()

        # 申请人（消费者）启动
        start_applicant()

        # 多线程压力测试
        #pressure_test()

    except WarningException as e:
        logger.warning(e)
    except ErrorException as e:
        logger.error(e)
    except CriticalException as e:
        logger.critical(e)
