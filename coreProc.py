#-*- coding:gbk -*-
#filename: coreProc.py
#�ó������ֱ����2.7�汾����
#--------------------------------------
#   author : ��Э��
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

from mPublic import *
import global_var
import sys
import httplib
import md5

#��ģ���Ǻ���ҵ����ģ�飬���ڴ�����Ϣ

'''
    �����Ǻ���ҵ����ģ�飬��������ϵͳ�ǼܵĴ
'''

#�������������ⷵ����Ϣ��Body-Sign�Ƿ���ȷ
#��Ҫ�Ĳ����У�
#   ���ص�Body-Sign
#   ���ص�msg
#   ���е�ѡ��
def CheckBodySign():
    if global_var.COMMAND_STR == 'init':  #�������ԿЭ��
        myrsa1 = MyRSA()
        #�Է�����Ϣ����md5
        retn_value_md5 = md5.new(global_var.retn_msg).hexdigest()
        #��ȡ��ǰ��ʼ��Կ���
        CurrInitServKeySeq = global_var.CurrInitServKeySeq
        #�ó�ʼ��Կ˽Կ�Է��ص�BODY-SIGN���н���
        my_value_md5 = myrsa1.decrypt(global_var.retn_bodysign,global_var.TerInitKey[CurrInitServKeySeq-1][2],\
                                    global_var.TerInitKey[CurrInitServKeySeq-1][3])
        del myrsa1
        #print 'ʹ�õ���Կ������:',global_var.TerInitKey[CurrInitServKeySeq-1][0]
        #print '####���ؼ����Body-Sign:[',retn_value_sign,']'
    elif global_var.COMMAND_STR == 'beg_session': #����ǿ�ʼ�Ự
        #�Է�����Ϣ����md5
        retn_value_md5 = md5.new(global_var.retn_msg).hexdigest()
        myrsa1 = MyRSA()
        #�÷���˹�Կ�Կ�ʼ�Ự��body-sign���н���
        #print global_var.retn_bodysign,global_var.serverRasPublicKey1,global_var.serverRasModuleKey1
        my_value_md5 = myrsa1.decrypt(global_var.retn_bodysign,global_var.serverRasPublicKey1,global_var.serverRasModuleKey1)
        del myrsa1
    else:  #�������������
        #��ȡ������Ϣ��md5
        retn_value_md5 = global_var.retn_bodysign
        #��������ֶ�����md5ֵ�����㷽���ǽ�tempk�ֱ�ӵ�������Ϣ��ǰ�����md5
        tempkey = global_var.tempkey
        #����Կ׷�ӵ�json��ͷ��β
        all_value = tempkey + global_var.retn_msg + tempkey
        #��ȡ�⴮��Ϣ��md5ֵ
        my_value_md5 = md5.new(all_value).hexdigest()
    #�����ӡ�жϵĽ��
    print '===================��֤����=========================='
    #�жϷ��ص�Body-Sign���ֶ�������Ƿ�һ��
    if retn_value_md5 == my_value_md5:
        print '��֤ǩ�����:SUCCESS\n'
    else:
        print '��֤ǩ�����:FAIL\n'

#���ﶨ���˽ӿ���Ϣ�ķ��ͺͳ��滯������,���ﲻ�����������ӵ����
#���������������£�
#   url:����Ƿ��͵�ַ��������Ӵ�
#   value:��������Ҫ���͵���Ϣ��
#   tips:��ѡ�ֶΣ���Ҫ�Ǵ�ӡ��Ϣ�н���������ʾ
#����ֵ��
#   msg������˷��ص�����
#ע������Ĭ��ʹ��ȫ�ֱ����еķ����ip�Ͷ˿ڲ���
#���ﶨ����HTTP��ͷ
http_header = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}

