#!/usr/bin/python2
# -*- coding: utf-8 -*-

from item_catalog import app

if __name__ == '__main__':
    app.secret_key = 'WLEF34HH1QKV8PIQEY228IYN5ZGZAXCG'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
