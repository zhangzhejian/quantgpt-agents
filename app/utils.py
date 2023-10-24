from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from configs import OPENAI_API_KEY, OPENAI_API_BASE
from langchain.schema.messages import (
    HumanMessage,
)
from langchain.schema import (
    LLMResult,
)


def generate_single_message(prompt: str, temperature: float, model_name:str="gpt-3.5-turbo-16k"):
    chat_model = ChatOpenAI(
        # model="gpt-4-32k",
        model=model_name,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE,
        temperature=temperature
    )
    return chat_model.predict(prompt)


async def agenerate_single_message(prompt: str, temperature: float, model_name:str="gpt-3.5-turbo-16k"):
    chat_model = ChatOpenAI(
        # model="gpt-4-32k",
        model=model_name,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE,
        temperature=temperature
    )
    return await chat_model.apredict(prompt)


async def agenerate_n_message(prompt: str, temperature: float, model_name:str="gpt-3.5-turbo-16k",n:int=2)->LLMResult:
    chat_model = ChatOpenAI(
        model=model_name,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE,
        temperature=temperature,
        n=n
    )
    return await chat_model.agenerate([[HumanMessage(content=prompt)]])