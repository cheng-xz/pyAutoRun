#-*- coding:gbk -*-
#filename: mPublic.py
#�ó������ֱ����2.7�汾����
#--------------------------------------
#   author : ��Э��
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#��ģ����һЩ�������Ϣ��������ϵ������ⲿ��������Ҫ�����ڶ�python�ڲ�ģ��ļ򵥷�װ

'''
    ������Ҫ��һЩ�������������ⲿ�������
'''

#��Ҫ�����ģ��
from ConfigParser import ConfigParser
import random
import jpype
import pyDes
import MySQLdb
import string
import sys


#�ú�����Ҫ���ڴ���������������Ϣ
#����˵����
#   seg������Ϣ��Ҳ�����������������Ĵ�
#   key���ؼ��ֶ���Ϣ��������������ĵȺ���ߵ�����
#   op�����ڱ�����ȡ�����������������ִ��������0��ʾ�ִ���1����û�ȡ�����ķ���,2��ʾ��ȡ�ü������е�ֵ
#   f����Ҫ���Ǹ��ļ���������Ϣ��Ĭ��ֵ��aipay.cfg����ļ�
#����ֵ��
#   retn:���ڶ�ȡ����ֵ
def getConf(seg,key='',op=0,f='./aipay.cfg'):
    cf = ConfigParser()
    try:
        cf.read(f)
        if op == 0:
            return cf.get(seg,key)
        elif op == 1:
            return cf.getint(seg,key)
        elif op == 2: #
            return cf.items(seg)
        else:
            print '���ݲ�������[op�����޶�ֵ]������...'
            return -1
    except:
        print '��ȡ������Ϣ����[%s]->[%s]' % (seg,key)
        return -1

#���������3des���ܵ�һ��ģ�飬���ܲ�����triple_des/ECB/0
#���ܷ�����������ֱ������Ϳ����ˣ�����Ҫ��123456���ܣ�ֱ�Ӵ���123456���ɣ����ص�������16���Ʊ���
#���ܴ�����Ǿ���16���Ʊ�������ݣ����ص���Դ��
#�ڽ��мӽ��ܹ�������Ҫ����
#���������
class My3DES():
    """����ģ��
    """
    def __init__(self,key):
        self.en_key = key
        #self.en_key = '138152311337088112957278'
        self._3DES = pyDes.triple_des(self.en_key, pyDes.ECB,b"\0\0\0\0\0\0\0\0", pad = '\0', padmode = pyDes.PAD_NORMAL)
        #self._3DES = pyDes.triple_des('12345678abcdefgh87654321', pyDes.CBC,'123456', pad = None, padmode = pyDes.PAD_PKCS5)
    def Encrypt(self,data):
        e = self._3DES.encrypt(data)
        #return base64.b64encode(e)
        return e.encode('hex')

    def Decrypt(self,enData):
        #d = base64.b64decode(enData)
        d = enData.decode('hex')
        return self._3DES.decrypt(d)


#��װ�Զ����RSA���ɷ���
#���ﲻ��ʹ�õ�python��ģ�飬����ͨ������java��class�ļ�
#�����õ���RSAUtil.class����ļ�����ʹ��ʱ��Ҫ�����ļ��뱾�ļ�����ͬһλ��
#ע������ֻ�Ƿ�װ����Ӧ�Ľӿڣ���ʹ��ʱ��Ҫ�Լ�������������мӽ���
class MyRSA():
    #����java�����
    def __init__(self):
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=.")
        self.BigIntCls = jpype.JClass('java.math.BigInteger')
        self.RSACls = jpype.JClass('RSAUtil')
    #ʹ�ù�Կ����
    def encrypt(self,data,e,n):
        BigInt_e = self.BigIntCls(e)
        BigInt_n = self.BigIntCls(n)
        return self.RSACls.encrypt(data,BigInt_e,BigInt_n)
    #ʹ��˽Կ����
    def decrypt(self,data,d,n):
        BigInt_d = self.BigIntCls(d)
        BigInt_n = self.BigIntCls(n)
        return self.RSACls.decrypt(data,BigInt_d,BigInt_n)
    #���������Կ
    def randomrsa(self):
        p = self.RSACls.getPrimes()
        q = self.RSACls.getPrimes()
        ran = self.RSACls.getRan(p,q)
        pKey = self.RSACls.getPublicKey(ran)
        priKey = self.RSACls.getPrivateKey(ran,pKey)
        n = self.RSACls.getN(p,q)
        return str(pKey),str(priKey),str(n)
    #����java�����
    def __del__(self):
        pass
        #if jpype.isJVMStarted():
        #    jpype.shutdownJVM()

#���������ڼ򵥼ӽ��ܵķ���
#�����ǵ�����jasypt-1.7.1.jar������е����ļ�        
#ע�⣺ÿ�ζ���ͬһ�������ܺ�Ľ������һ�������ǽ��ܵĽ�����ǿ��Խ���������
class MyEnc():
    def __init__(self):
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=jasypt-1.7.1.jar")
        self.BasicTextEncryptor = jpype.JPackage('org').jasypt.util.text.BasicTextEncryptor
        self.BasicTextEncryptor_inst = self.BasicTextEncryptor()
        self.BasicTextEncryptor_inst.setPassword("WWW.IAPPPAY.COM_YANGFENG")
    def __del__(self):
        pass
    def encrypt(self,msg):
        return self.BasicTextEncryptor_inst.encrypt(msg)
    def decrypt(self,encryptedmsg):
        return self.BasicTextEncryptor_inst.decrypt(encryptedmsg)

#����24λ�������Կ��Ҳ����TempKey
#����ͨ��python���������random������    
def GetRandTempKey():
    rand_ls = random.sample([c for c in string.hexdigits * 2],24)
    tempkey = ''
    for c in rand_ls:
        tempkey = tempkey + c
    return tempkey.lower()

#���������Ҫ�����������ѯ���ݿ������Ҳ����ע��ʱ������
#���������
#   self.db:һ��dic�������ݣ����а��������ݿ���������Ҫ����Ϣ
#   sql����Ҫִ�е�sql
#   op:��Ҫ���Ĳ���������0��ʾ��ѯ��1��ʾ���룬2��ʾ�޸�
#����ֵ��
#   result������ǲ�ѯ�������ͽ���ѯ�Ľ�����أ������������������Ӱ�����������
def querySQL(db,sql,op=0):
    try:  #�������Ĵ���
        conn = MySQLdb.connect(db['host'],db['user'],db['passwd'],db['db'],port=db['port'],charset="gbk")
    except Exception, e:
        print e
        sys.exit(1)
    #���һ����ѯ�α�
    cur = conn.cursor()
    #�������ñ��룬��ֹ��������
    #cur.execute('set names utf8')
    #cur.execute('set character_set_client=utf8')
    #cur.execute('set character_set_connection=utf8')
    #cur.execute('set character_set_results=gbk')
    try:
        n = cur.execute(sql)
        if op == 0: #������Ҫ���ؽ��
            result = cur.fetchall()  #����ֻ��ȡһ����¼����
        else: #����õ���Ӱ��ķ�����
            conn.commit()  #���޸��ύ�����ݿ���
    except Exception,e:
        print '���ݿ⴦���� %s' % e
    finally:
        cur.close()
        conn.close()
    if op ==0:
        if not result: #û���ҵ���¼������0
            return ''
        else: #ֱ�ӽ��鵽��IMSI����
            #���ﷵ��һ��Ԫ��
            return result
    else:
        return n #����Ӱ����з���
