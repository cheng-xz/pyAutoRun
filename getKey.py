#-*- coding:gbk -*-
#filename: getKey.py
#�ó������ֱ����2.7�汾����
#--------------------------------------
#   author : ��Э��
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#��ģ����Ҫ��ʵ�ֺͷ���˵���ԿЭ�̣���������˷��ص���Կ��Ϣд�뵽��ʱ��Կ�����ļ���
#��ԭ������ԿЭ�̵Ĺ���������
'''
    ��ģ���ȡ��Կ��Ϣ
'''

from ConfigParser import ConfigParser
import global_var
from coreProc import *
from retcode import *

#�����ʼ��һЩ����
cf = ConfigParser()

#��ȡĿ���������Ϣ
cf.read('./aipay.cfg')
global_var.serv = cf.get('cfg','serv') + ':' + cf.get('cfg','serv_port')
uc = cf.get('cfg','serv_uc')
TerminalID = cf.get('cfg','TerminalID')
del cf
#�������������ǩ
global_var.COMMAND_STR = 'init'

#��ȡһ�������Կ
SignKeySeq_rand = random.getrandbits(4)
if SignKeySeq_rand == 0:
    SignKeySeq_rand = 1 

global_var.CurrInitKeySeq = SignKeySeq_rand
ClientPublicKey = global_var.clientRasPublicKey1
ClientModKey = global_var.clientRasModuleKey1

init = get_msg_imp('init',[TerminalID,SignKeySeq_rand,1,16,ClientPublicKey,ClientModKey,'AndroidSec_V2.3.5'])
#������Ϣ
data = default_msg_send(uc,init,tips='��ԿЭ��<init>')
init_retn = eval(data)
if init_retn['RetCode'] != 0:
    print '��ԿЭ��ʧ�ܣ�������룺%s' % RetCodeConst.get(init_retn['RetCode'])
else: #��ӡ���ɵ���Կ��Ϣ
    try:
        SignKeySeq = init_retn['Body']['SignKeySeq']
        ServPublicKey = init_retn['Body']['ServPublicKey']
        ServModKey = init_retn['Body']['ServModKey']
    except:
        print '���ص����ݲ��������Զ��˳�!!'
        sys.exit(1)
    else:
        print '���ص�ǩ����ʼ��Կ����ǣ�',SignKeySeq,'\n����˹�Կ��:',ServPublicKey,'\n����˹�ԿģN�ǣ�',ServModKey
        cf1 = ConfigParser()
        cf1.read('./temp.cfg')
        cf1.set('key','serverRasPublicKey1',ServPublicKey)
        cf1.set('key','serverRasModuleKey1',ServModKey)
        #����д�����ݻ�д���ļ���
        cf1.write(open('./temp.cfg','w'))
        del cf1
        #�����صķ���˳�ʼ��Կ��ű�����ȫ���ļ���
        global_var.CurrInitServKeySeq = SignKeySeq
        #��ӡ��ǩ��Ϣ
        CheckBodySign()
