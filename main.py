import sys
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyupbit, time, datetime

from pyupbit.quotation_api import get_current_price
from volatility import *

form_class = uic.loadUiType("resource/main.ui")[0]
## chart.py의 ChartWidget 클래스
## graph.py의 QChartView 클래스
## overview.py의 OverviewWidget 클래스
## orderbook.py의 OrderbookWidget 클래스를 Qt Designer에서 메인으로 승격시키도록 했음.

class VolatilityWorker(QThread):
    tradingSent = pyqtSignal(str, float, float) #날짜, 주문타입, 주문량
    sellSent = pyqtSignal(str, float, float)
    
    def __init__(self, ticker, upbit):
        super().__init__()
        self.ticker = ticker
        self.upbit = upbit
        self.alive = True
        
    def run(self):  ## 스레드를 통해 자동매매
        while self.alive:
            try:
                now = datetime.datetime.now()
                start_time = get_start_time(self.ticker) # 오늘 9시
                end_time = start_time + datetime.timedelta(days=1)  # 내일 9시
                
                if start_time < now < end_time - datetime.timedelta(second=10):
                ## 오늘 9시부터 내일 8시 50초까지 매수 조건 확인, 내일 8시50초에서 내일 9시까지의 10초동안은 매도
                    target_price = get_target_price(self.ticker, 0.5)
                    ma15 = get_ma15(self.ticker)
                    current_price = get_current_price(self.ticker)
                    if target_price < current_price and ma15 < current_price:
                        krw = self.upbit.get_balance()
                        if krw > 5000:  # KRW-BTC의 최소 주문 가능 금액이 1000원
                            self.upbit.buy_market_order(self.ticker, 6000*0.9995)  # api키를 이용해 시장가 매수. 수수료 0.0005% 제외한 전체 금액으로 매수
                            buy_time = datetime.datetime.now()  # 매수 시간
                            self.tradingSent.emit(buy_time, target_price, 6000*0.9995) # 구매 시간, 구매 평단, 매수 금액
                
                else: # 내일 8시 50초~ 내일 9시까지의 시간
                    my_coin = self.upbit.get_balance(self.ticker)
                    if my_coin > 0.00008 : # 최소 거래 가능 금액 1000원 이상을 충족
                        self.upbit.sell_market_order(self.ticker, my_coin*0.9995) # 전량 시장가 매도
                        sell_time = datetime.datetime.now()
                        current_price = get_current_price(self.ticker)
                        self.sellSent.emit(sell_time, current_price, my_coin*current_price)
                    time.sleep(1)
            
            
            except:
                time.sleep(1)
            
    
    
    def close(self):
        self.alive = False

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = "KRW-BTC"
        self.button.clicked.connect(self.clickBtn)
        self.setWindowTitle("가즈아 자동머신 ver 0.1")
        self.setWindowIcon(QIcon("resource/doge.png"))
        
        with open("resource/upbitKey.txt") as f:
            lines = f.readlines()
            apikey = lines[0].strip()
            seckey = lines[1].strip()
            self.apiKey.setText(apikey)
            self.secKey.setText(seckey)
        
    def clickBtn(self):     ## 매매시작 버튼 클릭시 매매중단으로 변경. (그 반대도 포함)
        if self.button.text() == "매매시작":
            apiKey = self.apiKey.text()     #Qt Designer에서 apiKey와 secKey라는 이름으로 객체를 설정했음
            secKey = self.secKey.text()
            if len(apiKey) != 40 or len(secKey) != 40:
                self.textEdit.append("KEY가 올바르지 않습니다.")
                return
            else:
                self.b = pyupbit.Upbit(apiKey, secKey)
                balanced = self.b.get_balance()     # get_balance는 현재 현금 잔고를 조회, get_balances는 통화, 현금 잔고등 딕셔너리값 조회. get_balance(ticker값)는 해당 코인을 보유한 금액조회
                if balanced == None:
                    self.textEdit.append("KEY가 올바르지 않습니다.")
                    return
            
            self.button.setText("매매중단")
            self.textEdit.append("\"진행시켜.\"")
            self.textEdit.append(f"보유 현금 : {balanced} 원")
            target_point = get_target_price(self.ticker, 0.5)
            ma15 = get_ma15(self.ticker)
            self.textEdit.append(f"변동성 돌파 매수 포인트 : {target_point:,} 원  15일 이평선 : {ma15:,}  현재가가 이 금액들 보다 높아야 매수함.")
            
            
            self.vw = VolatilityWorker(self.ticker, self.b)
            self.vw.tradingSent.connect(self.receiveTradingSignal)  # 매수날짜, 구매평단, 매수금액
            self.vw.start() # 매매시작 버튼을 누른 상태에만 자동거래가 진행
            
            self.vw2 = VolatilityWorker(self.ticker, self.b)
            self.vw2.sellSent.connect(self.sellTradingSignal)
            self.vw2.start()
            self.vw2.close()
            
        else:
            self.vw.close() # 매매중단을 누르면 자동 매매 종료
            self.textEdit.append("이제 니 인생 살어~")
            self.button.setText("매매시작")
                
    def receiveTradingSignal(self, time, average_cost, cost_price):
        self.textEdit.append(f"[{time}] {self.ticker} 평단: {average_cost:,} 매수 금액:{cost_price:,}") # #날짜, 주문타입, 주문량 받아옴
        apiKey = self.apiKey.text()     #Qt Designer에서 apiKey와 secKey라는 이름으로 객체를 설정했음
        secKey = self.secKey.text()
        self.b = pyupbit.Upbit(apiKey, secKey)
        balanced = self.b.get_balance()
        self.textEdit.append(f"보유 현금 : {balanced} 원")
        
    def sellTradingSignal(self, time, currprice, sell_cost):
        self.textEdit.append(f"[{time}] {self.ticker} 매도가: {currprice:,} 총매도 금액:{sell_cost:,}")
        apiKey = self.apiKey.text()     #Qt Designer에서 apiKey와 secKey라는 이름으로 객체를 설정했음
        secKey = self.secKey.text()
        self.b = pyupbit.Upbit(apiKey, secKey)
        balanced = self.b.get_balance()
        self.textEdit.append(f"보유 현금 : {balanced} 원") 
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())