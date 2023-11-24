# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu
import time, threading
from db import Reids_Client
from getter import IpProxyGetter
import re
from multiprocessing import Process
from settings import CYCLE_VAILD_TIME, LOWER_THRESHOLD, UPPER_THRESHOLD, ADD_CYCLE_TIME, IP_LIVE, IP_CEHCK_COUNT
import json
import logging
"""
    功能：调度器
    包含：
        ---添加器：从代理服务器获取IP,传给校验器
        ---校验器：校验IP是否过期,校验成功存储到redis  [可扩展性]
"""


class VaildityTester(object):
    '''
       校验器
    '''

    def __init__(self):
        # 设为私有，不允许外部调用，存放待校验ip
        self.__raw_proxies = []

    def set_raw_proxies(self, proxiies):
        """
        set_raw_proxies 集原料代理
        放入未校验ip
        :param proxies: 未校验ip 从getter 中传入待校验ip
        :return:
        """
        self.__raw_proxies = proxiies
        # 数据库连接-->创建的方式会影响程序性能--》用的时候创建
        self.__conn = Reids_Client()  # redis数据库对象

    def get_ProxyPararmeter(self, ProxyParameter, ip_live=IP_LIVE):
        """
        获取代理校验参数
        ProxyParameter:{'ip': ip, 'expire_time': i['expire_time'], 'types': 'https'}
        """
        # proxy是从redis取出，是bytes类型，所以无法判断，进行转换
        if isinstance(ProxyParameter, bytes):
            # 转换为字符串
            ProxyParameter = ProxyParameter.decode('utf-8')
        """
            这里有2个逻辑，getter下载器yield过来的为dcit
            进行校验的为str类型
        """
        if type(ProxyParameter) == str:
            ProxyParameter = json.loads(re.sub(r"'", '"', ProxyParameter))
        now_time = int(time.time())
        # 将其转换为时间戳
        timeArray = time.strptime(ProxyParameter['expire_time'], "%Y-%m-%d %H:%M:%S")
        Expiration_timeStamp = int(time.mktime(timeArray))
        # 判断是否过期，并且存储
        if (Expiration_timeStamp - ip_live) > now_time:
            if ProxyParameter['types'] == 'http':
                self.__conn.put(str(ProxyParameter), types='http')  # redis当中存储
            if ProxyParameter['types'] == 'https':
                self.__conn.put(str(ProxyParameter), types='https')  # redis当中存储
            print('校验成功代理：', ProxyParameter)
        else:
            # todo 删除逻辑没写
            print('\033[1;31m已过期代理：{}\033[0m'.format(ProxyParameter))

    def verify_check_switch(self):
        """
        校验器开关
        """
        print('\033[1;30m{}\033[0m'.format('-' * 23 + '  VaildityTester 校验器启动（校验内存中IP/redis中的IP，并且存储）  ' + '-' * 23))
        for ProxyParameter in self.__raw_proxies:
            self.get_ProxyPararmeter(ProxyParameter)


class PoolAdder(object):
    """
    添加器
    """

    def __init__(self, threshold=UPPER_THRESHOLD):
        # 创建存入redis数据库中最大代理池数量阈值 内置条件
        self.__threshold = threshold # 60
        # 创建开关实例
        self.__tester = VaildityTester()
        # 创建redis数据库对象实例
        self.__conn = Reids_Client()
        # 创建getter实例
        self.__getter = IpProxyGetter()

    def is_over_threshold(self, types):
        """
        判断代理池中代理的数量是否达到最大值
        :return True: 超过阈值
        """
        if int(self.__conn.queue_len(types=types)) >= self.__threshold:
            return True
        return False

    def add_to_pool(self, types):
        """
        添加代理 添加到篮子
        :return:
        """
        print('\033[1;30m{}\033[0m'.format('-' * 28 + '  PoolAdder 添加器启动（代理商获得IP 存入内存 启动校验） ' + '-' * 28))
        # 循环获取ip （获取材料）
        while True:
            if self.is_over_threshold(types=types):  # 判断是否低于阈值
                print(f'目前代理池的数量为限定{UPPER_THRESHOLD}，不需要下载IP')
                break
            proxy_count = 0
            for _ in self.__getter.__Protocol_Func__:
                # 判断是那种类型
                if types == 'http':
                    proxies = self.__getter.get_raw_proxies('protocol_http')
                    if len(proxies) > 0:
                        proxy_count += len(proxies)
                        # 使用校验器校验，是否过期
                        self.__tester.set_raw_proxies(proxies)  # 放入材料
                        self.__tester.verify_check_switch()  # 开启机器（开启校验方法）
                if types == 'https':
                    proxies = self.__getter.get_raw_proxies('protocol_https')
                    if len(proxies) > 0:
                        proxy_count += len(proxies)
                        # 使用校验器校验，是否过期
                        self.__tester.set_raw_proxies(proxies)  # 放入材料
                        self.__tester.verify_check_switch()  # 开启机器（开启校验方法）
            if proxy_count == 0:  #
                # 判出一个运行时间的异常
                raise RuntimeError('获取代理时间过快，可忽略此异常！')


class Scheduler(object):
    """
    调度器
    """

    # 1、循环校验过程 不断从带池中头部获取一片，做定期检查
    @staticmethod
    def valid_proxy(cycle=CYCLE_VAILD_TIME):
        """
        :param CYCLE_VAILD_TIME: # 需要设置一个循环校验时间，不然放待校验ip的速度，还赶不上校验的速度
        :return:
        """
        # 连接数据库 等会校验存入进去的代理
        conn = Reids_Client()
        # 校验器对象
        tester = VaildityTester()
        # 循环校验
        while True:
            print('\033[1;30m{}\033[0m'.format('-' * 30 + '  Scheduler 调度器启动（控制调度器、添加器 核心CPU） ' + '-' * 29))
            http_parameters, https_parameters = conn.queue_len()
            for i in [http_parameters, https_parameters]:
                count = int(i[0] * IP_CEHCK_COUNT)  # 代理池存放IP数量
                types = i[2]  # 代理池是什么类型的代理
                print('准备校验的代理IP数量', count)
                if count == 0:
                    time.sleep(cycle)
                    break
                print('' * 20 + '取之前长度', conn.queue_len())
                proxies = conn.get(count=count, types=types)
                print('取之后长度', conn.queue_len())
                print('取出待校验IP数量', len(proxies))
                # 校验
                tester.set_raw_proxies(proxies)
                tester.verify_check_switch()
            time.sleep(cycle)

    @staticmethod
    def check_pool_add(lower_threshold=LOWER_THRESHOLD,
                       upper_threshold=UPPER_THRESHOLD,
                       cycle=ADD_CYCLE_TIME):
        """
        添加器开关
        """
        conn = Reids_Client()
        adder = PoolAdder(upper_threshold)
        while True:
            # （已有IP长度，IP类型）
            http_parameters, https_parameters = conn.queue_len()

            if http_parameters[1] != None:
                if http_parameters[0] <= lower_threshold:
                    t1 = threading.Thread(target=adder.add_to_pool, args=(http_parameters[2],))
                    t1.start()
            if https_parameters[1] != None:
                if https_parameters[0] <= lower_threshold:
                    t2 = threading.Thread(target=adder.add_to_pool, args=(https_parameters[2],))
                    t2.start()

            time.sleep(cycle)

    def run(self):
        # 创建多进程
        p1 = Process(target=Scheduler.check_pool_add)  # 从启动代理，到校验保存逻辑
        p2 = Process(target=Scheduler.valid_proxy)
        p1.start()
        p2.start()


if __name__ == '__main__':
    Scheduler().valid_proxy()
