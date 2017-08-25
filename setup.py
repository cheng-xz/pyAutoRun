# -*- coding:gbk -*-
# setup.py
from distutils.core import setup
import py2exe

setup(
    version = "0.1",
    description = 'aipay auto send http json tools',
    name = 'auto_main_c',
    console=["auto_main_c.py"],
    data_files = [('.',["aipay.cfg","RSAUtil.class","jasypt-1.7.1.jar","更新日志.txt"])]
    )
