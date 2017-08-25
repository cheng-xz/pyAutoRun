#-*- coding:gbk -*-
#filename: mPublic.py
#该程序可以直接在2.7版本运行
#--------------------------------------
#   author : 成协主
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#该模块是一些与核心消息处理函数关系不大的外部函数，主要是用于对python内部模块的简单封装

'''
    这里主要是一些公共函数，供外部程序调用
'''

#需要导入的模块
from ConfigParser import ConfigParser
import random
import jpype
import pyDes
import MySQLdb
import string
import sys


#该函数主要用于从配置项中配置信息
#参数说明：
#   seg：节信息，也就是中括号括起来的串
#   key：关键字段信息，是中括号下面的等号左边的内容
#   op：用于标明获取的内容是整数还是字串，如果是0表示字串，1则调用获取整数的方法,2表示读取该键下所有的值
#   f：需要从那个文件读配置信息，默认值是aipay.cfg这个文件
#返回值：
#   retn:用于读取到的值
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
            print '传递参数有误[op超出限定值]，请检查...'
            return -1
    except:
        print '读取配置信息出错，[%s]->[%s]' % (seg,key)
        return -1

#这个是用于3des加密的一个模块，加密参数是triple_des/ECB/0
#加密方法的数据是直接填入就可以了，如需要对123456加密，直接传入123456即可，返回的数据是16进制编码
#解密传入的是经过16进制编码的数据，返回的是源码
#在进行加解密过程中需要传入
#传入参数：
class My3DES():
    """加密模块
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


#封装自定义的RSA生成方法
#这里不是使用的python的模块，而是通过调用java的class文件
#这里用到了RSAUtil.class这个文件，在使用时需要将该文件与本文件放在同一位置
#注：这里只是封装了相应的接口，在使用时需要自己传入参数来进行加解密
class MyRSA():
    #启动java虚拟机
    def __init__(self):
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=.")
        self.BigIntCls = jpype.JClass('java.math.BigInteger')
        self.RSACls = jpype.JClass('RSAUtil')
    #使用公钥加密
    def encrypt(self,data,e,n):
        BigInt_e = self.BigIntCls(e)
        BigInt_n = self.BigIntCls(n)
        return self.RSACls.encrypt(data,BigInt_e,BigInt_n)
    #使用私钥解密
    def decrypt(self,data,d,n):
        BigInt_d = self.BigIntCls(d)
        BigInt_n = self.BigIntCls(n)
        return self.RSACls.decrypt(data,BigInt_d,BigInt_n)
    #生成随机密钥
    def randomrsa(self):
        p = self.RSACls.getPrimes()
        q = self.RSACls.getPrimes()
        ran = self.RSACls.getRan(p,q)
        pKey = self.RSACls.getPublicKey(ran)
        priKey = self.RSACls.getPrivateKey(ran,pKey)
        n = self.RSACls.getN(p,q)
        return str(pKey),str(priKey),str(n)
    #结束java虚拟机
    def __del__(self):
        pass
        #if jpype.isJVMStarted():
        #    jpype.shutdownJVM()

#这里是用于简单加解密的方法
#这里是调用了jasypt-1.7.1.jar这个包中的类文件        
#注意：每次对于同一个串加密后的结果都不一样，但是解密的结果都是可以解析出来的
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

#生成24位的随机密钥，也就是TempKey
#这里通过python的随机数类random来生成    
def GetRandTempKey():
    rand_ls = random.sample([c for c in string.hexdigits * 2],24)
    tempkey = ''
    for c in rand_ls:
        tempkey = tempkey + c
    return tempkey.lower()

#这个函数主要是用来处理查询数据库的请求，也处理注册时的请求
#输入参数：
#   self.db:一个dic类型数据，其中包含了数据库连接所需要的信息
#   sql：需要执行的sql
#   op:需要做的操作，其中0表示查询，1表示插入，2表示修改
#返回值：
#   result：如果是查询操作，就将查询的结果返回，如果是其他操作，则将影响的行数返回
def querySQL(db,sql,op=0):
    try:  #加入出错的处理
        conn = MySQLdb.connect(db['host'],db['user'],db['passwd'],db['db'],port=db['port'],charset="gbk")
    except Exception, e:
        print e
        sys.exit(1)
    #获得一个查询游标
    cur = conn.cursor()
    #这里设置编码，防止中文乱码
    #cur.execute('set names utf8')
    #cur.execute('set character_set_client=utf8')
    #cur.execute('set character_set_connection=utf8')
    #cur.execute('set character_set_results=gbk')
    try:
        n = cur.execute(sql)
        if op == 0: #这里需要返回结果
            result = cur.fetchall()  #这里只获取一条记录即可
        else: #这里得到受影响的返回行
            conn.commit()  #将修改提交到数据库中
    except Exception,e:
        print '数据库处理报错 %s' % e
    finally:
        cur.close()
        conn.close()
    if op ==0:
        if not result: #没有找到记录，返回0
            return ''
        else: #直接将查到的IMSI返回
            #这里返回一个元组
            return result
    else:
        return n #将受影响的行返回
