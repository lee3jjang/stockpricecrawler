import re
import pandas as pd
import urllib.request as req
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, urlencode

__all__ = ['PnoCrawler', 'NewPhonePriceCrawler', 'UsedPhonePriceCrawler']

class CetizenCrawler:

    def __init__(self):
        self.lastModifiedBy = 'cetizen_crawler'
        self.lastUpdateDate = datetime.now().strftime('%Y-%m-%d')

    def _save(self, data):
        writer = pd.ExcelWriter('{}.xlsx'.format(self.tableName), 'xlsxwriter')
        data.to_excel(writer, index=False)
        writer.save()

    def _add_info(self, data):
        data['lastModifiedBy'] = self.lastModifiedBy
        data['lastUpdateDate'] = self.lastUpdateDate
        return data

class PnoCrawler(CetizenCrawler):
    """세티즌에서 휴대폰 상품번호를 수집합니다.

    Examples
    --------
    >>> pno_crawler = PnoCrawler()
    >>> pno = pno_crawler.crawling()
    >>> models = list(pno.loc[lambda df: df.model.str.contains("SM"), 'pno'].unqiue())
    """

    def __init__(self):
        self.tableName = '상품정보'
        super().__init__()

        url = 'https://price.cetizen.com/'
        res = req.Request(url)
        html = req.urlopen(res).read().decode('cp949')
        self.soup = BeautifulSoup(html, 'html.parser')
        self.wireless = {'wireless_1[]': 'S', 'wireless_2[]': 'K', 'wireless_3[]': 'L',
                         'wireless_1,2[]': 'S,K', 'wireless_1,3[]': 'S,L', 'wireless_2,3[]': 'K,L',
                         'wireless_1,2,3[]': 'S,K,L', 'wireless_7[]': 'SELF', 'wireless_1,2,3,7[]':'S,K,L,SELF',
                         'wireless_0[]': 'wify', 'wireless_9[]': 'KOO'}

    def _get_info_wireless(self, wireless):
        # id=make_0 인 애들 말고 하나씩 더 있어서 2개씩 중복됨
        tag = self.soup.find_all('div', {'name': wireless})
        rst_list = []
        for i in range(len(tag)):
            pno = urlparse(tag[i].a['href']).query.split('&')[1].split('=')[1]
            name = tag[i].get_text().split('\n')[1]
            model = tag[i].get_text().split('\n')[2]
            price = tag[i].get_text().split('\n')[3].split('\xa0')[0]
                        
            rst_list.append([wireless[1], pno, name, model, price])
        df = pd.DataFrame(rst_list, columns=['wireless', 'pno', 'name', 'model', 'price'])
        return df

    def _data_processing(self, df):
        df.price = df.price.str.replace(',', '').str.replace('원', '')
        df = df.astype({'wireless': str, 'pno': str, 'name': str, 'model': str, 'price': float})
        # drop_duplicates : 나중에 없애야 함
        df = df[['wireless', 'pno', 'name', 'model']].drop_duplicates().reset_index(drop=True)
        return df

    def crawling(self, save=False):
        rst_list = []
        for wl in self.wireless.items():
            rst_list.append(self._get_info_wireless(wl))
        df = pd.concat(rst_list)
        df = self._add_info(self._data_processing(df))
        if save:
            self._save(df)
        return df


class NewPhonePriceCrawler(CetizenCrawler):
    """세티즌에서 휴대폰 출고가 데이터를 수집합니다.

    Examples
    --------
    >>> pno_crawler= PnoCrawler()
    >>> pno = pno_crawler.crawling()
    >>> models = list(pno.loc[lambda df: df.model.str.contains("SM"), 'pno'].unique())

    >>> nppc = NewPhonePriceCrawler(models)
    >>> newphone_price = nppc.crawling()
    """

    def __init__(self, pno):
        self.tableName = '출고가정보'
        super().__init__()
        self.pno = pno

    def crawling(self, save=False):
        rst_list = []
        for pl in self.pno:
            params = {'act': 'factory_price', 'q': 'info', 'pno': pl}
            url = 'https://market.cetizen.com/market.php'
            url_params = '{}?{}'.format(url, urlencode(params))
            html = req.urlopen(url_params).read()#.decode('cp949')
            soup = BeautifulSoup(html, 'html.parser')
            txt = str(soup.find_all('script', {'type': "text/javascript"})[18])
            start = txt.find('[')
            end = txt.find(']')
            txt = txt[start:end+1].replace('\r\n\t','')\
                .replace('date', '"date"').replace('value', '"value"').replace(': }', ':None}')
            data = eval(txt)
            for dt in data:
                rst_list.append((pl, dt['date'], dt['value']))
        df = self._add_info(pd.DataFrame(rst_list, columns=['pno', 'date', 'value']))
        if save:
            self._save(df)
        return df


class UsedPhonePriceCrawler(CetizenCrawler):
    """세티즌에서 휴대폰 중고가 데이터를 수집합니다.

    Examples
    --------
    >>> pno_crawler= PnoCrawler()
    >>> pno = pno_crawler.crawling()
    >>> models = list(pno.loc[lambda df: df.model.str.contains("SM"), 'pno'].unqiue())

    >>> uppc = UsedPhonePriceCrawler(models)
    >>> usedphone_price = uppc.crawling()
    """

    def __init__(self, pno):
        self.tableName = '중고가정보'
        super().__init__()
        self.pno = pno

    def crawling(self, save=False):
        rst_list = []
        for pl in self.pno:
            params = {'q': 'info', 'pno': pl, 'period': 1825}
            url = 'https://market.cetizen.com/market.php'
            url_params = '{}?{}'.format(url, urlencode(params))
            html = req.urlopen(url_params).read()#.decode('cp949')
            soup = BeautifulSoup(html, 'html.parser')
            txt = str(soup.find_all('script', {'type': "text/javascript"})[18])
            start = txt.find('[')
            end = txt.find(']')
            txt = txt[start:end+1].replace('\r\n\t', '')\
                .replace('date', '"date"').replace('mid', '"mid"').replace('high', '"high"').replace('low', '"low"')
            data = eval(txt)
            for dt in data:
                rst_list.append((pl, dt['date'], dt['low'], dt['mid'], dt['high']))
        df = self._add_info(pd.DataFrame(rst_list, columns=['pno', 'date', 'low', 'mid', 'high']))
        if save:
            self._save(df)
        return df