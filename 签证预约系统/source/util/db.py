import json
import time
from apscheduler.schedulers.background import BackgroundScheduler

from util.exception import CriticalException, ErrorException, WarningException
from util.log import logger
from util.config import config

import MySQLdb
from dbutils.pooled_db import PooledDB


class _MySQLPool:
    port = 3306
    charset = 'utf8'

    pool = None
    limit_count = 10  #最低预启动数据库连接数量

    def __init__(self):
        self.pool = PooledDB(MySQLdb, self.limit_count,
                             host=config.db_host,
                             user=config.db_user,
                             password=config.db_password,
                             db=config.db_database,
                             port=self.port, charset=self.charset, use_unicode=True)

    def select(self, sql):
        logger.debug(sql)
        conn = self.pool.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in result:
            logger.debug(row)
        return result

    def insert(self, sql):
        self.__ins_upd_del__(sql)

    def update(self, sql):
        self.__ins_upd_del__(sql)

    def delete(self, sql):
        self.__ins_upd_del__(sql)

    def execute_many(self, sql_list):
        if sql_list is None:
            return

        logger.debug(sql_list)
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            for sql in sql_list:
                cursor.execute(sql)
                logger.debug([True, int(cursor.lastrowid)])
            conn.commit()
        except Exception as err:
            conn.rollback()
            raise err
        finally:
            cursor.close()
            conn.close()

    def __ins_upd_del__(self, sql):
        logger.debug(sql)
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
            logger.debug([True, int(cursor.lastrowid)])
        except Exception as err:
            conn.rollback()
            raise err
        finally:
            cursor.close()
            conn.close()


class _DB_Log:
    def debug(self, descript):
        self.__add__(1, descript)

    def info(self, descript):
        self.__add__(2, descript)

    def warning(self, descript: (Exception, str)):
        self.__add__(3, str(descript))

    def error(self, descript: (Exception, str)):
        self.__add__(4, str(descript))

    def critical(self, descript: (Exception, str)):
        self.__add__(4, str(descript))

    def __add__(self, level, descript):
        db.insert("insert into log (level, descript) values (%d, '%s');" % (level, descript))


class _AutoCacheTbl:
    def __init__(self, start_hhmm, interval_minutes=5):
        self.__refresh__()
        self.sche = BackgroundScheduler(job_defaults={'max_instances': 1, 'misfire_grace_time': 5 * 60})
        self.sche.add_job(self.__refresh__, 'interval', minutes=interval_minutes,
                          start_date='2022-01-01 00:' + start_hhmm, args=[])
        # 启动线程
        self.sche.start()

    def __refresh__(self):
        pass

    def __del__(self):
        self.sche.shutdown()


class _SysParmTbl(_AutoCacheTbl):
    def __init__(self):
        self.__store__ = {}
        super(_SysParmTbl, self).__init__(start_hhmm="02:00", interval_minutes=5)

    def get(self, key):
        if key not in self.__store__:
            raise CriticalException("数据库的sys_parm表缺少数据。key=%s" % key, "TABLE_MISS_DATA")
        return self.__store__.get(key)

    def __refresh__(self):
        result = db.select("select parm_key, parm_value, value_type from sys_parm")
        for row in result:
            key = row[0]
            type = row[2]
            if type == "str":
                value = row[1]
            elif type == "int":
                value = int(row[1])
            elif type == "float":
                value = float(row[1])
            elif type == "bool":
                value = bool(row[1])
            elif type == "json":
                value = json.loads(row[1])
            else:
                value = row[1]

            self.__store__.update({key: value})

        logger.debug(self.__store__)


class _TcnDefineTbl(_AutoCacheTbl):
    def __init__(self):
        self.__store__ = {}
        super(_TcnDefineTbl, self).__init__(start_hhmm="02:02", interval_minutes=5)

    def get(self, country):
        if country not in self.__store__:
            raise CriticalException("数据库的tcn表缺少国家%s" % country, "TABLE_MISS_DATA")
        return self.__store__.get(country)

    def __refresh__(self):
        result = db.select("select country, type, value from tcn")
        for row in result:
            self.__store__.update({row[0]: (row[1], row[2])})


class _CityTbl(_AutoCacheTbl):
    def __init__(self):
        self.__store__ = {}
        super(_CityTbl, self).__init__(start_hhmm="02:03", interval_minutes=5)

    def get_city_code(self, city_name):
        if city_name not in self.__store__:
            raise ErrorException(("数据库的city表缺少城市名称%s" % city_name), "TABLE_MISS_DATA")
        return self.__store__.get(city_name)

    def __refresh__(self):
        result = db.select("select city_name, city_cd from city")
        for row in result:
            self.__store__.update({row[0]: row[1]})


db = _MySQLPool();
sys_parm = _SysParmTbl()
tcn_def = _TcnDefineTbl()
city_tbl = _CityTbl()
dblog = _DB_Log()
#if __name__ == '__main__':

    # 增删改查， 批量处理
    #result_list = db.select("select * from acct")
    #print(result_list)
    # db.insert(
    #     "INSERT INTO `sys_parm` (`parm_key`, `parm_value`, `comm`, `create_timestamp`, `update_datetime`) "
    #     "VALUES ('test key', '999', '测试专用的', '2022-11-01 12:38:53', '2022-11-01 12:38:53');")
    # db.update(
    #     "UPDATE `sys_parm` SET `parm_key`='test key', `parm_value`='111', `comm`='测试专用，更新后', "
    #     "`create_timestamp`='2022-11-01 12:38:53', `update_datetime`='2022-11-01 12:38:53' "
    #     "WHERE `parm_key`='test key';")
    # db.delete("DELETE FROM `sys_parm` WHERE `parm_key`='test key'")
    # db.execute_many(["DELETE FROM `sys_parm` WHERE `parm_key`='test key'",
    #                  "DELETE FROM `sys_parm` WHERE `parm_key`='test key'",
    #                  "DELETE FROM `sys_parm` WHERE `parm_key`='test key'"])
    #
    # # 主表数据会在系统初始化时候就load到内存，只需要在内存里面查就行了
    # logger.debug(sys_parm.get("data_maker.relogin_min"))
    # logger.debug(tcn_def.get("ca"))
    # logger.debug(city_tbl.get_city_code("Vancouver"))
    #
    # # 数据库log
    # dblog.critical(CriticalException("0001", "config文件有错误"))
    # dblog.critical("又是一个严重错误")
    # dblog.warning("警告信息")
    # dblog.error("错误信息")
    # dblog.info("数据库log测试结束")