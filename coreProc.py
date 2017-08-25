#-*- coding:gbk -*-
#filename: coreProc.py
#该程序可以直接在2.7版本运行
#--------------------------------------
#   author : 成协主
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

from mPublic import *
import global_var
import sys
import httplib
import md5

#该模块是核心业务处理模块，用于处理消息

'''
    这里是核心业务处理模块，用于所有系统骨架的搭建
'''

#这个函数用来检测返回消息的Body-Sign是否正确
#需要的参数有：
#   返回的Body-Sign
#   返回的msg
#   进行的选项
def CheckBodySign():
    if global_var.COMMAND_STR == 'init':  #如果是密钥协商
        myrsa1 = MyRSA()
        #对返回消息进行md5
        retn_value_md5 = md5.new(global_var.retn_msg).hexdigest()
        #获取当前初始密钥编号
        CurrInitServKeySeq = global_var.CurrInitServKeySeq
        #用初始密钥私钥对返回的BODY-SIGN进行解密
        my_value_md5 = myrsa1.decrypt(global_var.retn_bodysign,global_var.TerInitKey[CurrInitServKeySeq-1][2],\
                                    global_var.TerInitKey[CurrInitServKeySeq-1][3])
        del myrsa1
        #print '使用的密钥编码是:',global_var.TerInitKey[CurrInitServKeySeq-1][0]
        #print '####本地计算的Body-Sign:[',retn_value_sign,']'
    elif global_var.COMMAND_STR == 'beg_session': #如果是开始会话
        #对返回消息进行md5
        retn_value_md5 = md5.new(global_var.retn_msg).hexdigest()
        myrsa1 = MyRSA()
        #用服务端公钥对开始会话的body-sign进行解密
        #print global_var.retn_bodysign,global_var.serverRasPublicKey1,global_var.serverRasModuleKey1
        my_value_md5 = myrsa1.decrypt(global_var.retn_bodysign,global_var.serverRasPublicKey1,global_var.serverRasModuleKey1)
        del myrsa1
    else:  #如果是其他类型
        #获取返回消息的md5
        retn_value_md5 = global_var.retn_bodysign
        #下面的是手动计算md5值，计算方法是将tempk分别加到返回消息的前后进行md5
        tempkey = global_var.tempkey
        #将密钥追加到json的头和尾
        all_value = tempkey + global_var.retn_msg + tempkey
        #获取这串消息的md5值
        my_value_md5 = md5.new(all_value).hexdigest()
    #下面打印判断的结果
    print '===================验证返回=========================='
    #判断返回的Body-Sign和手动计算的是否一致
    if retn_value_md5 == my_value_md5:
        print '验证签名结果:SUCCESS\n'
    else:
        print '验证签名结果:FAIL\n'

#这里定义了接口消息的发送和常规化处理方法,这里不包含建立连接的语句
#这里的输入参数如下：
#   url:这个是发送地址后面的连接串
#   value:这里是需要发送的消息串
#   tips:可选字段，主要是打印消息中进行类型提示
#返回值：
#   msg：服务端返回的数据
#注：这里默认使用全局变量中的服务端ip和端口参数
#这里定义了HTTP的头
http_header = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}

