# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu

# ---------------------- redis 配置 -----------------------
HOST = 'localhost'
PORT = 6379
PASSWORD = '123456'

PROXY_NAME = 'proxies'
HTTP_PROXY_NAME = 'http_proxies'    # HTPP IP存储
HTTPS_PROXY_NAME = 'https_proxies'  # HTTPS IP存储

# -------------------- 代理商API接口  -----------------------
HTTP_URL = 'http://webapi.http.zhimacangku.com/getip?num=20&type=2&pro=0&city=0&yys=0&port=1&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='
HTTPS_URL = 'http://webapi.http.zhimacangku.com/getip?num=20&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='

# HTTPS_URL = None  # 不获得https类型

# ------------------- Scheduler 调度器配置 -------------------

TEST_TIME_OUT = 10  # 测试单个代理的超时时长
CYCLE_VAILD_TIME = 60  # 循环校验时间
ADD_CYCLE_TIME = 60  # 循环添加时间

LOWER_THRESHOLD = 20  # 代理池IP数量最小值
UPPER_THRESHOLD = 60  # 代理池IP数数量最大值

IP_LIVE = 120  # 代理API过期时间，实际上应当提前，避免IP失效了，造成请求接口响应失败误判为封禁，网络超时，数据丢失等
IP_CEHCK_COUNT = 0.3  # 每次校验10%
