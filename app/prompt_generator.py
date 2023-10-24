import json
from typing import Any, Callable, Dict, List, Optional
import schemas

keywords_response_format = {"keywords":["keyword","keyword"]}
new_correlation_response_format = { "Relevance":100,"Impact":"Possitive","Significance":80}
agent_response_format = {"Risk tolerance": 0, "Investment style": "style","Investment aggressiveness": 2,"decisions":[{"action": "buy or sell","probability": 20, "percent":"how much percent you wanna sell/buy. float type,0-100"}]}


def generate_stock_information( stock:schemas.Stock):
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

def generate_stock_mean_price_prompt( mean_price_info:schemas.MeanPriceInfo):
    return (
        f"Mean Price Sampled in {mean_price_info.sample_frequency.value} Info: \n"
        f"Long SMA period: {mean_price_info.long_period}\n"
        f"Short SMA period: {mean_price_info.short_period}\n"
        f"Crossover: Short SMA {mean_price_info.cross.value} Long SMA\n"
    )

def generate_bollinger_prompt( boll_info_info:schemas.BollingerInfo):
    prompt = ""
    if boll_info_info.boll_trend:
        prompt += f"{boll_info_info.boll_trend}\n"
    if boll_info_info.boll_status:
        prompt += f"Price {boll_info_info.boll_status}\n"
    return prompt

def generate_macd_prompt( macd_info_info:schemas.MACD):
    prompt = "MACD Info: \n"
    if macd_info_info.crossover:
        prompt += f'{macd_info_info.crossover.value}\n'
    if macd_info_info.divergence:
        prompt += f"divergence: {macd_info_info.divergence.value} \n"
    if macd_info_info.histogram:
        prompt += f"Histogram: {macd_info_info.histogram.value} \n"
    return prompt

def generate_price_prompt( price_info: schemas.StockPriceInfo):
    prompt = f"Price sampled by {price_info.sample_frequency.value}: \n"
    if price_info.price:
        prompt += f"price: {price_info.price} \n"
    if price_info.volume:
        prompt += f"volume: {price_info.volume}\n"
    return prompt

def generate_prompt_techinical_info( tech: schemas.StockTechInfo):
    prompt = "Technical Indicators:\n"
    if tech.price_infos:
        for info in tech.price_infos:
            prompt += generate_price_prompt(info)
    if tech.mean_price_infos:
        for info in tech.mean_price_infos:
            prompt += generate_stock_mean_price_prompt(info)
    if tech.boll_info:
        prompt += generate_bollinger_prompt(tech.boll_info)
    if tech.macd_info:
        prompt += generate_macd_prompt(tech.macd_info)
    
    return prompt

def generate_prompt_agent( agent_info:schemas.AgentInfo):
    prompt = f"Role Info: \n"
    prompt += f"Role:{agent_info.role.value}\n"
    if agent_info.investment_style:
        prompt += f"Investment style: {agent_info.investment_style.value} \n"
    prompt += f"Risk tolerance (0-10): {agent_info.risk_tolerance}\n"
    prompt += f"Greediness (0-10): {agent_info.greed}\n"
    prompt += f"Investment aggressiveness (0-10): {agent_info.investment_aggressiveness}\n"
    return prompt




def generate_agent_predict_prompt(
                                    role_description: str,agent_info:schemas.AgentInfo ,
                                    fundamental_info_prompt: str, tech_info_prompt: str, news_prompt = None):
    return (
        f"**Background**: Chinese Stock trade Market, you should play the Role below and give your action(buy/sell) and your possibility(0 to 100)\n"
        f"**Aim**: Maximum your profit no matter long or short term, depends on your Investment style\n"
        f"**Constraints**:\n\n1. Circuit Breaker System: To prevent excessive volatility, China's A-share market has a circuit breaker system in place. In most cases, the daily price fluctuation of a stock is limited to within 10%. Newly listed stocks are not subjected to this limit initially.\n"
        f"2. T+1 Trading System: The Chinese stock market operates on a T+1 trading system, which means stocks purchased on a given day can only be sold on the following day or later, prohibiting intraday buying and selling.\n"
        f"Role Description: {role_description}\n"
        f"{agent_info.to_prompt()}\n"
        f"{fundamental_info_prompt}\n"
        f"{tech_info_prompt}\n"
        "You should only respond in JSON format as described below \n"
        f"Response Format: \n{agent_response_format} \n"
        "Ensure the response can be parsed by Python json.loads. Don't explain reasons"
    )



