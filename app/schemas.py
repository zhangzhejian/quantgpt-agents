from pydantic import BaseModel,Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

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
        prompt += f"Risk tolerance (0-10): {self.risk_tolerance}\n"
        prompt += f"Greediness (0-10): {self.greed}\n"
        prompt += f"Investment aggressiveness (0-10): {self.investment_aggressiveness}\n"
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


# class Message(BaseModel):
#     """list[<role>: <content>]"""
#     content: str
#     role: str = field(default='user')  # system / user / assistant
#     cause_by: Type["Action"] = field(default="")
#     sent_from: str = field(default="")
#     send_to: str = field(default="")

#     def __str__(self):
#         # prefix = '-'.join([self.role, str(self.cause_by)])
#         return f"{self.role}: {self.content}"

#     def __repr__(self):
#         return self.__str__()

#     def to_dict(self) -> dict:
#         return {
#             "role": self.role,
#             "content": self.content
#         }


    