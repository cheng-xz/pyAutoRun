#-*- coding:gbk -*-
#filename: getKey.py
#该程序可以直接在2.7版本运行
#--------------------------------------
#   author : 成协主
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#该模块主要是实现和服务端的密钥协商，并将服务端返回的密钥信息写入到临时密钥配置文件中
#由原来的密钥协商的功能所改造
'''
    该模块获取密钥信息
'''

from ConfigParser import ConfigParser
import global_var
from coreProc import *
from retcode import *

#这里初始化一些数据
cf = ConfigParser()

#读取目标服务器信息
cf.read('./aipay.cfg')
global_var.serv = cf.get('cfg','serv') + ':' + cf.get('cfg','serv_port')
uc = cf.get('cfg','serv_uc')
TerminalID = cf.get('cfg','TerminalID')
del cf
#设置命令串用于验签
global_var.COMMAND_STR = 'init'

#获取一个随机密钥
SignKeySeq_rand = random.getrandbits(4)
if SignKeySeq_rand == 0:
    SignKeySeq_rand = 1 

global_var.CurrInitKeySeq = SignKeySeq_rand
ClientPublicKey = global_var.clientRasPublicKey1
ClientModKey = global_var.clientRasModuleKey1

init = get_msg_imp('init',[TerminalID,SignKeySeq_rand,1,16,ClientPublicKey,ClientModKey,'AndroidSec_V2.3.5'])
#发送消息
data = default_msg_send(uc,init,tips='密钥协商<init>')
init_retn = eval(data)
if init_retn['RetCode'] != 0:
    print '密钥协商失败，错误代码：%s' % RetCodeConst.get(init_retn['RetCode'])
else: #打印生成的密钥信息
    try:
        SignKeySeq = init_retn['Body']['SignKeySeq']
        ServPublicKey = init_retn['Body']['ServPublicKey']
        ServModKey = init_retn['Body']['ServModKey']
    except:
        print '返回的数据不完整，自动退出!!'
        sys.exit(1)
    else:
        print '返回的签名初始密钥编号是：',SignKeySeq,'\n服务端公钥是:',ServPublicKey,'\n服务端公钥模N是：',ServModKey
        cf1 = ConfigParser()
        cf1.read('./temp.cfg')
        cf1.set('key','serverRasPublicKey1',ServPublicKey)
        cf1.set('key','serverRasModuleKey1',ServModKey)
        #将改写的内容回写到文件中
        cf1.write(open('./temp.cfg','w'))
        del cf1
        #将返回的服务端初始密钥编号保存在全局文件中
        global_var.CurrInitServKeySeq = SignKeySeq
        #打印验签信息
        CheckBodySign()