def genrate_agent_predict_prompt_with_news_normal(
                                    role_description: str,agent_info:schemas.AgentInfo ,
                                    fundamental_info_prompt: str, tech_info_prompt: str,
                                    news_prompt: str)->str:
    return (
        f"**Background**: Chinese Stock trade Market, you should play the Role below and give your action(buy/sell) and your possibility(0 to 100)\n"
        f"**Aim**: Maximum your profit in short term, depends on your Investment style\n"
        f"**Role Description**: {role_description}\n"
        f"{agent_info.to_prompt()}\n"
        f"**Stock Fundamental Info**:{fundamental_info_prompt}\n"
        f"**Technical indicators Info**:{tech_info_prompt}\n"
        f"**Related News**:{news_prompt}\n\n"
        "You should only respond in JSON format as described below \n"
        f"Response Format: \n{agent_response_format} \n"
        "Ensure the response can be parsed by Python json.loads. Don't explain reasons"
    )

def genrate_agent_predict_prompt_with_news_multi_key():
    return




def generate_news_correlation( news: schemas.News, stock:schemas.Stock) -> str:
    return (
        f"news title:{news.title}\n"
        f"content: {news.content}\n"
        f"Stock Information:\n"
        f"{generate_stock_information(stock)}"
        f"Please indicate the relevance of the news (from 0 to 100)\n"
        f"and determine possitive or negative impact and how significant the impact is (from 0 to 100)\n"
        "You should only respond in JSON format as described below \n"
        f"Response Format: {new_correlation_response_format} \n"
        "Ensure the response can be parsed by Python json.loads\n"
        "temperature=1.6, don't explain reasons"
    )

def generate_prompt_news_keywords( title: str, content: str) -> str:
    return (
        f"news title:{title}\n"
        f"content: {content}\n"
        f"Please give all the keywords related to industries \n"
        "You should only respond in JSON format as described below \n"
        f"Response Format: {keywords_response_format} \n"
        "Ensure the response can be parsed by Python json.loads\n"
    )

def generate_prompt_news_keywords_batch( titles: list[str], contents: list[str]):
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


def generate_news_content_prompt( news:List[dict]):
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


# def generate_prompt_string() -> str:
#     """
#     Generate a prompt string based on the constraints, commands, resources,
#         and performance evaluations.
#     Returns:
#         str: The generated prompt string.
#     """
#     formatted_response_format = json.dumps(response_format, indent=4)
#     return (
#         f"Stock Price in minutes:\n{_generate_numbered_list(constraints)}\n"
#         f"Volumn in minutes:\n{_generate_numbered_list(constraints)}\n"
#         "Commands:\n"
#         f"{_generate_numbered_list(commands, item_type='command')}\n"
#         f"Resources:\n{_generate_numbered_list(resources)}\n"
#         "Performance Evaluation:\n"
#         f"{_generate_numbered_list(performance_evaluation)}\n"
#         "You should only respond in JSON format as described below \nResponse"
#         f" Format: \n{formatted_response_format} \nEnsure the response can be"
#         " parsed by Python json.loads"
#     )
def generate_prompt_extract_stock_news( news_dict: List[dict], stock_name: str):
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


def generate_agent_prompt( agent_info:schemas.AgentInfo,stock:schemas.Stock, tech: schemas.StockTechInfo):
    prompt = ""
    prompt += f"Background: Chinese Stock trade Market, you should play the Role below and give your action(buy/sell) and your possibility(0 to 100)\n"
    prompt += f"Aim: Maximum your profit no matter long or short term, depends on your Investment style\n"
    prompt += generate_prompt_agent(agent_info)
    prompt += generate_stock_information(stock)
    prompt += generate_prompt_techinical_info(tech)
    prompt += (
        "You should only respond in JSON format as described below \nResponse"
        f" Format: \n{agent_response_format} \nEnsure the response can be"
        " parsed by Python json.loads. temperature = 1.6, don't explain reasons"
    )
    return prompt

