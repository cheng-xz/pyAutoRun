# -*- coding:gbk -*-
#filename: mainCtrol.py
#该程序可以直接在2.7版本运行
#--------------------------------------
#   author : 成协主
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#该模块是主控模块，控制其他模块的运行
from coreProc import *
from mPublic import *
import coreProc
import global_var
from ConfigParser import ConfigParser
import sys
from checkData import *

#这里定义需要执行的函数列表，这些内容将会按顺序被调用
task_func = []
#这里定义函数中所需要的参数，以列表来保持列表中的内容
task_args = []
#这里定义全局的需要执行的任务编号
task_index = []

#该模块进行系统启动时的初始化工作，主要是读入配置文件的内容，并写入全局变量中
def _init():
    #获取调试开关
    global_var.DEBUG = getConf('cfg','debug',op=1)
    #获取是否有一个会话的开关
    global_var.onesession = getConf('cfg','onesession',op=1)
    #获取后台服务端的连接信息
    global_var.serv = getConf('cfg','serv') + ':' + getConf('cfg','serv_port')
    #获取数据库信息
    db_str = getConf('cfg','db_var')
    db_lst = db_str.split(',')
    global_var.db['host'] = db_lst[0]
    global_var.db['port'] = db_lst[1]
    global_var.db['user'] = db_lst[2]
    global_var.db['passwd'] = db_lst[3]
    global_var.db['db'] = db_lst[4]
    #获取后台服务连接串信息
    global_var.uc = getConf('cfg','serv_uc')
    global_var.cc = getConf('cfg','serv_cc')
    global_var.pc = getConf('cfg','serv_pc')
    global_var.sc = getConf('cfg','serv_sc')
    #获取客户端标识信息
    global_var.terminalid = getConf('cfg','terminalid')
    #载入服务端的公钥和模信息
    global_var.serverRasPublicKey1 = getConf('key','serverraspublickey1',f='./temp.cfg')
    global_var.serverRasModuleKey1 = getConf('key','serverrasmodulekey1',f='./temp.cfg')
    #获取参数常量表
    const_ls = getConf('const',op=2)
    for i in const_ls:
        global_var.const_dic[i[1]] = i[0]
        global_var.const_dic_r[i[0]] = i[1]
    #打印结果
    print global_var.serv
    print global_var.const_dic
    

#下面开始读取任务
#输入参数：
#       target_index：需要指定的任务编号
def _readTask(target_index):
    global task_func
    global task_args
    global task_index
    global onesession
    
    #获取关联信息
    target_arg_lst = []
    rela_index_lst = getConf('rela','rela_'+target_index,f='./task.cfg')
    if rela_index_lst == -1 or len(rela_index_lst) == 0:    #如果读取不到项,说明没有关联信息
        task_func.append('i_'+global_var.const_dic.get(target_index))
        #这里读取参数表
        rela_only_c_arg = getConf('cus_arg','c_arg_'+target_index,f='./task.cfg')
        if rela_only_c_arg == -1 or len(rela_only_c_arg) == 0: #如果目标项的参数在自定义参数表中没有定义，则尝试从默认参数配置项中读取
            rela_only_c_arg = getConf('default_arg','d_arg_'+target_index,f='./task.cfg')
            if rela_only_c_arg == -1 or len(rela_only_c_arg) == 0: #如果获取失败或者是空项，则参数为空
                rela_item_d_arg_lst = []
            else:
                rela_item_d_arg_lst = rela_only_c_arg.split(',')
        else:
            rela_item_d_arg_lst = rela_only_c_arg.split(',')
        task_args.append(rela_item_d_arg_lst)
    else: #说明有关联信息
        rela_index_lst_lst = rela_index_lst.split(',')
        for rela_item_ind in rela_index_lst_lst: #检索关联表的序列
            #获取对应的函数名称
            rela_item_func = 'i_' + global_var.const_dic[rela_item_ind]
            if rela_item_ind == target_index: #如果这里是目标任务的编号，则其配置项从自定义配置项中获取
                rela_item_d_arg = getConf('cus_arg','c_arg_'+target_index,f='./task.cfg')
                if rela_item_d_arg == -1 or len(rela_item_d_arg) == 0: #如果目标项的参数在自定义参数表中没有定义，则尝试从默认参数配置项中读取
                    rela_item_d_arg = getConf('default_arg','d_arg_'+rela_item_ind,f='./task.cfg')
            else:
                rela_item_d_arg = getConf('default_arg','d_arg_'+rela_item_ind,f='./task.cfg')
            if rela_item_d_arg == -1 or len(rela_item_d_arg) == 0: #如果获取失败或者是空项，则参数为空
                rela_item_d_arg_lst = []
            else:
                rela_item_d_arg_lst = rela_item_d_arg.split(',')
            #将函数名称字串和参数列表加入任务表中
            #这里增加重复性的关联查询
            if global_var.onesession:
                try:
                    task_func.index(rela_item_func)
                except ValueError: #如果之前没有相同的前置关联
                    task_func.append(rela_item_func)
                    task_args.append(rela_item_d_arg_lst)
                else:
                    try:
                        task_index.index(rela_item_ind)
                    except:
                        pass
                    else:  #目标任务不能放在最后执行
                        task_func.insert(-1,rela_item_func)
                        task_args.insert(-1,rela_item_d_arg_lst)
            else:
                task_func.append(rela_item_func)
                task_args.append(rela_item_d_arg_lst)

def _GetTask():
    global task_index
    #获取目标任务索引项
    target_index = getConf('task','task_lst',f='./task.cfg')
    target_index_lst = target_index.split(',')
    #这里将编号放入全局编号中
    task_index = target_index_lst
    for targe_index_item in target_index_lst:
        _readTask(targe_index_item)


            
#根据字串和参数传递执行
def _exec(func_str,args):
    func = getattr(coreProc,func_str)
    return func(args)

#下面是主流程控制
#开始执行初始化信息
print '开始读取配置信息，初始化数据...'
_init()
print '开始读取任务...'
_GetTask()
#这里打印待读取的任务
print '任务如下：'
task_i = 0
for task_n in task_func:
    print '[%d]%s' % (task_i,task_n)
    task_i += 1
  
print '参数列表如下：'
task_i = 0  
for arg_n in task_args:
    print task_i,arg_n
    task_i += 1
#开始执行任务
print '开始执行任务...'
task_i = 0
for func_item in task_func:
    #获取全局表中保存的参数列表
    func_arg = task_args[task_i]
    #运行该任务
    retn_data = _exec(func_item,func_arg)
    cmdid = global_var.const_dic_r[global_var.COMMAND_STR]
    #print '命令字段：',cmdid
    #判断当前需要执行的任务编号是不是在定义的任务编号之中，而不是关联任务
    try:
        tmp = task_index.index(cmdid)
    except ValueError: #如果不在则不作处理
        pass
    else: #否则调用检查
        print '-*-*-*-*-*-*-*-*这里检查返回值-*-*-*-*-*-*-*-*-*-*-*-*'
        mainCheck(retn_data,cmdid)
        print '-*-*-*-*-*-*-*-*这里检查返回值-*-*-*-*-*-*-*-*-*-*-*-*\n'
    #计数器变化
    task_i += 1

    
raw_input('按任意键退出...')
