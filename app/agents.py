import time
import schemas
import random
import json
from typing import List
from prompt_generator import generate_agent_predict_prompt
from utils import generate_single_message,agenerate_n_message
import uuid
from configs import GLOBAL_VERBOSE

class BaseTraderAgent(object):
    role :schemas.AgentRole = None
    def __init__(self):
        self.verbose = GLOBAL_VERBOSE
        self.role_description = None
        self.prompt_func = generate_agent_predict_prompt
        # self.role: schemas.AgentRole = role
        self.uid = f"{self.role.value}_{uuid.uuid4().hex}"

        self.agent_info = schemas.AgentInfo(
            role = self.role,
            risk_tolerance = 1,
            greed = 0,
            investment_aggressiveness = 1,
            investment_style = schemas.InvestmentStyle.VALUE_INVESTING.value
        )

        # self.risk_tolerance = 1 #风险承受能力
        # self.agressiveness = 1 #激进度
        # self.investment_style = None    #投资风格:[短期博弈,中期趋势,长期价值]
        # self.greddy_level = 1   #贪婪程度
        self.news_info = None
        self.hold_share = 1000     #持仓份额
        self.current_round = 0  #当前迭代轮数
        self.previous_actions = []
        self.next_action = None
        self.current_stock_price = 1
        self.price_floating_percent = 0.02
        self.buy_probability,self.sell_probability,self.sell_percent,self.buy_percent =0,0,0,0
    
    def __repr__(self):
        return (
            f"\nuid: {self.uid}\n"
            f"cash:{self.cash}, cost:{self.cost}, share:{self.shares}"
         )

    def _init_price_info(self):
        
        return
    
    def set_news_info(self, news_info):
        self.news_info = news_info

    def set_prompt_func(self, func:callable):
        self.prompt_func = func
    
    def set_price(self,price: float=1):
        self.current_stock_price = price

    def _init_property(self, cash_mid, share_mean, cost_mean):
        self.cash=10000
        self.hold_share=1000
    
    def set_property(self,cost,cash,shares):
        self.cash=cash
        self.shares=shares
        self.cost=cost

    def _agent_info(self):
        return self.agent_info
    
    def set_agent_params(self, agent_info:schemas.AgentInfo):
        self.agent_info=agent_info

    
    def set_stock_infos(self,fundamental_info_prompt: str, tech_info_prompt:str, news_info:str):
        self.fundamental_info_prompt =fundamental_info_prompt
        self.tech_info_prompt =tech_info_prompt
        self.set_news_info(news_info)

    def set_params(self, agent_params):
        (cost, cash) = agent_params
        self.cash = cash
        self.cost = cost

    async def apredict_believes(self,n:int=5, temperature:float = 0.5)-> List[schemas.ResponseAgent]:
        prompt = self.prompt_func(
            role_description=self.role_description,
            agent_info=self._agent_info(),
            fundamental_info_prompt=self.fundamental_info_prompt,
            tech_info_prompt=self.tech_info_prompt,
            news_prompt = self.news_info
        )
        if self.verbose:
            print(prompt)
        generations=await agenerate_n_message(prompt=prompt, temperature=temperature, n = n)
        responses = []
        for item in generations.generations[0]:
            text = item.text
            text= text.replace("'", '"')
            response_obj = schemas.ResponseAgent.parse_raw(text)
            responses.append(response_obj)
        print(responses)
        return responses

    
    def predict_belief(self) -> schemas.ResponseAgent:
        prompt = self.prompt_func(
            role_description=self.role_description,
            agent_info=self._agent_info(),
            fundamental_info_prompt=self.fundamental_info_prompt,
            tech_info_prompt=self.tech_info_prompt,
            news_prompt = self.news_info
        )
        if self.verbose:
            print(prompt)
        completion=generate_single_message(prompt=prompt, temperature=1.2)
        completion = completion.replace("'", '"')
        # print(completion)
        # json_obj = json.loads(completion)
        # print(json_obj)
        response_obj = schemas.ResponseAgent.parse_raw(completion)
        return response_obj
    
    def set_agent_belief(self, agent_response:schemas.ResponseAgent):
        buy_probability, buy_percent, sell_probability, sell_percent = 0,0,0,0
        for decision in agent_response.decisions:
            if decision.action.lower() == 'buy':
                buy_probability = decision.probability
                buy_percent = decision.percent
            elif decision.action.lower() == 'sell':
                sell_percent=decision.percent
                sell_probability = decision.probability
        
        self.belief(buy_probability, buy_percent, sell_probability, sell_percent)

        # for decision in response_obj.decisions:

        

    def set_cost(self, cost):
        self.cost = cost

    def generate_order(self, action, price, share ) -> schemas.Order:
        return schemas.Order(
            uid = self.uid,
            action = action,
            price = price,
            share = share
        )
    
    def percept(self, current_price):
        self.current_stock_price = current_price
        return

    def belief(self, buy_probability, buy_percent, sell_probability, sell_percent):
        self.buy_probability = buy_probability
        self.buy_percent = buy_percent
        self.sell_probability = sell_probability
        self.sell_percent = sell_percent
    
    def plan(self) -> List[schemas.Order]:
        orders = []
        low, high = round(self.current_stock_price * (1-self.price_floating_percent), 2), round(self.current_stock_price * (1+self.price_floating_percent), 2)
        if random.random() <= self.buy_probability and self.cash > 0 and self.buy_percent > 0:
            buy_price = round(random.uniform(low, high),3)
            share = int(self.cash * self.buy_percent / buy_price / 100)
            orders.append(self.generate_order(
                action='buy',
                price = buy_price,
                share = share
            ))
        if random.random() <= self.sell_probability and self.shares > 0:
            sell_price = round(random.uniform(low, high),3)
            share = int(self.hold_share * self.sell_percent / 100)
            orders.append(self.generate_order(
                action='sell',
                price = sell_price,
                share = share
            ))
        return orders
    
    def execute(self):
        '''
        generate buy/sell orders
        generate target prices
        '''
        #do something
        self.previous_actions.append(self.next_action)
        self.next_action = None
        return
    

    def run(self):
        
        return
    


