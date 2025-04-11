from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import openpyxl
import time
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException,ElementNotVisibleException
from selenium.webdriver.chrome.options import Options
import pickle

driver=webdriver.Edge()

class spider:
    login_url="https://kyfw.12306.cn/otn/resources/login.html"
    profile_url="https://kyfw.12306.cn/otn/view/index.html"
    left_ticket="https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
    passenger_url="https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def __init__(self,from_station,to_station,date,trains,passengers):
        self.from_station=from_station
        self.to_station=to_station
        self.date=date
        self.trains=trains
        self.passengers=passengers
        self.select_no=None
        self.select_seat=None

    def login(self):
        # driver.get(self.login_url)
        # driver.maximize_window()
        # node_login=driver.find_element(By.XPATH,'//div[@class="login-box"]//a[text()="扫码登录"]')
        # driver.execute_script("arguments[0].click();",node_login)
        # WebDriverWait(driver,1000).until(
        #     ec.url_to_be(self.profile_url)
        # )
        # print("登录成功")
        driver.get(self.login_url)
        with open("cookies.pkl","rb") as f:
            cookies=pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        
        driver.refresh()
        driver.get(self.login_url)
        driver.maximize_window()

    def search_tickiet(self):
        driver.get(self.left_ticket)
        from_station=driver.find_element(By.ID,"fromStation")
        to_station=driver.find_element(By.ID,"toStation")
        train_date=driver.find_element(By.ID,"train_date")

        from_station_code=self.init_station_code()[self.from_station]
        to_station_code=self.init_station_code()[self.to_station]
        
        driver.execute_script('arguments[0].value="%s"' % from_station_code,from_station)
        driver.execute_script('arguments[0].value="%s"' % to_station_code,to_station)
        driver.execute_script('arguments[0].value="%s"' % self.date,train_date)
        
        while True:
            WebDriverWait(driver,10).until(
                ec.element_to_be_clickable((By.ID,"query_ticket"))
            )
            btn=driver.find_element(By.ID,"query_ticket")
            driver.execute_script('arguments[0].click();',btn)

            WebDriverWait(driver,10).until(
                ec.presence_of_element_located((By.XPATH,'//tbody[@id="queryLeftTable"]/tr'))
        )
            trains=driver.find_elements(By.XPATH,'//tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        
            for train in trains:
                infos=train.text.replace('\n',' ').split(' ')
                train_no=infos[0]
                if train_no in self.trains:
                    seat_types=self.trains[train_no]
                    is_flag=False
                    for seat_type in seat_types:
                        if seat_type=='O':
                            count=infos[9]
                            if count.isdigit() or count=='有':
                                is_flag=True
                                break

                        elif seat_type=='M':
                            count=infos[10]
                            if count.isdigit() or count=='有':
                                is_flag=True
                                break

                    if is_flag:
                        self.select_no=train_no
                        node_buy=train.find_element(By.XPATH,'.//a[@class="btn72"]')
                        driver.execute_script("arguments[0].click();",node_buy)
                        # if ec.presence_of_element_located((By.XPATH,'//div[@class="modal-login"]')):
                        #     driver.refresh()
                        #     break
                        return
 
    def confirm_passenger(self):
        WebDriverWait(driver,1000).until(
            ec.url_to_be(self.passenger_url)
        )
        WebDriverWait(driver,1000).until(
            ec.presence_of_element_located((By.XPATH,'//ul[@id="normal_passenger_id"]/li/label'))
        )
        passengers=driver.find_elements(By.XPATH,'//ul[@id="normal_passenger_id"]/li/label')
        for passenger in passengers:
            name=passenger.text
            if name in self.passengers:
                driver.execute_script("arguments[0].click();",passenger)
        # 选座操作有些多余 正常都是默认二等座 谁坐一等座
        # seat_select=Select(driver.find_element(By.ID,'seatType_1'))
        # seat_types=self.trains[self.select_no]
        # for seat_type in seat_types:
        #     try:
        #         seat_select.select_by_value(seat_type)
        #         if seat_type=='O':
        #             self.select_seat="二等座"
        #         elif seat_type=='M':
        #             self.select_seat="一等座"
        #     except:
        #         continue
        #     else:
        #         break
        WebDriverWait(driver,1000).until(
            ec.element_to_be_clickable((By.ID,'submitOrder_id'))
        )

        node_submission=driver.find_element(By.ID,'submitOrder_id')
        driver.execute_script("arguments[0].click();",node_submission)
        WebDriverWait(driver,1000).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME,'dhtmlx_window_active'))
        )
        WebDriverWait(driver,1000).until(
            ec.element_to_be_clickable((By.ID,'qr_submit_id'))
        )
        # node_submit=driver.find_element(By.ID,'qr_submit_id')
        # while node_submit:
        #     try:
        #         driver.execute_script("arguments[0].click();",node_submit)
        #         node_submit=driver.find_element(By.ID,'qr_submit_id')
        #     except ElementNotVisibleException:
        #         break
        print(f'{self.select_no}车次抢票成功！')
        input("按Enter退出......")



    def run(self):
        self.login()
        self.search_tickiet()
        self.confirm_passenger()


    def init_station_code(self):
        wb=openpyxl.load_workbook('车站代码.xlsx')
        ws=wb.active
        lst=[]
        for row in ws.rows:
            sub_lst=[]
            for cell in row:
                sub_lst.append(cell.value)
            lst.append(sub_lst)

        return dict(lst)

def start():
    # from_station=input("请输入起始车站:")
    # to_station=input("请输入终点车站:")
    # date=input("请输入出发日期（例如：2025-02-08）:")
    # passenger=input("请输入乘车人：")
    # train=input("请输入要乘坐的车次：")
    # login=spider(from_station,to_station,date,{train:['O','M']},[passenger])
    login=spider('潮汕','深圳坪山','2025-04-16',{'D7341':['O','M'],'G3007':['O','M'],'D7341':['O','M']},['郑锐荣'])
    login.run()

if __name__ == '__main__':
    start()