def default_msg_send(url,value,tips='tip'):
    DEBUG = global_var.DEBUG
    serv = global_var.serv
    #print '���ӷ�����:http://%s%s' % (self.serv,url)
    #��ʼ��������
    try:
        conn = httplib.HTTPConnection(serv) #ע�����һ�������趨�˳�ʱʱ�� timeout = 5000
    except:
        print '���ӷ����� %s��ʱ,�Զ��˳�....' % serv
        sys.exit(1)
    #�����conn���벻Ϊ��
    #assert conn
    #��ӡ��װ�õ�json�����
    if DEBUG:
        print 'json request package[%s] : \n%s' % (tips,value.encode('gbk'))
    #��ʼ��������
    #Ŀǰʼ��Ҫǩ��
    #ifsign = cf.getint('cfg','ifsign')
    #�ж��Ƿ�Ϊ��ʼ�Ự,�������Ҫ�ÿͻ���˽Կ���м���
    if tips.startswith('��ʼ�Ự'):
        #cf.read('./aipay.cfg')
        #beg_sign = cf.get('cfg','beg_sign')
        #value_sign = str(beg_sign)
        myrsa1 = MyRSA()
        #����Ϣ���ݽ���MD5
        value_md5 = md5.new(value).hexdigest()
        #�ÿͻ���˽Կ����RSA����
        value_sign = myrsa1.encrypt(value_md5,global_var.clientRasPrivateKey1,global_var.clientRasModuleKey1)
        del myrsa1
    elif tips.startswith('��ԿЭ��'):
        myrsa1 = MyRSA()
        #����Ϣ���ݽ���MD5
        value_md5 = md5.new(value).hexdigest()
        #��ȡ��ǰ��ʼ��Կ���
        CurrInitKeySeq = global_var.CurrInitKeySeq
        #print '===================���Ǽ����========================='
        #�ó�ʼ��Կ˽Կ����RSA����
        #print '�ύ�ĳ�ʼ��Կ�Ǳ���ǣ�%d,��Կ��%s\t˽Կ��:%s\tģ�ǣ�%s' % (global_var.TerInitKey[CurrInitKeySeq-1][0],
        #    global_var.TerInitKey[CurrInitKeySeq-1][1],global_var.TerInitKey[CurrInitKeySeq-1][2],
        #    global_var.TerInitKey[CurrInitKeySeq-1][3])
        value_sign = myrsa1.encrypt(value_md5,global_var.TerInitKey[CurrInitKeySeq-1][2],\
                                    global_var.TerInitKey[CurrInitKeySeq-1][3])
        del myrsa1
    else:
        #��ȡͨ����Կ
        body_sign = global_var.tempkey
        #����Կ׷�ӵ�json��ͷ��β
        all_value = body_sign + value + body_sign
        #��ȡ�⴮��Ϣ��md5ֵ
        value_sign = md5.new(all_value).hexdigest()
    #����Ϣǩ�����뵽httpͷ��
    http_header['Body-Sign'] = str(value_sign)
    conn.request('POST',url,value.encode('utf8'),http_header)
    #print '>>>>���͵�Body-Sign:[',str(value_sign),']'
    #��ȡ���ض���
    try:
        response = conn.getresponse()
    except:
        print '+-+-+-+-��������+-+-���ջ�Ӧ��Ϣ��ʱ....+-+-+-+-+-+-+-+-+-\n�Զ��˳�....'
        sys.exit(1)
    if DEBUG:
        #��ӡ���
        print(response.status,response.reason)
    msg = ''
    while True:
        data = response.read(1024) #��������趨һ����С����ֹ���ص�ֵ̫��
        if len(data) == 0:
            break
        msg = msg + data
    global_var.retn_msg = msg
    #�����жϱ��뷽ʽ�������UTF-8���룬����ת��ΪGBK����
    if isinstance(msg,unicode):  #����������ж��ַ��������Ƿ�Ϊunicode����
        pass
    else:
        msg = unicode(msg,'utf-8').encode('gbk')
    if DEBUG:
        #�����ص����ݴ�ӡ����
        print('���ؽ�����£�')
        #print '<<<<���ص�Body-Sign��[',response.getheader('Body-Sign'),']'
        print(msg)
        print("===================���Ǽ����=========================\n")
    global_var.retn_bodysign = response.getheader('Body-Sign')
    #�ر�����
    conn.close()

    return msg  #���ﷵ�صİ����ִ���ʽ
    

