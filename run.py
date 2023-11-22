# -*- coding: utf-8 -*-
# @Time    : 2023-08-28 18:10
# @Author  : JackWu
# @FileName: run.py

from scheduler import Scheduler
from api import app


def main():
    s = Scheduler()
    s.run()
    app.run(host='0.0.0.0',port=5000,debug=True)


if __name__ == '__main__':
    main()
