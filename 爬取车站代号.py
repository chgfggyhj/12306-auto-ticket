import requests
import re
import openpyxl
def get_station():
    url="https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9343"
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'}
    resp=requests.get(url,headers=headers)
    print(resp.text)
    stations=re.findall(r'([\u4e00-\u9fa5]+)\|([A-Z]+)',resp.text)
    return stations

def save(lst):
    wb=openpyxl.Workbook()
    ws=wb.active
    for item in lst:
        ws.append(item)
    wb.save('车站代码.xlsx')

if __name__=="__main__":
    lst=get_station()
    save(lst)
    
