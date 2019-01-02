#! /usr/bin/python3
# _*_ coding: UTF -8 _*_

"""TicketsQuery

Usage:
	test.py query (<from_sta>) (<to_sta>) (<date>)
	test.py (-h | --help)
	test.py --version

Options:
	-h --help	
	--version

"""

import re
import requests

from prettytable import PrettyTable
from docopt import docopt


STATION_DICT_URL = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9088'

def getStation(sta):
    str = requests.get(STATION_DICT_URL).text

    #匹配中文的正则表达式
    area = re.findall("([\u4E00-\u9FA5]+)\|([A-Z]+)",str)
    area = dict(area)

    if sta in area:
        return area[sta]


def getUrl(from_sta, to_sta, date):
    #url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2019-01-10&leftTicketDTO.from_station=SZH&leftTicketDTO.to_station=WFK&purpose_codes=ADULT'

    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=' + date + '&leftTicketDTO.from_station=' + from_sta + '&leftTicketDTO.to_station=' + to_sta + '&purpose_codes=ADULT'
    return url
	
""" 
json result
['M%2BDQkRO5sxjNE1aEy73EtQBrnlwKGAWqRuP6%2BWIOrnYUQB2sUQNHG7pAYMA5VKEgpnGrqaVFoymv%0Atm9RWS2pbm7gOijdnqak%2B4SAxrTTfKUjPkEdmFyRbMGZ4dWGIIF3dc8ngBq2YoEfKX9QKj687KRq%    0A3E3h3DsagYvxXMjOJiFEx%2BkycVOMJE84eH7iFd9nuWsdgpdTWhHqNfz6ZsgnjPDV9bEc2jDYSINb%0A3FpXTFQsblYl', '预订', '550000D31490', 'D314', 'SHH', 'VNP', 'SHH', 'VNP', '21:07    ', '08:55', '11:48', 'Y', '8cf2zk4qp%2BawyfkrIw1bZnLmic%2BndnvI', '20181108', '3', 'H3', '01', '04', '0', '0', '', '', '', '有', '', '', '', '', '', '', '有', '', '    ', '', 'O040', 'O4', '1']
"""

if __name__ == '__main__':
    arguments = docopt(__doc__, version='TicketsQuery v1.0')

    from_sta = arguments.get("<from_sta>")
    to_sta = arguments.get("<to_sta>")
    date = arguments.get("<date>")

    #将汉字转换为特定编码
    from_sta_code = getStation(from_sta)
    to_sta_code = getStation(to_sta)

    #拼接url 用来get        
    url = getUrl(from_sta_code, to_sta_code, date)
    print(url)
    #请求url        
    html = requests.get(url)
    #html.encoding = 'utf-8'
    #print(html.text)
   
    #网页返回200 Ok进行解析
    if html.status_code == 200:
    #获取json
        try:
            res = html.json()["data"]["result"]
            # print(res)
            sta_dict = html.json()["data"]["map"] #获得到一个字典  用于站点的汉字和字符标记转换
            #做表
            table=PrettyTable(["车次","出发站","到达站","出发时间","到达时间","历时","特等座","一等座","二等座","软卧","硬卧","软座","硬座","无座"])

            for data in res:
                list = data.split("|") #分割，获取所有信息填入的list
                #print(list)
                if list[1]=='列车停运': #根据json 挨个分析
                    continue
                line_no = list[3]
                from_sta = list[6]
                to_sta = list[7]
                start_time = list[8]
                stop_time = list[9]
                cost_time = list[10]
				
				#字符串 赋值 ： or  两个都有值，取第一个，第一个没有值，取第二个
                TDZ=list[32] or "--"    #特等座
                YDZ=list[31] or "--"    #一等座
                EDZ=list[30] or "--"    #二等座
                RW=list[23] or "--"     #软卧
                YW=list[28] or "--"     #硬卧
                RZ=list[27] or "--"     #软座
                YZ=list[29] or "--"     #硬座
                WZ=list[26] or "--"  #无座  

                #表格添加列
                table.add_row([line_no, sta_dict[from_sta], sta_dict[to_sta], start_time, stop_time, cost_time, TDZ, YDZ, EDZ, RW, YW, RZ, YZ, WZ])
            print (table)
        except Exception as e:
            print('Error:',e)

