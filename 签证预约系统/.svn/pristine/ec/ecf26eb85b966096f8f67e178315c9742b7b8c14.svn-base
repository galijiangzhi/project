import logging

import yaml

import util.global_var as g
from util.log import logger


class Config:
    def __init__(self, yaml_file: str):
        try:
            logging.debug("开始读取配置文件")
            with open(yaml_file, 'rb') as f:
                # yaml文件通过---分节，多个节组合成一个列表
                date = yaml.safe_load_all(f)
                # salf_load_all方法得到的是一个迭代器，需要使用list()方法转换为列表
                data_dict = dict(list(date)[0])

                self.db_host = data_dict.get("db_host")
                self.db_user = data_dict.get("db_user")
                self.db_password = data_dict.get("db_password")
                self.db_database = data_dict.get("db_database")
                self.acct_type_cd = data_dict.get("acct_type_cd")

            return
        except Exception as e:
            raise e


config = Config(g.CONFIG_FILE_NAME)

if __name__ == '__main__':
    logger.debug(["db信息", config.db_user, config.db_host, config.db_database, config.db_password])
    logger.debug(["可处理账户的信息", config.acct_type_cd])
