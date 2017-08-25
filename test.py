#-*- coding:gbk -*-
#filename: test.py

import sys

'''
    该程序用于测试自动化在运行中可能的各种效果
'''


test_data = {'Body': {'RecordNum': 3, 'SubHisList': \
             [{'TransTime': '20111107152737', 'PayAccount': 1, 'CPOprID': '', 'CpName': 'helloiapppay', \
               'TransID': '03111110715272750005', 'ChrPointName': '33', 'WaresName': 'wfy3', 'Price': 20}, \
              {'TransTime': '20111107152528', 'PayAccount': 1, 'CPOprID': '', 'CpName': 'helloiapppay', \
               'TransID': '03111110715251250004','ChrPointName': '33', 'WaresName': 'wfy1', 'Price': 50},\
              {'TransTime': '20111104165611', 'PayAccount': 1, 'CPOprID': '', 'CpName': '\xb0\xae\xb1\xb4\xd0\xc5\xcf\xa2\xbc\xbc\xca\xf51',\
               'TransID': '03111110416560750008', 'ChrPointName': '2333', 'WaresName': '\xb0\xfc\xb4\xce\xca\xfd', 'Price': 20}], 'TotalNum': 118}, \
             'Version': '2.0', 'NodeType': 0, 'RetCode': 0, 'TokenID': '30871512648731704517918082175463', 'MsgID': 2620, 'CommandID': 33030, 'NodeID': 'auto_byCXZ_v1.1'}

#这里的格式说明如下，在字段前面有字典用#表明，如果后面有列表则用*标明，逗号表明需要匹配的值，如果后面没有标记
check_data = '#Body#**RecordNum,3'
#check_data = '#Body#SubHisList*#TransID,03111110715251250004'
#check_data = '#TokenID,2233'


check_data_ls = check_data.split(',')
item_ls = check_data_ls[0]  #存放的是字串
value_ls = check_data_ls[1:] #存放的是列表

dic_ls = item_ls.split('#')

#标明在前面一个项前面是否有列表，有*标明有
is_before = 0

#由于可能有多个值，这里用列表保存
final_value = []
#找到返回数据中的值
def getItemFromDic(data_dic,item_ls):
    tmp_dic = data_dic
    for dic_item in item_ls:
        if len(dic_item) == 0:
            continue
        tmp_dic = tmp_dic.get(dic_item)
    return tmp_dic

#这里先判断检查串中是否有*，如果小于2个则可以正常处理，否则提示无法处理
sp_cnt = item_ls.count('*')
if sp_cnt > 1:
    print 'can not process'
    sys.exit(1)
elif sp_cnt == 0:
    final_value = getItemFromDic(test_data,item_ls.split('#'))
else: #如果有一个
    dic_ls_1 = item_ls.split('*')[0]
    dic_ls_2 = item_ls.split('*')[1]
    #获取前一个的所有的列表数据
    dic_ls_1_data = getItemFromDic(test_data,dic_ls_1.split('#'))
    for d1 in dic_ls_1_data: #列表中每个字段为一个字典
        final_value.append(getItemFromDic(d1,dic_ls_2.split('#')))
    
#print getItemFromDic(test_data,dic_ls)
print final_value        

    