#ͳһ��Ϣ��װ�ӿ�ʵ��
#����������£�
#  msg_index:�������ļ��е�msg��key��
#  args��������������÷�����Ϣ�Ĵ����������list����ʽ����
#�����Զ������tokenid
def get_msg_imp(msg_index,args=[]):
    #print args
    try:
        get_msg_content_fmt = getConf('msg',msg_index)
        #print get_msg_content_fmt
        if msg_index not in ['beg_session','init']:
            args.append(global_var.tokenid)
        #print args
        get_msg_str = get_msg_content_fmt % tuple(args)
    except Exception,e:
        print '��ȡ%s���ó���' % msg_index
        print '������Ϣ:',e
        sys.exit(1)
    return get_msg_str

#�����ǿ�ʼ�Ự�е�һ���ؼ�����tempkey�����ɷ���
#ʹ��ʱֻ��Ҫ���øò�������
def getTempKey():
    #���������һ��δ���ܵ�tempkey
    src_tempkey = GetRandTempKey()
    #print src_tempkey
    #����Դtempkeyд�뵽ȫ�ֱ�����
    
    global_var.tempkey = src_tempkey
    #ͨ��RSA�㷨�������ɼ��ܵ�tempkey
    serverRasPublicKey1 = global_var.serverRasPublicKey1
    serverRasModuleKey1 = global_var.serverRasModuleKey1
    myrsa1 = MyRSA()
    TempKey_en = myrsa1.encrypt(src_tempkey,serverRasPublicKey1,serverRasModuleKey1)
    del myrsa1

    return TempKey_en


#���￪ʼ����ʼ�Ự��Ϣ
#�ú����������⺯������֮ǰû��ǰ����Ϣ��tokenid�Ӹ���Ϣ�з���
#�ú�����������װ��ʼ�Ự�ı�Ҫ��Ϣ��Ȼ��ͨ��ͳһ�Ľӿڷ��͸���������
#��ڲ�����
#   url:��ַ��������Ӵ�����passport
#   ClientName:�豸���ƣ�һ��ȡIMSI
#   !!!����Ĳ���ͨ���б�������
#����ֵ��
#   tokenid���Ự����
def i_beg_session(args = []):
    #�������getTempKey()������ȡ���ܺ����ʱ��Կ
    tempkey_en = getTempKey()
    #print 'tempkey_src:',global_var.tempkey
    #����ʱkey������б���
    args.append(tempkey_en)
    #��ȡ��װ����Ϣ
    beg_session_msg = get_msg_imp('beg_session',args)
    #������Ϣ����ģ�飬��ʼ������Ϣ
    data = default_msg_send(global_var.uc,beg_session_msg,tips='��ʼ�Ự<beg_session>')
    #��ʼ�������ص���Ϣ
    try:
        beg_session_retn_dic = eval(data)
    except:
        print '��ʼ�Ự�����Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if beg_session_retn_dic['RetCode'] != 0:
        print '��ʼ�Ự��Ϣ������0������Ĳ����Զ�����...'
        sys.exit(2)
    else:
        tokenid = beg_session_retn_dic['TokenID']
        #���Ự����д��ȫ�ֱ���
        global_var.tokenid = tokenid
        #��ʼ������Ϣ���
        global_var.COMMAND_STR = 'beg_session'
        CheckBodySign()
    return beg_session_retn_dic

#���ﴦ������Ự
#
def i_end_session(args = []):
    #��ȡ��װ��Ϣ
    end_session_msg = get_msg_imp('end_session',args)
    #������Ϣ
    data = default_msg_send(global_var.uc,end_session_msg,tips='�����Ự<end_session>')
    #��ʼ�������ص���Ϣ
    try:
        end_session_retn_dic = eval(data)
    except:
        print '�����Ự�����Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if end_session_retn_dic['RetCode'] != 0:
        print '�����Ự��Ϣ������0...'
    else:
        #pass
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'end_session'
        CheckBodySign()
    return end_session_retn_dic

