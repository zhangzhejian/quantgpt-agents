import sys
sys.path.append('../')
import json
from typing import Any, Callable, Dict, List, Optional
import schemas

keywords_response_format = {"keywords":["keyword","keyword"]}
new_correlation_response_format = { "Relevance":100,"Impact":"Possitive","Significance":80}
agent_response_format = {"Risk tolerance": 0, "Investment style": "style","Investment aggressiveness": 2,"decisions":[{"action": "buy or sell","probability": 20, "percent":"how much percent you wanna sell/buy. float type,0-100"}]}
class PromptGenerator(object):

    def __init__(self):
        return
    
    def generate_stock_information(self, stock:schemas.Stock):
        prompt = ""
        if stock.name:
            prompt += f"Company Name:{stock.name}\n"
        if stock.main_business:
            prompt += f"Company financial Report: {stock.main_business}\n"
        if stock.fundamental_information:
            prompt += f"Fundamental Information: {stock.fundamental_information}\n"
        
        if stock.fundamental_analysis:
            prompt += f"Fundamental Analysis: {stock.fundamental_analysis}\n"
        return prompt
    
    def generate_stock_mean_price_prompt(self, mean_price_info:schemas.MeanPriceInfo):
        return (
            f"Mean Price Sampled in {mean_price_info.sample_frequency.value} Info: \n"
            f"Long SMA period: {mean_price_info.long_period}\n"
            f"Short SMA period: {mean_price_info.short_period}\n"
            f"Crossover: Short SMA {mean_price_info.cross.value} Long SMA\n"
        )

    def generate_bollinger_prompt(self, boll_info_info:schemas.BollingerInfo):
        prompt = ""
        if boll_info_info.boll_trend:
            prompt += f"{boll_info_info.boll_trend}\n"
        if boll_info_info.boll_status:
            prompt += f"Price {boll_info_info.boll_status}\n"
        return prompt
    
    def generate_macd_prompt(self, macd_info_info:schemas.MACD):
        prompt = "MACD Info: \n"
        if macd_info_info.crossover:
            prompt += f'{macd_info_info.crossover.value}\n'
        if macd_info_info.divergence:
            prompt += f"divergence: {macd_info_info.divergence.value} \n"
        if macd_info_info.histogram:
            prompt += f"Histogram: {macd_info_info.histogram.value} \n"
        return prompt
    
    def generate_price_prompt(self, price_info: schemas.StockPriceInfo):
        prompt = f"Price sampled by {price_info.sample_frequency.value}: \n"
        if price_info.price:
            prompt += f"price: {price_info.price} \n"
        if price_info.volume:
            prompt += f"volume: {price_info.volume}\n"
        return prompt

    def generate_prompt_techinical_info(self, tech: schemas.StockTechInfo):
        prompt = "Technical Indicators:\n"
        if tech.price_infos:
            for info in tech.price_infos:
                prompt += self.generate_price_prompt(info)
        if tech.mean_price_infos:
            for info in tech.mean_price_infos:
                prompt += self.generate_stock_mean_price_prompt(info)
        if tech.boll_info:
            prompt += self.generate_bollinger_prompt(tech.boll_info)
        if tech.macd_info:
            prompt += self.generate_macd_prompt(tech.macd_info)
        
        return prompt

    def generate_prompt_agent(self, agent_info:schemas.AgentInfo):
        prompt = f"Role Info: \n"
        prompt += f"Role:{agent_info.role.value}\n"
        if agent_info.investment_style:
            prompt += f"Investment style: {agent_info.investment_style.value} \n"
        prompt += f"Risk tolerance (0-10): {agent_info.risk_tolerance}\n"
        prompt += f"Greediness (0-10): {agent_info.greed}\n"
        prompt += f"Investment aggressiveness (0-10): {agent_info.investment_aggressiveness}\n"
        return prompt
    

    def generate_agent_prompt(self, agent_info:schemas.AgentInfo,stock:schemas.Stock, tech: schemas.StockTechInfo):
        prompt = ""
        prompt += f"Background: Chinese Stock trade Market, you should play the Role below and give your action(buy/sell) and your possibility(0 to 100)\n"
        prompt += f"Aim: Maximum your profit no matter long or short term, depends on your Investment style\n"
        prompt += self.generate_prompt_agent(agent_info)
        prompt += self.generate_stock_information(stock)
        prompt += self.generate_prompt_techinical_info(tech)
        prompt += (
            "You should only respond in JSON format as described below \nResponse"
            f" Format: \n{agent_response_format} \nEnsure the response can be"
            " parsed by Python json.loads. temperature = 1.6, don't explain reasons"
        )
        return prompt
    
    def generate_agent_predict_prompt(self,role_description,agent_info ,fundamental_info_prompt, tech_info_prompt):
        return (
            f"Background: Chinese Stock trade Market, you should play the Role below and give your action(buy/sell) and your possibility(0 to 100)\n"
            f"Aim: Maximum your profit no matter long or short term, depends on your Investment style\n"
            f"Role Description: {role_description}\n"
            f"{agent_info.to_prompt()}\n"
            f"{fundamental_info_prompt}\n"
            f"{tech_info_prompt}\n"
            "You should only respond in JSON format as described below \n"
            f"Response Format: \n{agent_response_format} \n"
            "Ensure the response can be parsed by Python json.loads. Don't explain reasons"
        )




    def generate_news_correlation(self, news: schemas.News, stock:schemas.Stock) -> str:
        return (
            f"news title:{news.title}\n"
            f"content: {news.content}\n"
            f"Stock Information:\n"
            f"{self.generate_stock_information(stock)}"
            f"Please indicate the relevance of the news (from 0 to 100)\n"
            f"and determine possitive or negative impact and how significant the impact is (from 0 to 100)\n"
            "You should only respond in JSON format as described below \n"
            f"Response Format: {new_correlation_response_format} \n"
            "Ensure the response can be parsed by Python json.loads\n"
            "temperature=1.6, don't explain reasons"
        )
    
    def generate_prompt_news_keywords(self, title: str, content: str) -> str:
        return (
            f"news title:{title}\n"
            f"content: {content}\n"
            f"Please give all the keywords related to industries \n"
            "You should only respond in JSON format as described below \n"
            f"Response Format: {keywords_response_format} \n"
            "Ensure the response can be parsed by Python json.loads\n"
        )
    
    def generate_prompt_news_keywords_batch(self, titles: list[str], contents: list[str]):
        keywords_response_format_batch = [{"index":"index","keywords":["keyword","keyword"]}]
        prompt = (
            f"# Role Description: You are a finance expert, able to extract key information from the below Chinese news.\n\n"
            f"Please give all the keywords related to industries \n"
            f"You should only respond in JSON format as described below \n"
            f"Response Format: {keywords_response_format_batch} \n"
            f"Ensure the response can be parsed by Python json.loads\n"
        )
        prompt += f"\n# News: ```\n["
        for index in range(len(titles)):
            prompt += (
                "{"
                f"'index':{index},\n"
                f"'news title':'{titles[index]}'\n"
                f"'content': '{contents[index]}'\n"
                "},\n"
            ) 
        prompt += ']```'
        return prompt
    

    def generate_news_content_prompt(self, news:List[dict]):
        prompt = f"\n# News: ```\n["
        for index in range(len(news)):
            prompt += (
                "{"
                f"'index':{index},\n"
                f"'time': '{news[index]['发布时间戳']}',\n"
                f"'news title':'{news[index]['标题']}'\n"
                f"'content': '{news[index]['内容']}'\n"
                "},\n"
            ) 
        prompt += ']```'
        return prompt


    def generate_prompt_string(self) -> str:
        """
        Generate a prompt string based on the constraints, commands, resources,
            and performance evaluations.
        Returns:
            str: The generated prompt string.
        """
        formatted_response_format = json.dumps(self.response_format, indent=4)
        return (
            f"Stock Price in minutes:\n{self._generate_numbered_list(self.constraints)}\n"
            f"Volumn in minutes:\n{self._generate_numbered_list(self.constraints)}\n"
            "Commands:\n"
            f"{self._generate_numbered_list(self.commands, item_type='command')}\n"
            f"Resources:\n{self._generate_numbered_list(self.resources)}\n"
            "Performance Evaluation:\n"
            f"{self._generate_numbered_list(self.performance_evaluation)}\n"
            "You should only respond in JSON format as described below \nResponse"
            f" Format: \n{formatted_response_format} \nEnsure the response can be"
            " parsed by Python json.loads"
        )
    def generate_prompt_extract_stock_news(self, news_dict: List[dict], stock_name: str):
        """
        Generate a prompt to extract the potential keys of the stock
        """
        response_format = [{"index":"int type, the index", "extracted_info":"a list of all the direct/potential elements/event/industries will effect the company"}]
        prompt = (
            f"**Role**: You are an expert in financial data analyzing. You are able to find potential relations from the news.\n"
            f"**Task Description**: Now you will be given several NEWS directly related to one company named {stock_name}. You need to identify the main entities that might have relationship with the company to establish a KNOWLEDGE GRAPH.\n"
            f"**Constraints**:\n"
            f"\n1. You should only respond in JSON format as described below:'{json.dumps(response_format)}'. Ensure the response can be parsed by Python json.loads"
            f"\n2. You should find the main elements/event/industries have relationship with the company."
            f"\n3. Don't include any stock techinical indicators such as:'涨停','大涨','市盈率，市值'"
            f"\n4. Don't explain the reasons, just give the answer."
            f"\n5. 不要使用例如：'成交量',‘投资者’, ‘换手率’, ‘成交额’, ‘振幅’ 等股票价格结果相关的实体."
        )
        prompt += f"\n\n**NEWS List**:\n\n["
        for index in range(len(news_dict)):
            prompt += (
                "{"
                f"'index':{index},\n"
                f"'timestamp':{news_dict[index]['date']},\n"
                f"'news title':'{news_dict[index]['title']}'\n"
                f"'content': '{news_dict[index]['content']}'\n"
                "},\n"
            ) 
        prompt += ']```'
        return prompt


