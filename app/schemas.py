from pydantic import BaseModel,Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

risk_tolerance_map:dict = {
    0: "Avoids all risk (Equivalent to keeping money under a mattress)",
    1: "Ultra Conservative (Primarily in ultra-safe instruments like treasury bills)",
    2: "Very Conservative (High allocation to bonds and other fixed-income securities)",
    3: "Conservative (Mainly bonds, with a small allocation to equities or other slightly riskier assets)",
    4: "Mildly Conservative (Balanced between bonds and equities)",
    5: "Moderate (Even split between equities and bonds or other fixed-income securities)",
    6: "Mildly Aggressive (Higher allocation to equities with some bonds and possibly alternative assets)",
    7: "Aggressive (Mainly equities, with a minimal bond or fixed-income allocation)",
    8: "Very Aggressive (High concentration in equities, potentially including riskier sectors or emerging markets)",
    9: "Extremely Aggressive (Potential for high-risk ventures, speculative assets, or leveraged investments)",
    10: "Speculative (Full exposure to highly speculative investments or betting on single outcomes)"
}

greed_map:dict= {
    0: "Not greedy at all",
    1: "Very slightly greedy",
    2: "Slightly greedy",
    3: "Mildly greedy",
    4: "Moderately greedy",
    5: "Average greediness",
    6: "Above average greedy",
    7: "Quite greedy",
    8: "Very greedy",
    9: "Extremely greedy",
    10: "Ultimate greed",
}

aggressiveness_map:dict = {
    0: "Ultra Conservative",
    1: "Very Conservative",
    2: "Conservative",
    3: "Mildly Conservative",
    4: "Moderate",
    5: "Balanced",
    6: "Mildly Aggressive",
    7: "Aggressive",
    8: "Very Aggressive",
    9: "Extremely Aggressive",
    10: "All-in Aggressive",
}


class AgentRole(Enum):
    BEGINNER = "Beginner Trader"
    SENIOR = "Senior Trader"
    EXPERT = "Expert Trader"
    FUNDMANAGER = 'FUND MANAGER'

class InvestmentStyle(Enum):
    ACTIVITE_INVESTING = "Active Investing"
    VALUE_INVESTING = "Value Investing"
    TECHNICAL_TRADING= "Technical Trading"


class SampleFrequency(Enum):
    daily = "1 day"
    weekly = '5 days'
    min_15 = '15 minute'
    min_5 = '5 minute'
    hour = '60 minute'

class BollStatus(Enum):
    reach_up = "Reach Bollinger Upper Band"
    reach_down = "Reach Bollinger Lower Band"
    normal='normal, no reacing neither up nor down'
    

class BollTrend(str,Enum):
    up = "Bollinger Middle Band Trend Up"
    down = "Bollinger Middle Band Trend Down"

class MeanPriceStatus(Enum):
    up_cross = "Up Cross"
    down_cross = "Down Cross"
    normal='No cross'

class MACDCrossStatus(Enum):
    gold = "macd line up cross signal line"
    dead = "macd line down cross signal line"
    normal="no crossover"

class Order(BaseModel):
    uid: str
    action: str 
    price: float
    share: int

class DealedOrder(BaseModel):
    buy_price: float
    sell_price: float
    dealed_price: float
    dealed_share: int



class News(BaseModel):
    title: str
    content: str
    date: Optional[datetime]
    keywords: Optional[List[str]]


class Stock(BaseModel):
    name: str
    main_business: Optional[List[str]]
    fundamental_information: Optional[str]
    fundamental_analysis: Optional[str]


class BollingerInfo(BaseModel):
    boll_status: Optional[BollStatus]
    boll_trend : Optional[BollTrend]

    def to_prompt(self):
        prompt = (
            f"The Bollinger info:\n"
            f"bollinger status:{self.boll_status.value}\n"
            f"bollinger trend: {self.boll_trend.value}"
        )
        return prompt


class MeanPriceInfo(BaseModel):
    sample_frequency: SampleFrequency
    long_period: int
    short_period: int
    cross: MeanPriceStatus

    def to_prompt(self):
        prompt = (
            f"The mean price is sampled by frequency {self.sample_frequency.value}\n"
            f"The long term period is {self.long_period} days, the short term period is {self.short_period}\n"
            f"The cross information is {self.cross.value}"
        )
        return prompt

class MACD(BaseModel):
    crossover: MACDCrossStatus
    divergence: Optional[str]
    histogram: Optional[str]
    
    def to_prompt(self):
        prompt = (
            f"MACD Info:\n"
            f"The macd line is {self.crossover.value} and the histogram is {self.histogram}"
        )
        return prompt


class StockPriceInfo(BaseModel):
    sample_frequency: SampleFrequency
    price: Optional[List[float]]
    volume: Optional[List[float]]

    def to_prompt(self):
        prompt = (
            f"Price Info List sampled by {self.sample_frequency.value}:\n"
            f"Price List: {self.price}\n"
            f"Volume List: {self.volume}"
        )
        return prompt

class StockTechInfo(BaseModel):
    # name: str
    price_infos: List[StockPriceInfo]
    mean_price_infos: Optional[List[MeanPriceInfo]]
    boll_info: Optional[BollingerInfo]
    macd_info: Optional[MACD]

    def to_prompt(self):
        price_prompt = '\n'.join([item.to_prompt() for item in self.price_infos])
        mean_price_prompt = '\n'.join([item.to_prompt() for item in self.mean_price_infos])
        prompt = (
            f"{price_prompt}\n"
            f"{mean_price_prompt}\n"
            f"{self.boll_info.to_prompt()}\n"
            f"{self.macd_info.to_prompt()}\n"
        )
        return str(prompt)
    
    def get_price_by_freq_and_index(self, freq:SampleFrequency=SampleFrequency.daily, index:int=-1):
        for price_info in self.price_infos:
            if price_info.sample_frequency ==freq:
                return price_info.price[index]
        return -1
    

class AgentInfo(BaseModel):
    role: AgentRole
    risk_tolerance: int
    greed: int
    investment_aggressiveness: int
    investment_style: Optional[InvestmentStyle]

    def to_prompt(self):
        prompt = f"Role Info: \n"
        prompt += f"Role:{self.role.value}\n"
        if self.investment_style:
            prompt += f"Investment style: {self.investment_style.value} \n"
        prompt += f"Risk tolerance (0-10): {self.risk_tolerance} {risk_tolerance_map[self.risk_tolerance]}\n"
        prompt += f"Greediness (0-10): {self.greed} {greed_map[self.greed]}\n"
        prompt += f"Investment aggressiveness (0-10): {self.investment_aggressiveness} {aggressiveness_map[self.investment_aggressiveness]}\n"
        return prompt


class RawMessage(BaseModel):
    content: str
    role: str    

class FundamentalInfo(BaseModel):
    stock_name: str
    main_business_info: str

    def to_prompt(self):
        return f"Fundamental Information of {self.stock_name}:\n{self.main_business_info}\n\n"

class AgentDecision(BaseModel):
    action: str
    probability: int
    percent:float

class ResponseAgent(BaseModel):
    risk_tolerance: int =Field( alias="Risk tolerance")
    investment_style: str = Field( alias="Investment style")
    investment_aggressiveness: str = Field( alias="Investment aggressiveness")
    decisions: List[AgentDecision]