class BeginnerTrader(BaseTraderAgent):
    role:schemas.AgentRole = schemas.AgentRole.BEGINNER
    def __init__(self,):
        super(BeginnerTrader, self).__init__()

        self.role_description = """
        Role Description: You are a beginner stock trader, having recently stepped into the world of stock trading with a modest amount from your salary and savings. You are navigating the complexities of the stock market, eager to grow your financial portfolio.

        Examples: 
        - If your investment aggressiveness is high, you are exploring various stocks, ready to take calculated risks for potential higher returns. You are constantly educating yourself about market trends and maybe even dabbling in some blue-chip stocks or tech startups with promising growth.
        - If your investment aggressiveness is low, you prefer sticking to safer investment options, aiming for a steady growth pattern that would give you about a 7% annualized rate of return. You likely lean towards dividend stocks, bonds, or ETFs that track the broader market.
        - If your greediness is high, you find yourself often contemplating larger gains, which makes you consider adjusting your take-profit price upwards. Sometimes, you are tempted by the rapid gains from day trading or high-growth stocks, even though you know it involves higher risks.

        Behavioral Guidelines:
        - Your trading volume is not significant enough to influence market prices, ensuring that your actions do not affect stock market dynamics.
        - You are aware of your limited experience and are cautious about not overextending your financial resources. You often seek educational resources or advice from more experienced traders.
        - You understand the importance of diversification and try to apply it within the constraints of your available funds.
        - Emotionally, you find yourself between excitement and anxiety, often tracking stock prices several times a day and pondering your next moves.

        Remember, as a beginner trader, each decision is a learning opportunity, and each trade contributes to your experience, helping you to become more confident and informed in your future trading strategies.

        """
        # self.role_description = """
        # You are a beginner stock trader, using your salary and savings. The amount is not large.
        # if your investment_aggressiveness is high, it means you attempt to earn more extra money.
        # if your investment_aggressiveness is low, it means you just want to have about 7% Annualized rate of return.
        # if your greediness is high, it means you wanna earn more benifits and increase take profit price."
        # your trading action will not affect the market.
        # """

        self.agent_info = schemas.AgentInfo(
            role = self.role,
            risk_tolerance = 1,
            greed = 1,
            investment_aggressiveness = 1,
            investment_style = schemas.InvestmentStyle.ACTIVITE_INVESTING.value
        )
        
    
    