#�����û���Ȩ
#
def i_user_auth(args = []):
    #��ȡ��װ��Ϣ
    user_auth_msg = get_msg_imp('user_auth',args)
    #������Ϣ
    data = default_msg_send(global_var.uc,user_auth_msg,tips='�û���Ȩ<user_auth>')
    #��ʼ�������ص���Ϣ
    try:
        user_auth_retn_dic = eval(data)
    except:
        print '�û���Ȩ�����Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if user_auth_retn_dic['RetCode'] != 0:
        print '��Ȩ��Ϣ������0...'
        sys.exit(2)
    else:
        #pass
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'end_session'
        CheckBodySign()
    return user_auth_retn_dic


#������ʷ�б�
def i_get_subhis(args = []):
    #��ȡ��װ��Ϣ
    get_sub_his_msg = get_msg_imp('get_subhis',args)
    #������Ϣ
    data = default_msg_send(global_var.cc,get_sub_his_msg,tips='��ѯ������Ϣ<get_subhis>')
    #��ʼ�������ص���Ϣ
    try:
        get_subhis_retn_dic = eval(data)
    except:
        print '��ѯ������Ϣ�����Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if get_subhis_retn_dic['RetCode'] != 0:
        print '��ѯ������ʷ��Ϣ������0...'
    else:
        #pass
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'get_subhis'
        CheckBodySign()
    return get_subhis_retn_dic

#��ѯ�û����
def i_get_account(args = []):
    #��ȡ��װ��Ϣ
    get_account_msg = get_msg_imp('get_account',args)
    #������Ϣ
    data = default_msg_send(global_var.pc,get_account_msg,tips='��ѯ�û������Ϣ<get_account>')
    #��ʼ�������ص���Ϣ
    try:
        get_account_retn_dic = eval(data)
    except:
        print '��ѯ�û��������Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if get_account_retn_dic['RetCode'] != 0:
        print '��ѯ�û������Ϣ������0...'
    else:
        #pass
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'get_account'
        CheckBodySign()
    return get_account_retn_dic


#����
def i_pricing(args = []):
    #��ȡ��װ��Ϣ
    pricing_msg = get_msg_imp('pricing',args)
    #������Ϣ
    data = default_msg_send(global_var.cc,pricing_msg,tips='������Ϣ<pricing>')
    #��ʼ�������ص���Ϣ
    try:
        pricing_retn_dic = eval(data)
    except:
        print '���۳����Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if pricing_retn_dic['RetCode'] != 0:
        print '������Ϣ������0...'
    else:
        #�����صĽ�����ˮ��feeid��ʱ���
        global_var.retn_transid = pricing_retn_dic['Body']['TransID']
        global_var.retn_feeid = pricing_retn_dic['Body']['FeeinfoList'][0]['FeeID']
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'pricing'
        CheckBodySign()
    return pricing_retn_dic

#�Զ�֧��
def i_pay(args = []):
    #��ȡ��װ��Ϣ
    #���ｫ�Զ�֧���Ĳ������ģ��������õ�Ϊ׼
    #print args
    if len(global_var.retn_transid) == 0 or len(global_var.retn_feeid) == 0:
        print '����ִ��pricing������ִ��֧������...'
        sys.exit(1)
    args.insert(0,global_var.retn_transid)
    args.insert(1,global_var.retn_feeid)
    pay_msg = get_msg_imp('pay',args)
    #������Ϣ
    data = default_msg_send(global_var.pc,pay_msg,tips='�Զ�֧����Ϣ<pay>')
    #��ʼ�������ص���Ϣ
    try:
        pay_retn_dic = eval(data)
    except:
        print '֧�������Զ��˳�...'
        sys.exit(1)
    #�������ֵ��Ϊ0����˵���д��������Զ��˳�
    if pay_retn_dic['RetCode'] != 0:
        print '֧��������0...'
    else:
        #����ʱ��ŵĽ�����ˮ��feeid���
        global_var.retn_transid = ''
        global_var.retn_feeid = ''
        #��ʼ������Ϣ���        
        global_var.COMMAND_STR = 'pay'
        CheckBodySign()
    return pay_retn_dic
