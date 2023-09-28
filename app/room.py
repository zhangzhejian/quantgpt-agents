from agents import BeginnerTrader,SeniorTrader,FundManager, BaseTraderAgent
from stock_analyzer import stock_analyzer
import schemas 
from qstock_searcher import search_main_business, get_stock_name,determine_news_key_words_batch,extract_from_stock_news_batch
import json
from multi_key_index import IndexStore, IndexNode, TextChunk
import tqdm
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os, json
import pickle
from typing import Tuple, List
import time
PARSE_FOLDER_PATH = os.path.join(os.getcwd(), 'parse_res')
# 读取 .env file.
load_dotenv()
openai_api_key= os.getenv('LITELLM_OPENAI_API_KEY')
openai_api_base= os.getenv('LITELLM_OPENAI_API_BASE')

class Room(object):

    def __init__(self,):
        self.code = '002855'
        # get_news_by_stock('002330')
        # determine_news_key_words_batch()
        self._init_stock_topics(self.code)
        self.fundamental_info =self._init_fundamental_info(self.code)
        self.index_store = self._init_news_vectorstore()
        self._init_agents()
        return
    

    def _init_agents(self):
        self.agents = [BeginnerTrader(),SeniorTrader(),FundManager()]
        for agent in self.agents:
            agent.percept(self.current_price_info.price[-1])
    

    def _init_fundamental_info(self, code):
        self.stock_name= get_stock_name(code)
        main_business_info = search_main_business(code)
        return schemas.FundamentalInfo(
            stock_name=self.stock_name,
            main_business_info=json.dumps(main_business_info, indent=2,ensure_ascii=False)
        )
        # print(self.fundamental_info.to_prompt())
    

    def _init_stock_news_info(self):
        return

    
    def _init_stock_topics(self, code):
        self.stock_code= code
        self.stock_tech_info = stock_analyzer.generate_tech_infos(code)
        self.current_price_info = self.stock_tech_info.price_infos[0]
        # print(self.stock_tech_info.to_prompt())

    def _init_news_vectorstore(self):
        # embedding = OpenAIEmbeddings(openai_api_key=openai_api_key,
        #             openai_api_base=openai_api_base)
        index_store:IndexStore = IndexStore()
        if os.path.exists('index_store.json'):
            index_store.load_from_file('index_store.json')
            print(index_store.chunks)
            return
        (news_dict_list,extracted_from_news) = extract_from_stock_news_batch(self.code)
        print(len(news_dict_list), len(extracted_from_news))
        index_store:IndexStore = IndexStore()
        start_ = time.time()
        for i in range(len(news_dict_list)):
            content = news_dict_list[i]['content']
            extracted_list = extracted_from_news[i]['extracted_info']
            index_nodes = []
            # embeddings = embedding.embed_documents(texts = extracted_list)
            for index,item in enumerate(extracted_list):
                node = IndexNode(
                    content=item,
                    id = hash(item),
                )
                index_nodes.append(node)
                if not index_store.contains(item):
                    index_store.add_node(node)
                    
            index_store.add_chunk(TextChunk(
                id = hash(content),
                content=content,
                index_node_ids = [item.id for item in index_nodes]
            ))
        print(time.time()-start_)
        # print([item.dict() for item in index_store.chunks])
        # print(index_store.node_to_chunk)
        index_store.save('index_store.json')
        return index_store


if __name__ == '__main__':
    room = Room()
    agent = BeginnerTrader()
    # agent.set_stock_infos(
    #     fundamental_info_prompt=room.fundamental_info.to_prompt(),
    #     tech_info_prompt=room.stock_tech_info.to_prompt()
    # )
    # agent.predict_belief()

    senior_agent = SeniorTrader()
    senior_agent.set_stock_infos(
        fundamental_info_prompt=room.fundamental_info.to_prompt(),
        tech_info_prompt=room.stock_tech_info.to_prompt()
    )
    senior_agent.predict_belief()
    print(senior_agent.plan())

    # fund_agent = FundManager()
    # fund_agent.set_stock_infos(
    #     fundamental_info_prompt=room.fundamental_info.to_prompt(),
    #     tech_info_prompt=room.stock_tech_info.to_prompt()
    # )
    # fund_agent.predict_belief()
    # print(fund_agent.plan())
