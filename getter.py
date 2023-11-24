# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu
import requests, re
from settings import HTTP_URL, HTTPS_URL
# from proxypool.settings import HTTP_URL, HTTPS_URL
import time


class IpProxyMeta(type):
    """
    继承python所有类的祖宗，即自定义元类
    """
    def __new__(cls, name, bases, attrs):
        # protocol 协议 指定为http还是https、scoks5
        attrs['__Protocol_Func__'] = []
        for k, v in attrs.items():
            if 'protocol_' in k:
                attrs['__Protocol_Func__'].append(k)
        return type.__new__(cls, name, bases, attrs)


class IpProxyGetter(metaclass=IpProxyMeta):
    """
    从IP代理服务商，提取代理IP
    http
    https
    socks5
    隧道代理
    """

    def get_raw_proxies(self, callfunc):
        """ # TODO 使用异步协程来处理, 这里并未实现真正意义上阈值处理
        通过给指定名字来调用对应方法，获取某种协议代理如callfunc = protocol_http
        获得的为http协议的IP
        :param callfunc:
        :return:
        """
        proxies = []
        for proxy in eval(f'self.{callfunc}()'):
            proxies.append(proxy)
        return proxies

    def protocol_http(self):
        """
          获取 http 类型代理
        """
        time.sleep(2)
        if HTTP_URL != None:
            proxies = []
            response = requests.get(
                url=HTTP_URL
            )
            json = response.json()['data']
            # 获取时间
            for i in json:
                ip = i['ip'] + ":" + str(i['port'])
                res = {"ip": "{}".format(ip), "expire_time": "{}".format(i['expire_time']), "types": "http",
                       "use_num": '0'}
                proxies.append(res)
                # yield res
            return proxies

    def protocol_https(self):
        """
          获取 https 类型代理
        """
        time.sleep(2)
        if HTTPS_URL != None:
            proxies = []
            response = requests.get(
                url=HTTPS_URL
            )
            json = response.json()['data']
            # print(json)
            # 获取时间
            for i in json:
                ip = i['ip'] + ":" + str(i['port'])
                res = {"ip": "{}".format(ip), "expire_time": "{}".format(i['expire_time']), "types": "https",
                       "use_num": '0'}
                proxies.append(res)
                # yield res
            return proxies
        return None



if __name__ == '__main__':
    f = IpProxyGetter()
    print(f.__dir__())
    # print(f.__Protocol_Func__)
    # print(IpProxyGetter().protocol_http())
