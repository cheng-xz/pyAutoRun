#-*- coding:gbk -*-
#filename: checkData.py
#该程序可以直接在2.7版本运行
#--------------------------------------
#   author : 成协主
#   email:chengxiezhu@iapppay.com;chengxiezhu@126.com
#--------------------------------------

import sys
import global_var
from mPublic import *

'''
    该程序用于检查返回的数据与任务文件中指定的数据是否一致
'''

#找到字典中的项
#参数说明：
#   data_dic:需要查找的数据字典
#   item_ls:获取字典中的关键项的列表
def getItemFromDic(data_dic,item_ls):
    tmp_dic = data_dic
    for dic_item in item_ls:
        if len(dic_item) == 0:
            continue
        tmp_dic = tmp_dic.get(dic_item)

    return tmp_dic


#从完整数据中获取所需要检查字段的返回值,其中包括了各种标识符号
#参数说明：
#
def getData(test_data,item_ls):
    final_value = []
    #检查检查字段中的*个数
    sp_cnt = item_ls.count('*')
    if sp_cnt > 1: #如果大于1个*，表示列表中还有列表，目前无法处理
        print 'can not process'
        sys.exit(1)
    elif sp_cnt == 0:
        final_value = getItemFromDic(test_data,item_ls.split('#'))
    else: #如果有一个*
        dic_ls_1 = item_ls.split('*')[0]
        dic_ls_2 = item_ls.split('*')[1]
        #获取前一个的所有的列表数据
        dic_ls_1_data = getItemFromDic(test_data,dic_ls_1.split('#'))
        for d1 in dic_ls_1_data: #列表中每个字段都是一个字典
            final_value.append(getItemFromDic(d1,dic_ls_2.split('#')))

    return final_value

#print getData(test_data,item_ls)
#比较返回值和预期值
#参数说明：
#   real:实际返回的数据，可能是一个整数、字串或者是列表
#   expect：期望的结果，类型是列表
def compareResult(real,expect):
    #定义结果
    result = 0
    #对实际返回值进行转换，转为一个包含字串的列表
    if type(real).__name__ == 'int':
        real = str(real)
    if type(real).__name__ == 'str':
        real = [real]
    #这里增加对返回数据是列表的处理
    #如果是列表类型，将其中的所有整型都转换成字串性
    j = 0
    if type(real).__name__ == 'list':
        for i_r in real:
            real[j]=str(i_r)
            j+=1
            
    print real,' -> ',expect,
    #从预期数据中取出每个值，看其在返回数据中是否存在
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

#该参数是检查项的主控函数，用于检查返回数据的字段
#输入参数：
#   retnData:从服务端返回的数据字典
#   commandIndex：任务项编号
def mainCheck(retnData,commandIndex):
    #获取配置项
    checkItemAll = getConf('check_result','c_r_'+commandIndex,f='./task.cfg')
    if checkItemAll == -1:
        print '未设置检查项'
        return -1
    #对检查项进行分解
    checkItemAll_ls = checkItemAll.split('|')
    #检查每个待检查的项
    for checkItemAll_ls_item in checkItemAll_ls:
        if len(checkItemAll_ls_item) == 0:
            continue
        i1 = checkItemAll_ls_item.split(',')
        i1_item = i1[0]
        i1_value = i1[1:]
        retn_value = getData(retnData,i1_item)
        compareResult(retn_value,i1_value)
    