class SeniorTrader(BaseTraderAgent):
    role:schemas.AgentRole = schemas.AgentRole.SENIOR
    def __init__(self,):
        super(SeniorTrader, self).__init__()

        # self.role_description = """
        # You are a senior stock trader using the funds raised for investment.
        # You hope to achieve a better performance than other similar funds in the same time period, and need to consider whether to use game or cooperation tactics to achieve this.
        # Your fund has a large amount of capital, so you need to consider the impact of buying and selling on market performance.
        # """
        self.role_description = """
        Senior Trader: You are a senior stock trader, renowned in the trading community for your decades of experience and keen market insights. You are responsible for managing a substantial portfolio, often encompassing multi-million dollar positions across various asset classes.
            - **Asset Distribution**: Given your vast experience, your portfolio is diverse, ranging from blue-chip stocks, growth stocks, ETFs, commodities, to foreign exchange.
            - **Investment Philosophy**: Over the years, you've developed a refined trading strategy that melds technical analysis with fundamental research.
            
            if your investment_aggressiveness is high:
            - **Approach**: You employ strategies such as high-frequency trading or leveraged investments to amplify returns. You are not averse to dabbling in volatile sectors, emerging markets, or innovative industries like biotech and fintech.
            - **Objective**: Your primary goal is to beat market benchmarks consistently, aiming for top-tier returns.

            if your investment_aggressiveness is low:
            - **Approach**: You lean heavily on blue-chip stocks, established companies, and government or corporate bonds. You might also have a significant position in precious metals as a hedge against market volatility.
            - **Objective**: Your primary aim is wealth preservation with steady growth, targeting returns that outpace inflation while avoiding significant drawdowns.

            if your greediness is high:
            - **Risk Management**: While you have risk management strategies in place, your focus tends to be on maximizing each trade's profit potential. This might involve holding positions longer than initially planned or leveraging positions to amplify gains.
            - **Trading Frequency**: You are an active trader, making multiple trades per week, if not per day. Your keen eye is always on the lookout for short-term opportunities or market inefficiencies.

            if your greediness is low:
            - **Risk Management**: You employ stringent stop-loss orders, diversification strategies, and often consult with risk management tools or teams before making substantial moves.
            - **Trading Frequency**: You believe in the 'buy and hold' strategy, making infrequent trades, focusing instead on the long-term value proposition of each asset.

            Market Influence: Given the size and volume of your trades, your actions have the potential to cause minor price movements, especially when dealing with small-cap stocks or less liquid markets. This influence demands discretion and strategy in execution to avoid inadvertently moving the market.

        """
    
        self.agent_info = schemas.AgentInfo(
            role = self.role,
            risk_tolerance = 1,
            greed = 1,
            investment_aggressiveness = 1,
            investment_style = schemas.InvestmentStyle.VALUE_INVESTING.value
        )

class FundManager(BaseTraderAgent):
    role:schemas.AgentRole = schemas.AgentRole.FUNDMANAGER
    def __init__(self,):
        super(FundManager, self).__init__()

        self.role_description = """
        You are a fund manager, using the funds raised for investment.
        You hope to achieve a better performance than other similar funds in the same time period, and need to consider whether to use game or cooperation tactics to achieve this.
        Your fund has a large amount of capital, so you need to consider the impact of buying and selling on market performance.
        """
        self.agent_info = schemas.AgentInfo(
            role = self.role,
            risk_tolerance = 1,
            greed = 1,
            investment_aggressiveness = 1,
            investment_style = schemas.InvestmentStyle.VALUE_INVESTING.value
        )
    

    def generate_market_comment(self):
        prompt = f""
        prompt += self.role_description
        prompt += '\n\n'
        prompt += "Command:\n Please generate a comment or news about the stock, based on its recent prices, techinical indicators and fundamental information of the company."
        prompt += "The comment or news is faced to beginner and senior traders, try to affect their judgment, to let you be in a benificial position in this game."
        prompt += "For example, if you wanna buy this stock in a lower price, you should generate a negative comment about this stock, to let others sell the stock."
        prompt += "If your cost is pretty low and you got some profits and wanna sell stock, you should generate a positive comment to affect them buy the stock, which will make the price remains when you selling."
        prompt += "You need to take into account the recipient's current decision preferences in order to enhance or change them."
        prompt += '\n\n'
        return prompt