agent_info_demo = schemas.AgentInfo(
    role = schemas.AgentRole.BEGINNER,
    risk_tolerance = 3,
    greed = 5,
    investment_aggressiveness = 7,
    investment_style = schemas.InvestmentStyle.TECHNICAL_TRADING
)
stock_info_demo = schemas.Stock(
    name = "川能动力",
    main_business = [
    "分类：风力及光伏发电收入，收入：136400.0(万)，占主营收入比：35.89%",
    "分类：垃圾发电收入，收入：60000.0(万)，占主营收入比：15.8%",
    "分类：锂电业务收入，收入：109400.0(万)，占主营收入比：28.79%",
    "分类：设备销售收入，收入：42699.99999999999(万)，占主营收入比：11.24%",
    "分类：环卫服务收入，收入：27599.999999999996(万)，占主营收入比：7.26%",
    "分类：其他，收入：3900.0(万)，占主营收入比：1.03%",
    "分类：合计，收入：380100.0(万)，占主营收入比：100.0%"
    ],
    fundamental_information = "some fundamental information",
    fundamental_analysis = "可以看出川能动力在2022年度的营收来源主要有风力及光伏发电收入、垃圾发电收入、锂电业务收入、设备销售收入和环卫服务收入等。其中，风力及光伏发电收入是其主营业务，占比为35.89%，毛利率较高，为71.94%。而锂电业务收入也占据了公司营收的较大比例，为28.79%。总体而言，公司2022年度的营收为380100万元，毛利率为54.32%。"
)