def default_msg_send(url,value,tips='tip'):
    DEBUG = global_var.DEBUG
    serv = global_var.serv
    #print '连接服务器:http://%s%s' % (self.serv,url)
    #开始建立连接
    try:
        conn = httplib.HTTPConnection(serv) #注：最后一个参数设定了超时时间 timeout = 5000
    except:
        print '连接服务器 %s超时,自动退出....' % serv
        sys.exit(1)
    #这里的conn必须不为空
    #assert conn
    #打印组装好的json请求包
    if DEBUG:
        print 'json request package[%s] : \n%s' % (tips,value.encode('gbk'))
    #开始发送请求
    #目前始终要签名
    #ifsign = cf.getint('cfg','ifsign')
    #判断是否为开始会话,如果是需要用客户端私钥进行加密
    if tips.startswith('开始会话'):
        #cf.read('./aipay.cfg')
        #beg_sign = cf.get('cfg','beg_sign')
        #value_sign = str(beg_sign)
        myrsa1 = MyRSA()
        #对消息内容进行MD5
        value_md5 = md5.new(value).hexdigest()
        #用客户端私钥进行RSA加密
        value_sign = myrsa1.encrypt(value_md5,global_var.clientRasPrivateKey1,global_var.clientRasModuleKey1)
        del myrsa1
    elif tips.startswith('密钥协商'):
        myrsa1 = MyRSA()
        #对消息内容进行MD5
        value_md5 = md5.new(value).hexdigest()
        #获取当前初始密钥编号
        CurrInitKeySeq = global_var.CurrInitKeySeq
        #print '===================我是间隔线========================='
        #用初始密钥私钥进行RSA加密
        #print '提交的初始密钥是编号是：%d,公钥：%s\t私钥是:%s\t模是：%s' % (global_var.TerInitKey[CurrInitKeySeq-1][0],
        #    global_var.TerInitKey[CurrInitKeySeq-1][1],global_var.TerInitKey[CurrInitKeySeq-1][2],
        #    global_var.TerInitKey[CurrInitKeySeq-1][3])
        value_sign = myrsa1.encrypt(value_md5,global_var.TerInitKey[CurrInitKeySeq-1][2],\
                                    global_var.TerInitKey[CurrInitKeySeq-1][3])
        del myrsa1
    else:
        #获取通信密钥
        body_sign = global_var.tempkey
        #将密钥追加到json的头和尾
        all_value = body_sign + value + body_sign
        #获取这串消息的md5值
        value_sign = md5.new(all_value).hexdigest()
    #将消息签名放入到http头中
    http_header['Body-Sign'] = str(value_sign)
    conn.request('POST',url,value.encode('utf8'),http_header)
    #print '>>>>发送的Body-Sign:[',str(value_sign),']'
    #获取返回对象
    try:
        response = conn.getresponse()
    except:
        print '+-+-+-+-哈哈。。+-+-接收回应消息超时....+-+-+-+-+-+-+-+-+-\n自动退出....'
        sys.exit(1)
    if DEBUG:
        #打印结果
        print(response.status,response.reason)
    msg = ''
    while True:
        data = response.read(1024) #这里最好设定一个大小，防止返回的值太大
        if len(data) == 0:
            break
        msg = msg + data
    global_var.retn_msg = msg
    #这里判断编码方式，如果是UTF-8编码，则将其转换为GBK编码
    if isinstance(msg,unicode):  #这个函数是判断字符串编码是否为unicode编码
        pass
    else:
        msg = unicode(msg,'utf-8').encode('gbk')
    if DEBUG:
        #将返回的数据打印出来
        print('返回结果如下：')
        #print '<<<<返回的Body-Sign：[',response.getheader('Body-Sign'),']'
        print(msg)
        print("===================我是间隔线=========================\n")
    global_var.retn_bodysign = response.getheader('Body-Sign')
    #关闭连接
    conn.close()

    return msg  #这里返回的包的字串形式
    

#统一消息组装接口实现
#输入参数如下：
#  msg_index:在配置文件中的msg的key串
#  args：这个是用于设置返回消息的传入参数，以list的形式传递
#这里自动添加了tokenid
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
        print '获取%s配置出错' % msg_index
        print '出错信息:',e
        sys.exit(1)
    return get_msg_str

#这里是开始会话中的一个关键参数tempkey的生成方法
#使用时只需要调用该参数即可
def getTempKey():
    #先随机生成一个未加密的tempkey
    src_tempkey = GetRandTempKey()
    #print src_tempkey
    #将该源tempkey写入到全局变量中
    
    global_var.tempkey = src_tempkey
    #通过RSA算法加密生成加密的tempkey
    serverRasPublicKey1 = global_var.serverRasPublicKey1
    serverRasModuleKey1 = global_var.serverRasModuleKey1
    myrsa1 = MyRSA()
    TempKey_en = myrsa1.encrypt(src_tempkey,serverRasPublicKey1,serverRasModuleKey1)
    del myrsa1

    return TempKey_en


#这里开始处理开始会话消息
#该函数属于特殊函数，其之前没有前置消息，tokenid从该消息中返回
#该函数会首先组装开始会话的必要消息，然后通过统一的接口发送给网络服务端
#入口参数：
#   url:地址后面的连接串，如passport
#   ClientName:设备名称，一般取IMSI
#   !!!这里的参数通过列表来传递
#返回值：
#   tokenid：会话令牌
def i_beg_session(args = []):
    #这里调用getTempKey()函数获取加密后的临时密钥
    tempkey_en = getTempKey()
    #print 'tempkey_src:',global_var.tempkey
    #将临时key加入的列表中
    args.append(tempkey_en)
    #获取组装好消息
    beg_session_msg = get_msg_imp('beg_session',args)
    #调用消息发送模块，开始发送消息
    data = default_msg_send(global_var.uc,beg_session_msg,tips='开始会话<beg_session>')
    #开始解析返回的消息
    try:
        beg_session_retn_dic = eval(data)
    except:
        print '开始会话出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if beg_session_retn_dic['RetCode'] != 0:
        print '开始会话消息不返回0，后面的操作自动忽略...'
        sys.exit(2)
    else:
        tokenid = beg_session_retn_dic['TokenID']
        #将会话令牌写入全局变量
        global_var.tokenid = tokenid
        #开始返回消息检查
        global_var.COMMAND_STR = 'beg_session'
        CheckBodySign()
    return beg_session_retn_dic

