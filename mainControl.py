# -*- coding:gbk -*-
#filename: mainCtrol.py
#�ó������ֱ����2.7�汾����
#--------------------------------------
#   author : ��Э��
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

#��ģ��������ģ�飬��������ģ�������
from coreProc import *
from mPublic import *
import coreProc
import global_var
from ConfigParser import ConfigParser
import sys
from checkData import *

#���ﶨ����Ҫִ�еĺ����б���Щ���ݽ��ᰴ˳�򱻵���
task_func = []
#���ﶨ�庯��������Ҫ�Ĳ��������б��������б��е�����
task_args = []
#���ﶨ��ȫ�ֵ���Ҫִ�е�������
task_index = []

#��ģ�����ϵͳ����ʱ�ĳ�ʼ����������Ҫ�Ƕ��������ļ������ݣ���д��ȫ�ֱ�����
def _init():
    #��ȡ���Կ���
    global_var.DEBUG = getConf('cfg','debug',op=1)
    #��ȡ�Ƿ���һ���Ự�Ŀ���
    global_var.onesession = getConf('cfg','onesession',op=1)
    #��ȡ��̨����˵�������Ϣ
    global_var.serv = getConf('cfg','serv') + ':' + getConf('cfg','serv_port')
    #��ȡ���ݿ���Ϣ
    db_str = getConf('cfg','db_var')
    db_lst = db_str.split(',')
    global_var.db['host'] = db_lst[0]
    global_var.db['port'] = db_lst[1]
    global_var.db['user'] = db_lst[2]
    global_var.db['passwd'] = db_lst[3]
    global_var.db['db'] = db_lst[4]
    #��ȡ��̨�������Ӵ���Ϣ
    global_var.uc = getConf('cfg','serv_uc')
    global_var.cc = getConf('cfg','serv_cc')
    global_var.pc = getConf('cfg','serv_pc')
    global_var.sc = getConf('cfg','serv_sc')
    #��ȡ�ͻ��˱�ʶ��Ϣ
    global_var.terminalid = getConf('cfg','terminalid')
    #�������˵Ĺ�Կ��ģ��Ϣ
    global_var.serverRasPublicKey1 = getConf('key','serverraspublickey1',f='./temp.cfg')
    global_var.serverRasModuleKey1 = getConf('key','serverrasmodulekey1',f='./temp.cfg')
    #��ȡ����������
    const_ls = getConf('const',op=2)
    for i in const_ls:
        global_var.const_dic[i[1]] = i[0]
        global_var.const_dic_r[i[0]] = i[1]
    #��ӡ���
    print global_var.serv
    print global_var.const_dic
    

