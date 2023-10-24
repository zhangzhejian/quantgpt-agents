import numpy as np
import schemas
from agents import BaseTraderAgent,BeginnerTrader, FundManager,SeniorTrader
from typing import List
from utils import generate_single_message


class BaseAgentDelegater():
    def __init__(self):
        clss = [SeniorTrader, BeginnerTrader, FundManager]
        self.agents:List[BaseTraderAgent] = []
        for cls in clss:
            self.agents += self._init_agents(cls=cls, size=5)
        self._init_agents_property(
            mean_cost=10,
            sigma=0,
            size=len(self.agents),
            mean_cash=10000,
            mean_share=1000
        )
        return
    
    
    def set_agents_prompt_func(self, prompt_func:callable):
        for agent in self.agents:
            agent.set_prompt_func(prompt_func)

    def generate_normal_distribution(self, mean, sigma, size):
        """
        Generate a normal distribution with a custom mean and standard deviation (sigma).
        
        :param mean: The mean value of the normal distribution.
        :param sigma: The standard deviation (sigma) of the normal distribution.
        :param size: The number of samples to generate.
        :return: A numpy array containing the generated samples.
        """
        return np.random.normal(loc=mean, scale=sigma, size=size).tolist()
    
    def _init_agents(self,cls, size):
        return [cls() for _ in range(size)]
    
    # def _get_agents(self, cls, size):
        # return [cls() for _ in range(size)]
    
    def _init_agents_property(self, mean_cost, sigma, size, mean_cash, mean_share):
        cost_distribution = self.generate_normal_distribution(mean_cost, mean_cost / 5, size)
        cash_distribution = self.generate_normal_distribution(mean_cash, mean_cash / 5, size)
        share_distribution = self.generate_normal_distribution(mean_share, mean_share / 5, size)
        property_params = zip( cost_distribution, cash_distribution, share_distribution)
        for index, item in enumerate(property_params):
            cost, cash, shares = item
            self.agents[index].set_property(cost, cash, shares)
    
    def predict_belief(self) -> List[schemas.Order]:
        order_list = []
        for agent in self.agents:
            belief = agent.predict_belief()
            agent.set_agent_belief(belief)
            orders = agent.plan()
            order_list += orders
        return order_list
    
    async def apredict_believes(self):
        order_list = []
        for agent in self.agents:
            belief = await agent.apredict_believes()
            agent.set_agent_belief(belief)
            orders = agent.plan()
            order_list += orders
        return order_list
        

    def _init_stock_info(self,fundamental_info_prompt: str, tech_info_prompt:str, price: float, news_info: str):
        for agent in self.agents:
            agent.set_stock_infos(
                fundamental_info_prompt=fundamental_info_prompt,
                tech_info_prompt=tech_info_prompt,
                news_info=news_info
            )
            agent.set_price(price)
    
            