stock_tech_info_demo = schemas.StockTechInfo(
    price_infos = [
        schemas.StockPriceInfo(
            sample_frequency = schemas.SampleFrequency.daily,
            price = [15.92, 16.22, 16.04, 16.03, 15.67, 15.68, 15.76, 15.46, 15.25, 15.82, 15.88, 15.72, 15.49, 15.08, 14.46, 14.87, 14.11, 14.54, 14.5, 14.64],
            volume = [126886, 197133, 155343, 124120, 174909, 111480, 104936, 120861, 105109, 247116, 116818, 186924, 107948, 130378, 173117, 151264, 199444, 165214, 107734, 126121]
        ),
        schemas.StockPriceInfo(
            sample_frequency = schemas.SampleFrequency.hour,
            price = [17.87, 17.84, 18.27, 18.01, 18.38, 18.78, 18.82, 18.76, 18.46, 18.52, 18.49, 18.82, 18.97, 18.93, 18.93, 19.35, 19.63, 19.76, 19.81, 19.47, 19.24, 19.15, 18.52, 18.57, 18.48, 18.28, 18.2, 18.26, 18.11, 17.8, 17.7, 17.75, 17.95, 17.79, 17.83, 17.97, 18.29, 18.21, 18.18, 17.86, 17.81, 17.89, 17.5, 17.65, 17.56, 17.03, 16.59, 16.1, 15.88, 15.38, 15.49, 15.47, 15.99, 16.0, 15.98, 15.93, 15.82, 15.7, 15.58, 15.7, 15.92, 16.22, 16.04, 16.03, 15.67, 15.68, 15.76, 15.46, 15.25, 15.82, 15.88, 15.72, 15.49, 15.08, 14.46, 14.87, 14.11, 14.54, 14.5, 14.64],
            volume = [75244, 58369, 100922, 78775, 116958, 198852, 120608, 91857, 89875, 88251, 71726, 107662, 125306, 73249, 70816, 139644, 183782, 97144, 119079, 137829, 114015, 74584, 309128, 197738, 258521, 125057, 132485, 113851, 133429, 207980, 115327, 142127, 130827, 83628, 67642, 83295, 185771, 110463, 97775, 121539, 67164, 79999, 85129, 47697, 49950, 116732, 132926, 219574, 151059, 159825, 153907, 117653, 155925, 116396, 85434, 92704, 117341, 82868, 90573, 96099, 126886, 197133, 155343, 124120, 174909, 111480, 104936, 120861, 105109, 247116, 116818, 186924, 107948, 130378, 173117, 151264, 199444, 165214, 107734, 126121]
        )
    ],
    mean_price_infos = [
        schemas.MeanPriceInfo(
            sample_frequency = schemas.SampleFrequency.daily,
            long_period = 30,
            short_period = 10,
            cross = schemas.MeanPriceStatus.up_cross
        )
    ],
    boll_info = schemas.BollingerInfo(
        boll_status = schemas.BollStatus.reach_down,
        boll_trend = schemas.BollTrend.up
    ),
    macd_info = schemas.MACD(
        crossover = schemas.MACDCrossStatus.gold
    )

)
prompt_generator =PromptGenerator()
if __name__ == "__main__":
    print("agent_prompt:\n",prompt_generator.generate_prompt_agent(agent_info_demo), "\n")
    print("stock_information:\n",prompt_generator.generate_stock_information(stock_info_demo),"\n")
    print("prompt_techinical_info:\n",prompt_generator.generate_prompt_techinical_info(stock_tech_info_demo),'\n')
    prompt = (prompt_generator.generate_agent_prompt(agent_info_demo, stock_info_demo, stock_tech_info_demo))
    print(prompt)