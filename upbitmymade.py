import sys
from PyQt5 import uic
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis   # QLineSeries는 데이터 그리기, QChart는 그려질 공간, QValueAxis는 틱 마크, 그리드라인, 쉐이드를 보여주게 함, QDateTimeAxis는 날짜 축 관리
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal
import time
import pyupbit

class PriceWorker(QThread): ## QThread 상속받는 PriceWorker클래스
    dataSent = pyqtSignal(float)    # 메인 쓰레드에 데이터 전달을 위한 dataSent시그널 정의
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True   # QThread의 종료를 위해 만든 변수
        
    def run(self):
        while self.alive:   # 나중에 alive가 false가 되면 반복문 탈출로 쓰레드가 종료될 것임.
            data = pyupbit.get_current_price(self.ticker) #현재가를 계속 data에 바인딩
            time.sleep(1)
            self.dataSent.emit(data)    # 시그널을 메인쓰레드에 알린다. data > pyqtSignal(float)의 인자로 보내진다
            
    def close(self):
        self.alive = False  # close 메서드 호출시 PriceWorker 쓰레드 종료시킴.

class ChartWidget(QWidget): ## 차트위젯 클래스
    def __init__(self, parent=None, ticker="KRW-BTC"): # parent는 위젯이 그려질 위치, None이면 그냥 새로운 창에 그림.
        super().__init__(parent)
        uic.loadUi("resource/chart.ui", self)   # UI 만들어 놓은 거 불러오기
        self.ticker = ticker
        
        self.viewLimit = 128 # 그릴 데이터 수의 최대치를 미리 설정.
        self.priceData = QLineSeries()  # 데이터 그리는 QLineSeries객체를 priceData가 바인딩
        self.priceChart = QChart() # 그려질 공간을 만드는 QChart객체를 priceChart가 바인딩
        self.priceChart.addSeries(self.priceData)   # 데이터를 차트객체로 전달하여 시각화
        self.priceChart.legend().hide() #차트 범례를 숨기는 기능
        
        axisX = QDateTimeAxis() # 날짜 x축 관리 QDateTimeAxis 객체를 axisX가 바인딩
        axisX.setFormat("hh:mm:ss") # 날짜를 시:분:초 형태로 양식을 구성
        axisX.setTickCount(4)   # 차트에 표시할 날짜 개수를 4로 지정
        dt = QDateTime.currentDateTime() # 현재 시간 정보를 QDateTime 객체로 얻어와 dt가 바인딩
        axisX.setRange(dt, dt.addSecs(self.viewLimit))  # X축에 출력될 값 범위를 현재 시간~ viewLimit=128초까지 설정. addSecs()메서드는 지정된 초 이후 시간을 QDateTime으로 반환
        axisY = QValueAxis()    # 정수 값 담고 y축 담당할 QValueAxis 객체를 axisY가 바인딩
        axisY.setVisible(True) # False y 축의 레이블을 차트에 표시하지 않음
        
        self.priceChart.addAxis(axisX, Qt.AlignBottom)  # x축을 아래쪽에 그릴 각을 잡는다
        self.priceChart.addAxis(axisY, Qt.AlignRight)   # y축을 오른쪽에 그릴 각을 잡는다
        self.priceData.attachAxis(axisX)    # x축에 차트와 데이터를 연결한다
        self.priceData.attachAxis(axisY)    # y축에 차트와 데이터를 연결한다
        self.priceChart.layout().setContentsMargins(0, 0, 0, 0) # 왼쪽 위쪽 오른쪽 아래쪽 여백을 0으로 설정
        
        self.priceView.setChart(self.priceChart)    # 지금까지 어떻게 그릴건지에 대한 정보를 토대로 화면에 그려낸다
        self.priceView.setRenderHints(QPainter.Antialiasing) # 차트에 anti-aliasing 적용
        
        self.pw = PriceWorker(ticker)   # 쓰레드를 다루는 메서드인 PriceWorker의 객체를 생성
        self.pw.dataSent.connect(self.appendData)   # PriceWorker 클래스의 dataSent쓰레드를 appendData메서드와 연결시킨다. pyqtSignal(float)에서 float의 인자로 보내진 Data를 appendData메서드의 인자값으로 보낸다
        self.pw.start() # PriceWorker클래스의 run메서드를 실행시키고, appendData 메서드도 활성화 시킨다.
        
    def closeEvent(self, event):    ## PriceWorker 쓰레드를 종료시키는 메서드. closeEvent는 부모 QWidget에 정의된 메서드로, UI의 종료 버튼 누르면 실행이 됨. 자식 클래스에서 closeEvent를 재정의하여 종료되기 전 쓰레드를 종료시키는 것임. 이처럼 부모 클래스의 메서드를 자식 클래스에서 재정의하는 것을 매서드 오버라이딩이라 함.
        self.pw.close()
        
    def appendData(self, currPirce):    ## 차트에 그릴 데이터를 입력 받는 메서드. currPirce는 현재가. (쓰레드를 통해 data값을 매개변수로 받았다)
        ## viewLimit만큼의 데이터가 저장되어 있으면 오래된 데이터를 하나 제거하고 새로운 데이터를 추가시킨다.
        if len(self.priceData) == self.viewLimit:
            self.priceData.remove(0)    # 제일 오래된 데이터를 제거
        dt = QDateTime.currentDateTime()    # 현재 시간 정보를 얻어와서 dt에 바인딩
        self.priceData.append(dt.toMSecsSinceEpoch(), currPirce)    # 데이터에 새로운 dt(현재 시간)의 milisecond값과(x축) 현재가 currPirce값(y축)을 담는다.
        self.__updateAxis()

    def __updateAxis(self): ## 데이터의 x,y축정보를 조절해 어느 구간을 출력할지 결정. 데이터값(x시간, y현재가)을 받아왔으니 이제 차트에 반영을 해서 그린다.
        ## 차트그래프가 viewLimit값보다 많이 그림을 그리는 것을 방지
        pvs = self.priceData.pointsVector() # 저장된 데이터들을 리스트로 얻어와서 pvs가 바인딩. 시간별 현재가에 대한 데이터들이 리스트로 정리되어 있을 것임. pvs의 x:시간, y:현재가
        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))    # 리스트화된 데이터(시간별 현재가에 대한 데이터)의 가장 오래된 객체를 선택해서 x좌표에 저장된 값을 가져온다. 그리고 milisecond값으로 변환해 dtStart에 바인딩
        if len(self.priceData) == self.viewLimit:   # 데이터 최대치에 도달하면?
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x())) # 가장 최근 시간 정보가 들어있는 마지막 객체를 선택해 dtLast에 바인딩
        else:   # viewLimit에 도달하기 전에는 x축 가장 처음값 + viewLimit값을 dtLast에 바인딩
            dtLast = dtStart.addSecs(self.viewLimit) # 항상 viewLimit개의 데이터를 출력하는데 사용
        
        ## 차트상에 그려낼 x값과 y값의 범위를 갱신한다
        ax = self.priceChart.axisX()    # ax가 차트의 x축값을 바인딩?
        ax.setRange(dtStart, dtLast)    # 표시될 x축 범위 설정
        ay = self.priceChart.axisY()    # ax가 차트의 y축값을 바인딩?
        dataY = [v.y() for v in pvs]    # dataY가 데이터 리스트의 각 값의 y축으로 쓰이도록 바인딩?
        ay.setRange(min(dataY), max(dataY)) # 표시될 y축 최소, 최대의 범위 설정
        

            
if __name__ == "__main__":  # 이벤트 루프 생성
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    cw = ChartWidget()  #차트위젯 객체 생성
    cw.show()
    exit(app.exec_())