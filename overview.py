import sys
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget
from pyupbit import WebSocketManager

class OverViewWorker(QThread):
    dataSent = pyqtSignal(float, float, float, float, float, float, float, float, float, str)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True
    
    def run(self):
        wm = WebSocketManager("ticker", ["KRW-BTC"])    # 24시간 기준 비트코인 가격정보 요청하는 웹소켓 정의
        while self.alive:
            data = wm.get() # 웹 서버가 보내온 정보를 얻어옴
            #print(data)
            #print(data['trade_price'])
            self.dataSent.emit(float(data['trade_price']),
                               float(data['signed_change_rate']),
                               float(data['acc_trade_volume_24h']),
                               float(data['high_price']),
                               float(data['acc_trade_price_24h']),
                               float(data['low_price']),
                               float(data['signed_change_price']),
                               float(data['prev_closing_price']),
                               float(data['opening_price']),
                               str(data['code']))
        wm.terminate()
    def close(self):
        self.alive = False

class OverviewWidget(QWidget):
    def __init__(self, parent=None, ticker="KRW-BTC"):
        super().__init__(parent)
        uic.loadUi("resource/overview.ui", self)
        self.ticker = ticker
        
        self.ovw = OverViewWorker(ticker)
        self.ovw.dataSent.connect(self.fillData)
        self.ovw.start()
        
    def closeEvent(self, event):
        self.ovw.close()
        
    def fillData(self, trade_price, signed_change_rate, acc_trade_volume_24h, high_price, acc_trade_price_24h, low_price, signed_change_price, prev_closing_price, opening_price, code):
        ## trade_price:종가, signed_change_rate:전일종가대비 변화량, acc_trade_volume_24h : 누적거래량, high_price : 고가, 
        ## acc_trade_price_24h : 누적 거래금액, low_price : 저가, signed_change_price : 전일 종가 대비 변화 금액, prev_closing_price : 전일 종가
        self.label_1.setText(f"{trade_price:,}")
        signed_change_rate*=100
        self.label_2.setText(f"{signed_change_rate:.2f}%")
        self.label_4.setText(f"{acc_trade_volume_24h:.4f} {self.ticker}")
        self.label_6.setText(f"{high_price:,}")
        self.label_8.setText(f"{acc_trade_price_24h/100000000:,.1f} 억 KRW")
        self.label_10.setText(f"{low_price:,}")
        self.label_12.setText(f"{opening_price:,}")
        
        self.label_14.setText(f"{prev_closing_price:,}"+"   "+f"{signed_change_price:,}") if trade_price < prev_closing_price else self.label_14.setText(f"{prev_closing_price:,}"+"   "+f"+{signed_change_price:,}")
        self.label_15.setText(code)
        
        self.__updateStyle()
    
    def __updateStyle(self):
        if '-' in self.label_2.text():
            self.label_1.setStyleSheet("color:blue;")
            self.label_2.setStyleSheet("background-color:blue;color:white")
        else:
            self.label_1.setStyleSheet("color:red;")
            self.label_2.setStyleSheet("background-color:red;color:white")
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ob = OverviewWidget()
    ob.show()
    exit(app.exec_())