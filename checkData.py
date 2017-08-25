#-*- coding:gbk -*-
#filename: checkData.py
#�ó������ֱ����2.7�汾����
#--------------------------------------
#   author : ��Э��
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

import sys
import global_var
from mPublic import *

'''
    �ó������ڼ�鷵�ص������������ļ���ָ���������Ƿ�һ��
'''

#�ҵ��ֵ��е���
#����˵����
#   data_dic:��Ҫ���ҵ������ֵ�
#   item_ls:��ȡ�ֵ��еĹؼ�����б�
def getItemFromDic(data_dic,item_ls):
    tmp_dic = data_dic
    for dic_item in item_ls:
        if len(dic_item) == 0:
            continue
        tmp_dic = tmp_dic.get(dic_item)

    return tmp_dic


#�����������л�ȡ����Ҫ����ֶεķ���ֵ,���а����˸��ֱ�ʶ����
#����˵����
#
def getData(test_data,item_ls):
    final_value = []
    #������ֶ��е�*����
    sp_cnt = item_ls.count('*')
    if sp_cnt > 1: #�������1��*����ʾ�б��л����б�Ŀǰ�޷�����
        print 'can not process'
        sys.exit(1)
    elif sp_cnt == 0:
        final_value = getItemFromDic(test_data,item_ls.split('#'))
    else: #�����һ��*
        dic_ls_1 = item_ls.split('*')[0]
        dic_ls_2 = item_ls.split('*')[1]
        #��ȡǰһ�������е��б�����
        dic_ls_1_data = getItemFromDic(test_data,dic_ls_1.split('#'))
        for d1 in dic_ls_1_data: #�б���ÿ���ֶζ���һ���ֵ�
            final_value.append(getItemFromDic(d1,dic_ls_2.split('#')))

    return final_value

#print getData(test_data,item_ls)
#�ȽϷ���ֵ��Ԥ��ֵ
#����˵����
#   real:ʵ�ʷ��ص����ݣ�������һ���������ִ��������б�
#   expect�������Ľ�����������б�
def compareResult(real,expect):
    #������
    result = 0
    #��ʵ�ʷ���ֵ����ת����תΪһ�������ִ����б�
    if type(real).__name__ == 'int':
        real = str(real)
    if type(real).__name__ == 'str':
        real = [real]
    #�������ӶԷ����������б�Ĵ���
    #������б����ͣ������е��������Ͷ�ת�����ִ���
    j = 0
    if type(real).__name__ == 'list':
        for i_r in real:
            real[j]=str(i_r)
            j+=1
            
    print real,' -> ',expect,
    #��Ԥ��������ȡ��ÿ��ֵ�������ڷ����������Ƿ����
    for expect_item in expect:
        try:
            i = real.index(expect_item)
        except ValueError:
            result = 0
        else:
            result = 1
    if result:
        print ':success'
    else:
        print ':fail'

#�ò����Ǽ��������غ��������ڼ�鷵�����ݵ��ֶ�
#���������
#   retnData:�ӷ���˷��ص������ֵ�
#   commandIndex����������
def mainCheck(retnData,commandIndex):
    #��ȡ������
    checkItemAll = getConf('check_result','c_r_'+commandIndex,f='./task.cfg')
    if checkItemAll == -1:
        print 'δ���ü����'
        return -1
    #�Լ������зֽ�
    checkItemAll_ls = checkItemAll.split('|')
    #���ÿ����������
    for checkItemAll_ls_item in checkItemAll_ls:
        if len(checkItemAll_ls_item) == 0:
            continue
        i1 = checkItemAll_ls_item.split(',')
        i1_item = i1[0]
        i1_value = i1[1:]
        retn_value = getData(retnData,i1_item)
        compareResult(retn_value,i1_value)
    
