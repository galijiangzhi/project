关于安装
    1，安装相应的chromedriver
        确认已经安装chrome浏览器，并查看chrome浏览器的版本
        下载相应版本的chromedriver.exe
            https://chromedriver.chromium.org/downloads
        拷贝chromedriver.exe到python编译器可以找到的目录
    2，安装编译器要求安装的各种python包
    3，用test.py测试是否能正确login账户，正确取得相应的日期时间

关于功能
    ais网站操作分为两类，已付费账户和未付费账户，这两类的功能有所不同。
    未付费账户：
        可以login
        取得日期（一次可以取得账户相关国家的所有城市的最早日期）
    已付费账户：
        可以login（login的同时会做检查：tcn，预约人数，visa类型，账户是否过期等）
        取得时分
        预约面试
