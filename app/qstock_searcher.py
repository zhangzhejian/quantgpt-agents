import sys
sys.path.append('../')
import qstock as qs
from typing import List
import utils, json
from prompt_generator import prompt_generator
from langchain.callbacks import get_openai_callback
from datetime import datetime
import pandas as pd

def get_stock_df(code):
    return qs.get_data(code)

def get_stock_name(code):
    df = qs.get_data(code)
    # print(df)
    return df['name'].iloc[-1]

def search_main_business(stock):
    df=qs.main_business(stock)
    select_period = df.head(1)['报告期'].values[0]
    cols = ['分类','营业收入(万)', '占主营收入比', '毛利率']
    df = df[(df['报告期'] == select_period) & (df['分类方向'] == '按行业分')][cols]
    dic = df.to_dict(orient='records')
    if len(dic) <= 0:
        return None
    result = {}
    result[f'报告期:{select_period}'] = dic
    return result

def get_all_industry_name_list() -> List[str]:
    name_list=qs.ths_index_name('行业')
    return name_list

'''
通过GPT总结新闻标题和内容的行业关键词
用于后续匹配股票的主营业务、所属行业、概念
'''
def determine_news_keywords():
    news = qs.news_data()
    # print(len(news))
    with get_openai_callback() as cb:
        for index, row in news.iterrows():
            if index >= 2:
                break
            print(index,row)
            prompt = prompt_generator.generate_prompt_news_keywords(title= row['标题'], content= row['内容'])
            print(f"prompt:{prompt}")
            result = utils.generate_single_message(prompt=prompt, temperature=0)
            print(f"prediction:{result}")
        print("total_cost:",cb.total_cost)

def get_news_keywords(news:List[dict]):
    titles = [item['标题'] for item in news]
    contents = [item['内容'] for item in news]
    with get_openai_callback() as cb:
        prompt = prompt_generator.generate_prompt_news_keywords_batch(titles, contents)
        print(f"prompt:{prompt}")
        result = utils.generate_single_message(prompt=prompt, temperature=0)
        result=result.replace("'", '"')
        print(f"prediction:{result}")
        print("total_cost:",cb.total_cost)
        return json.loads(result)

def determine_news_key_words_batch(batch_size=5) -> List[dict]:
    whole_size = 200
    news = qs.news_data()[-whole_size:]
    news['发布时间戳'] = news.apply(lambda row: datetime.combine(row['发布日期'], row['发布时间']), axis=1)
    news['发布时间戳'] = news['发布时间戳'].dt.strftime('%Y-%m-%d %H:%M:%S')
    news = news[['标题', '内容','发布时间戳']]
    news_dict_list = news.to_dict(orient='records')
    news.to_csv('news.csv')
    result = []
    for i in range(whole_size//batch_size + 1):
        result += get_news_keywords(news_dict_list[i*batch_size:(i+1)*batch_size])
    print(result)
    return result


def extract_from_stock_news(news: List[dict],name:str):
    prompt = prompt_generator.generate_prompt_extract_stock_news(news, stock_name=name)
    with get_openai_callback() as cb:
        print(f"prompt:\n{prompt}")
        result = utils.generate_single_message(prompt=prompt, temperature=0,model_name="gpt-4-32k")
        result=result.replace("'", '"')
        print(f"prediction:\n{result}")
        print("total_cost:",cb.total_cost)
        return json.loads(result)

def extract_from_stock_news_batch(code)-> tuple[List[dict], List[dict]]:
    name = get_stock_name(code)
    news = qs.news_data('个股', code=code)
    whole_size=100
    batch_size=10
    # news.to_csv('stock_news.csv')
    news = news[['date','title', 'content']]
    news_dict_list = news.to_dict(orient='records')
    extracted_from_news = []
    for i in range(whole_size//batch_size + 1):
        extracted_from_news += extract_from_stock_news(news_dict_list[i*batch_size:(i+1)*batch_size], name) if (i)*batch_size < len(news_dict_list)-1 else []

    return (news_dict_list,extracted_from_news)




def determine_news_correlation(title, content, stock_information):
    return

if __name__ == '__main__':
    code = '000155'
    print(get_stock_name(code))
    # print(get_all_industry_name_list())
    # determine_news_key_words_batch()
    search_main_business('000155')
    name_list=qs.ths_index_name('行业')
    print(len(name_list))
    # print(df=qs.eps_forecast())
    df=qs.intraday_money('中国平安')
    print(df)
    print(qs.stock_snapshot('中国平安'))
    news = qs.news_data()
    news.to_csv('news.csv')
    df=qs.get_data('000155')
    df = df.tail(20)
    # print(df)
    print(df['close'].values.tolist())
    print(df['volume'].values.tolist())

    # df=qs.get_data('000155',start='20220928',freq=101)
    # print(df)
    # df = df.tail(80)
    # # print(df)
    # print(df['close'].values.tolist())
    # print(df['volume'].values.tolist())
    df=qs.main_business('000155')
    print(df)
    print(search_main_business('000155'))