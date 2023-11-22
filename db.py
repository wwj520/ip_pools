# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu
# @FileName: run.py
import pickle

import redis
from settings import HOST, PASSWORD, PORT, PROXY_NAME, HTTP_PROXY_NAME, HTTPS_PROXY_NAME
import json


class Reids_Client(object):
    def __init__(self, host=HOST, port=PORT, password=PASSWORD):
        if password:
            self.__conn = redis.Redis(host=host, port=port, password=password)
        else:
            self.__conn = redis.Redis(host=host, port=port)

    def put(self, proxy, types):
        """
        向代理池尾部添加一个代理
        :param proxy: 代理ip
        :param types: 代理类型
        :return:
        """

        # self.__conn.rpush(PROXY_NAME, proxy)
        if types == 'http':
            self.__conn.rpush(HTTP_PROXY_NAME, proxy)
        if types == 'https':
            self.__conn.rpush(HTTPS_PROXY_NAME, proxy)

    def lput(self, proxy, types):
        '''
        向代理池头部部添加一个使用过的代理
        :param proxy:
        :return:
        '''
        # self.__conn.lpush(PROXY_NAME, proxy)
        if types == 'http':
            self.__conn.lpush(HTTP_PROXY_NAME, proxy)
        if types == 'https':
            self.__conn.lpush(HTTPS_PROXY_NAME, proxy)

    def pop(self, types):
        """
        获取一个代理
        redisd的存储所有数据都是bytes类型-
        :param types: 代理类型
        :return: 可用的最新代理
        """

        # return self.__conn.rpop(PROXY_NAME).decode('utf-8')
        if types == 'http':
            return self.__conn.rpop(HTTP_PROXY_NAME).decode('utf-8')
        if types == 'https':
            return self.__conn.rpop(HTTPS_PROXY_NAME).decode('utf-8')

    def get(self, count=1, types=None):
        """
        获取count个代理，同时将这些数据删除
        :param count: 默认数量为1
        :param types: 代理类型
        :return:
        """

        if types == 'http':
            proxies = self.__conn.lrange(HTTP_PROXY_NAME, 0, count - 1)
            self.__conn.ltrim(HTTP_PROXY_NAME, count, -1)
            return proxies
        if types == 'https':
            proxies = self.__conn.lrange(HTTPS_PROXY_NAME, 0, count - 1)
            self.__conn.ltrim(HTTPS_PROXY_NAME, count, -1)
            return proxies

    def queue_len(self, types=None):
        """
        针对添加器，什么是开始添加，什么时候结束添加，应该查看代理池有无数据，那么查看代理池的长度
        :param types: 代理类型
        :return:
        """
        # return self.__conn.llen(PROXY_NAME)
        if types == None:
            http_parameters = (self.__conn.llen(HTTP_PROXY_NAME), HTTP_PROXY_NAME,'http')
            https_parameters = (self.__conn.llen(HTTPS_PROXY_NAME), HTTPS_PROXY_NAME,'https')
            return http_parameters, https_parameters
        elif types == 'http':
            return self.__conn.llen(HTTP_PROXY_NAME)
        elif types == 'https':
            return self.__conn.llen(HTTPS_PROXY_NAME)

    def flush(self):
        self.__conn.flushdb()  # 清空代理池


if __name__ == '__main__':

    conn = Reids_Client()
    print(conn.queue_len(types='http'))


    # redis中，如果为0是所有都取出，因为这个错误导致bug，直接忽略阈值情况
    # print('取之前长度', conn.queue_len)
    # res = conn.get(count=1)
    # print('取之后长度', conn.queue_len)
    # print('取的IP', res)
    # print(len(res))