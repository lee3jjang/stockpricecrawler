import time
import logging
import pandas as pd
from datetime import datetime

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('log/stockpricecrawler.log')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

class StockPriceCrawler:
    """
        Example
        -------
            >> spc = StockPriceCrawler()
            >> spc.set_code(['005830', '005930', '105560'])
            >> spc.set_daterange('2019-01-31', '2019-12-31')
            >> spc.get_stock_price()
    """

    def __init__(self):
        pass
        
    def set_code(self, company_codes):
        """
            수집할 주가 코드 설정

            :param list company_code: 회사코드 list
        """
        
        self.company_codes = company_codes
        
    def set_daterange(self, start, end, format='%Y-%m-%d'):
        """
            수집할 날짜 범위 설정
            both days inclusive임

            :params str start: 수집시작일
            :params str end: 수집종료일
            :params str format: start, end 입력 format
        """
        self.start_date = datetime.strptime(start, '%Y-%m-%d')
        self.end_date = datetime.strptime(end, '%Y-%m-%d')
        if self.start_date > self.end_date:
            raise Exception('날짜 범위 입력 오류')

    def get_stock_price(self):
        delay = 0.1
        
        start_time = datetime.now()

        result = []
        for code in self.company_codes:
            logger.info(f'데이터 수집을 시작합니다. (code: {code})')
            page = 1
            while(True):
                url = f'https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'
                data = pd.read_html(url)[0].dropna()                
                if page != 1:
                    try:
                        if data.iloc[-1, 0] == result[-1].iloc[-1, 0]:
                            break
                    except:
                        break
                data.insert(0, '회사코드', code)
                result.append(data)
                date_min = datetime.strptime(data['날짜'].iloc[-1], '%Y.%m.%d')
                if date_min <= self.start_date:
                    break
                page += 1
                time.sleep(delay)
        stock_price = pd.concat(result)
        stock_price.columns = ['회사코드', '기준일자', '종가', '전일비', '시가', '고가', '저가', '거래량']
        stock_price['기준일자'] = pd.to_datetime(stock_price['기준일자'], format='%Y.%m.%d')
        stock_price = stock_price.query('기준일자 <= @self.end_date and 기준일자 >= @self.start_date').reset_index(drop=True)
        stock_price = stock_price[['기준일자', '회사코드', '종가', '시가', '고가', '저가', '거래량']]

        end_time = datetime.now()
        logger.info(f'데이터 수집을 종료합니다. (수집시간: {(end_time-start_time).seconds}초, 데이터수: {len(stock_price):,}개)')
        return stock_price