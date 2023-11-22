# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu
# @FileName: run.py
from flask import Flask, g, render_template,request
from db import Reids_Client
import json
import re
import requests

"""
没有找到，如何获得访问者的外网ip方法，只能让其手动
"""


app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis_client'):
        g.redis_client = Reids_Client()
    return g.redis_client

@app.route('/')
def index():
    print('访问者的IP:',request.remote_addr)
    print(request.user_agent)
    return render_template("index.html", **locals())


@app.route('/proxy_index')
def proxy_index():
    return render_template("proxy_index.html", **locals())

@app.route('/add_ip',methods=['GET','POST'])
def add_ip():
    data = request.form
    ip = data.get('ip')
    if type(ip) == str:
        if len(ip) < 11:
            res = '请输入正确ip地址！'
            return render_template("add_ip.html", **locals())
        print('成功')
        api_url = 'http://wapi.http.linkudp.com/index/index/save_white?neek=253760&appkey=249595af6047611a7f0136c55508857d&white=' +ip
        print(api_url)
        res = requests.get(url=api_url).text
        return render_template("add_ip.html", **locals())
    return render_template("add_ip.html", **locals())

@app.route('/get_http')
def get_http():
    res = str(get_conn().pop(types='http'))
    res = json.loads(re.sub(r"'", '"', res))
    res['use_num'] = str(int(res['use_num']) + 1)
    get_conn().lput(str(res), types=res['types'])
    # return render_template("http_show.html", **locals())
    return res

@app.route('/get_https')
def get_https():
    res = str(get_conn().pop(types='https'))
    res = json.loads(re.sub(r"'", '"', res))
    res['use_num'] = str(int(res['use_num']) + 1)
    get_conn().lput(str(res), types=res['types'])
    # return render_template("https_show.html", **locals())
    return res


@app.route('/count')
def count():
    http_parameters, https_parameters = get_conn().queue_len()
    # ((54, 'http_proxies', 'http'), (56, 'https_proxies', 'https'))
    http_proxy_len = http_parameters[0]
    https_proxy_len = https_parameters[0]
    return render_template('show.html', **locals())


