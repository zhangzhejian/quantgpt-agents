import pandas as pd
import numpy as np
from qstock_searcher import get_stock_df
import schemas
import datetime
MEAN_PRICE_LONG_PERIOD=30
MEAN_PRICE_SHORT_PERIOD=10

class StockAnalyzer(object):

    def __init__(self,):
        return
    

    def get_stock_fund_info(self):
        pass
    
    def get_mean_prices(self, df):
        periods = [MEAN_PRICE_SHORT_PERIOD, MEAN_PRICE_LONG_PERIOD]
        for period in periods:
            col_name = f'{period}日均价'
            price_roll_window = df['close'].rolling(window=period)
            df[col_name] = price_roll_window.mean()
            df = df.fillna(0)

        df[f'{periods[0]}日均线上穿{periods[1]}日均线'] = (df[f'{periods[0]}日均价'].shift(1) < df[f'{periods[1]}日均价'].shift(1)) & (df[f'{periods[0]}日均价'] > df[f'{periods[1]}日均价'])
        df[f'{periods[0]}日均线下穿{periods[1]}日均线'] = (df[f'{periods[0]}日均价'].shift(1) > df[f'{periods[1]}日均价'].shift(1)) & (df[f'{periods[0]}日均价'] < df[f'{periods[1]}日均价'])
        return df

    def bollinger_bands(self, data, window, num_std):
        """
        计算布林带
        :param data: 股票价格数据
        :param window: 计算布林带所需的时间窗口
        :param num_std: 用于计算上下轨的标准差倍数
        :return: 中轨，上轨，下轨
        """
        rolling_mean = data.rolling(window=window).mean()
        rolling_std = data.rolling(window=window).std()
        
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        
        return rolling_mean, upper_band, lower_band
    
    def get_bollinger_bands(self, df):
        df['Middle_Band'], df['Upper_Band'], df['Lower_Band'] = self.bollinger_bands(data=df['close'], window=20, num_std=2)
        df['Reach_Bollinger_Low'] = df['close'] <= df['Lower_Band']
        df['Reach_Bollinger_Up'] = df['close'] >= df['Upper_Band']
        df['Middle_Band_Trend'] = df['Middle_Band'] - df['Middle_Band'].shift(1)
        return df

    def macd(self, data, short_window, long_window, signal_window):
        """
        计算平滑异同移动平均线（MACD）
        :param data: 股票价格数据
        :param short_window: 短期EMA窗口
        :param long_window: 长期EMA窗口
        :param signal_window: MACD信号线窗口
        :return: MACD, Signal
        """
        ema_short = data.ewm(span=short_window).mean()
        ema_long = data.ewm(span=long_window).mean()
        macd = ema_short - ema_long
        signal = macd.ewm(span=signal_window).mean()
        
        return macd, signal
    
    def cal_macd(self, df):
        # 计算MACD
        short_window = 12
        long_window = 26
        signal_window = 9
        df['MACD'], df['Signal'] = self.macd(df['close'], short_window, long_window, signal_window)
        df['Histogram'] = df['MACD'] - df['Signal']
        # 计算交叉点
        df['Cross'] = np.where(df['MACD'] > df['Signal'], 1, -1)
        # 查找买入点和卖出点
        df['up_cross'] = df['Cross'].diff() == 2
        df['down_cross']= df['Cross'].diff() == -2
        return df


    def generate_tech_infos(self, code:str,date:datetime ) -> schemas.StockTechInfo:
        df= get_stock_df(code) 
        df = self.get_bollinger_bands(df)
        df = self.cal_macd(df)
        df = self.get_mean_prices(df)
        last_row = df.tail(1)
        price_info = schemas.StockPriceInfo(
            sample_frequency = schemas.SampleFrequency.daily.value,
            price = df.tail(15)['close'].values.tolist(),
            volume=df.tail(15)['volume'].values.tolist()
        )
        if last_row['Reach_Bollinger_Up'].iloc[0]:
            boll_status = schemas.BollStatus.reach_up.value
        elif last_row['Reach_Bollinger_Low'].iloc[0]:
            boll_status = schemas.BollStatus.reach_down.value
        else:
            boll_status =  schemas.BollStatus.normal.value

        boll_info = schemas.BollingerInfo(
            boll_status =  boll_status,
            boll_trend = schemas.BollTrend.up.value if last_row['Middle_Band_Trend'].iloc[0] >= 0 else schemas.BollTrend.down.value,
        )
        if last_row['up_cross'].iloc[0]:
            macd_cross_status = schemas.MACDCrossStatus.gold
        elif last_row['down_cross'].iloc[0]:
            macd_cross_status = schemas.MACDCrossStatus.dead
        else:
            macd_cross_status = schemas.MACDCrossStatus.normal
        macd_info=schemas.MACD(
            crossover= macd_cross_status,
            histogram=round(last_row['Histogram'].iloc[0],2)
        )
        if last_row[f'{MEAN_PRICE_SHORT_PERIOD}日均线上穿{MEAN_PRICE_LONG_PERIOD}日均线'].iloc[0]:
            mean_price_cross = schemas.MeanPriceStatus.up_cross
        elif last_row[f'{MEAN_PRICE_SHORT_PERIOD}日均线下穿{MEAN_PRICE_LONG_PERIOD}日均线'].iloc[0]:
            mean_price_cross = schemas.MeanPriceStatus.down_cross
        else:
            mean_price_cross = schemas.MeanPriceStatus.normal

        mean_price_info = schemas.MeanPriceInfo(
            sample_frequency = schemas.SampleFrequency.daily.value,
            long_period=MEAN_PRICE_LONG_PERIOD,
            short_period=MEAN_PRICE_SHORT_PERIOD,
            cross=mean_price_cross
        )

        # print(price_info.to_prompt())
        # print(boll_info.to_prompt())
        # print(macd_info.to_prompt())
        # print(mean_price_info.to_prompt())
        stock_tech_info=schemas.StockTechInfo(
            price_infos=[price_info],
            mean_price_infos=[mean_price_info],
            boll_info=boll_info,
            macd_info=macd_info
        )
        # print(stock_tech_info.to_prompt())
        return stock_tech_info
        
stock_analyzer = StockAnalyzer()
if __name__ == '__main__':
    analyzer = StockAnalyzer()
    # df= get_stock_df('000155') 
    # print(df.columns)
    # # df = analyzer.get_mean_prices(df)
    # df = analyzer.get_bollinger_bands(df)
    # df = analyzer.cal_macd(df)
    # print(df)

    analyzer.generate_tech_infos('603778')