#���濪ʼ��ȡ����
#���������
#       target_index����Ҫָ����������
def _readTask(target_index):
    global task_func
    global task_args
    global task_index
    global onesession
    
    #��ȡ������Ϣ
    target_arg_lst = []
    rela_index_lst = getConf('rela','rela_'+target_index,f='./task.cfg')
    if rela_index_lst == -1 or len(rela_index_lst) == 0:    #�����ȡ������,˵��û�й�����Ϣ
        task_func.append('i_'+global_var.const_dic.get(target_index))
        #�����ȡ������
        rela_only_c_arg = getConf('cus_arg','c_arg_'+target_index,f='./task.cfg')
        if rela_only_c_arg == -1 or len(rela_only_c_arg) == 0: #���Ŀ����Ĳ������Զ����������û�ж��壬���Դ�Ĭ�ϲ����������ж�ȡ
            rela_only_c_arg = getConf('default_arg','d_arg_'+target_index,f='./task.cfg')
            if rela_only_c_arg == -1 or len(rela_only_c_arg) == 0: #�����ȡʧ�ܻ����ǿ�������Ϊ��
                rela_item_d_arg_lst = []
            else:
                rela_item_d_arg_lst = rela_only_c_arg.split(',')
        else:
            rela_item_d_arg_lst = rela_only_c_arg.split(',')
        task_args.append(rela_item_d_arg_lst)
    else: #˵���й�����Ϣ
        rela_index_lst_lst = rela_index_lst.split(',')
        for rela_item_ind in rela_index_lst_lst: #���������������
            #��ȡ��Ӧ�ĺ�������
            rela_item_func = 'i_' + global_var.const_dic[rela_item_ind]
            if rela_item_ind == target_index: #���������Ŀ������ı�ţ�������������Զ����������л�ȡ
                rela_item_d_arg = getConf('cus_arg','c_arg_'+target_index,f='./task.cfg')
                if rela_item_d_arg == -1 or len(rela_item_d_arg) == 0: #���Ŀ����Ĳ������Զ����������û�ж��壬���Դ�Ĭ�ϲ����������ж�ȡ
                    rela_item_d_arg = getConf('default_arg','d_arg_'+rela_item_ind,f='./task.cfg')
            else:
                rela_item_d_arg = getConf('default_arg','d_arg_'+rela_item_ind,f='./task.cfg')
            if rela_item_d_arg == -1 or len(rela_item_d_arg) == 0: #�����ȡʧ�ܻ����ǿ�������Ϊ��
                rela_item_d_arg_lst = []
            else:
                rela_item_d_arg_lst = rela_item_d_arg.split(',')
            #�����������ִ��Ͳ����б�����������
            #���������ظ��ԵĹ�����ѯ
            if global_var.onesession:
                try:
                    task_func.index(rela_item_func)
                except ValueError: #���֮ǰû����ͬ��ǰ�ù���
                    task_func.append(rela_item_func)
                    task_args.append(rela_item_d_arg_lst)
                else:
                    try:
                        task_index.index(rela_item_ind)
                    except:
                        pass
                    else:  #Ŀ�������ܷ������ִ��
                        task_func.insert(-1,rela_item_func)
                        task_args.insert(-1,rela_item_d_arg_lst)
            else:
                task_func.append(rela_item_func)
                task_args.append(rela_item_d_arg_lst)

def _GetTask():
    global task_index
    #��ȡĿ������������
    target_index = getConf('task','task_lst',f='./task.cfg')
    target_index_lst = target_index.split(',')
    #���ｫ��ŷ���ȫ�ֱ����
    task_index = target_index_lst
    for targe_index_item in target_index_lst:
        _readTask(targe_index_item)


            
#�����ִ��Ͳ�������ִ��
def _exec(func_str,args):
    func = getattr(coreProc,func_str)
    return func(args)

#�����������̿���
#��ʼִ�г�ʼ����Ϣ
print '��ʼ��ȡ������Ϣ����ʼ������...'
_init()
print '��ʼ��ȡ����...'
_GetTask()
#�����ӡ����ȡ������
print '�������£�'
task_i = 0
for task_n in task_func:
    print '[%d]%s' % (task_i,task_n)
    task_i += 1
  
print '�����б����£�'
task_i = 0  
for arg_n in task_args:
    print task_i,arg_n
    task_i += 1
#��ʼִ������
print '��ʼִ������...'
task_i = 0
for func_item in task_func:
    #��ȡȫ�ֱ��б���Ĳ����б�
    func_arg = task_args[task_i]
    #���и�����
    retn_data = _exec(func_item,func_arg)
    cmdid = global_var.const_dic_r[global_var.COMMAND_STR]
    #print '�����ֶΣ�',cmdid
    #�жϵ�ǰ��Ҫִ�е��������ǲ����ڶ����������֮�У������ǹ�������
    try:
        tmp = task_index.index(cmdid)
    except ValueError: #���������������
        pass
    else: #������ü��
        print '-*-*-*-*-*-*-*-*�����鷵��ֵ-*-*-*-*-*-*-*-*-*-*-*-*'
        mainCheck(retn_data,cmdid)
        print '-*-*-*-*-*-*-*-*�����鷵��ֵ-*-*-*-*-*-*-*-*-*-*-*-*\n'
    #�������仯
    task_i += 1

    
raw_input('��������˳�...')