#这里处理结束会话
#
def i_end_session(args = []):
    #获取组装消息
    end_session_msg = get_msg_imp('end_session',args)
    #发送消息
    data = default_msg_send(global_var.uc,end_session_msg,tips='结束会话<end_session>')
    #开始解析返回的消息
    try:
        end_session_retn_dic = eval(data)
    except:
        print '结束会话出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if end_session_retn_dic['RetCode'] != 0:
        print '结束会话消息不返回0...'
    else:
        #pass
        #开始返回消息检查        
        global_var.COMMAND_STR = 'end_session'
        CheckBodySign()
    return end_session_retn_dic

#处理用户鉴权
#
def i_user_auth(args = []):
    #获取组装消息
    user_auth_msg = get_msg_imp('user_auth',args)
    #发送消息
    data = default_msg_send(global_var.uc,user_auth_msg,tips='用户鉴权<user_auth>')
    #开始解析返回的消息
    try:
        user_auth_retn_dic = eval(data)
    except:
        print '用户鉴权出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if user_auth_retn_dic['RetCode'] != 0:
        print '鉴权消息不返回0...'
        sys.exit(2)
    else:
        #pass
        #开始返回消息检查        
        global_var.COMMAND_STR = 'end_session'
        CheckBodySign()
    return user_auth_retn_dic


#交易历史列表
def i_get_subhis(args = []):
    #获取组装消息
    get_sub_his_msg = get_msg_imp('get_subhis',args)
    #发送消息
    data = default_msg_send(global_var.cc,get_sub_his_msg,tips='查询交易信息<get_subhis>')
    #开始解析返回的消息
    try:
        get_subhis_retn_dic = eval(data)
    except:
        print '查询订购信息出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if get_subhis_retn_dic['RetCode'] != 0:
        print '查询交易历史消息不返回0...'
    else:
        #pass
        #开始返回消息检查        
        global_var.COMMAND_STR = 'get_subhis'
        CheckBodySign()
    return get_subhis_retn_dic

#查询用户余额
def i_get_account(args = []):
    #获取组装消息
    get_account_msg = get_msg_imp('get_account',args)
    #发送消息
    data = default_msg_send(global_var.pc,get_account_msg,tips='查询用户余额信息<get_account>')
    #开始解析返回的消息
    try:
        get_account_retn_dic = eval(data)
    except:
        print '查询用户余额出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if get_account_retn_dic['RetCode'] != 0:
        print '查询用户余额消息不返回0...'
    else:
        #pass
        #开始返回消息检查        
        global_var.COMMAND_STR = 'get_account'
        CheckBodySign()
    return get_account_retn_dic


#批价
def i_pricing(args = []):
    #获取组装消息
    pricing_msg = get_msg_imp('pricing',args)
    #发送消息
    data = default_msg_send(global_var.cc,pricing_msg,tips='批价信息<pricing>')
    #开始解析返回的消息
    try:
        pricing_retn_dic = eval(data)
    except:
        print '批价出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if pricing_retn_dic['RetCode'] != 0:
        print '批价消息不返回0...'
    else:
        #将返回的交易流水和feeid临时存放
        global_var.retn_transid = pricing_retn_dic['Body']['TransID']
        global_var.retn_feeid = pricing_retn_dic['Body']['FeeinfoList'][0]['FeeID']
        #开始返回消息检查        
        global_var.COMMAND_STR = 'pricing'
        CheckBodySign()
    return pricing_retn_dic

#自动支付
def i_pay(args = []):
    #获取组装消息
    #这里将自动支付的参数更改，不以配置的为准
    #print args
    if len(global_var.retn_transid) == 0 or len(global_var.retn_feeid) == 0:
        print '请先执行pricing流程再执行支付流程...'
        sys.exit(1)
    args.insert(0,global_var.retn_transid)
    args.insert(1,global_var.retn_feeid)
    pay_msg = get_msg_imp('pay',args)
    #发送消息
    data = default_msg_send(global_var.pc,pay_msg,tips='自动支付信息<pay>')
    #开始解析返回的消息
    try:
        pay_retn_dic = eval(data)
    except:
        print '支付出错，自动退出...'
        sys.exit(1)
    #如果返回值不为0，则说明有错误发生，自动退出
    if pay_retn_dic['RetCode'] != 0:
        print '支付不返回0...'
    else:
        #将临时存放的交易流水和feeid清空
        global_var.retn_transid = ''
        global_var.retn_feeid = ''
        #开始返回消息检查        
        global_var.COMMAND_STR = 'pay'
        CheckBodySign()
    return pay_retn_dic
