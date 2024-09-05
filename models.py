import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings, AzureOpenAI
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_groq import ChatGroq
from pydantic.v1.types import SecretStr
import asyncio
from langchain_pinecone.embeddings import PineconeEmbeddings
from langchain.embeddings.base import Embeddings


# Load environment variables
load_dotenv()

# Configuration
DEFAULT_TEMPERATURE = 0.0

# Utility function to get API keys from environment variables
def get_api_key(service):
    return os.getenv(f"API_KEY_{service.upper()}") or os.getenv(f"{service.upper()}_API_KEY")


# # Ollama models
# def get_ollama_chat(model_name:str, temperature=DEFAULT_TEMPERATURE, base_url="http://localhost:11434"):
#     return Ollama(model=model_name,temperature=temperature, base_url=base_url)

# def get_ollama_embedding(model_name:str, temperature=DEFAULT_TEMPERATURE):
#     return OllamaEmbeddings(model=model_name,temperature=temperature)

# # OpenAI models
# def get_openai_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
#     api_key = api_key or get_api_key("openai")
#     return ChatOpenAI(model_name=model_name, temperature=temperature, api_key=api_key) # type: ignore

# def get_openai_instruct(model_name:str,api_key=None, temperature=DEFAULT_TEMPERATURE):
#     api_key = api_key or get_api_key("openai")
#     return OpenAI(model=model_name, temperature=temperature, api_key=api_key) # type: ignore

# def get_openai_embedding(model_name:str, api_key=None):
#     api_key = api_key or get_api_key("openai")
#     return OpenAIEmbeddings(model=model_name, api_key=api_key) # type: ignore

def get_azure_openai_chat(deployment_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureChatOpenAI(deployment_name=deployment_name, temperature=temperature, api_key=api_key, azure_endpoint=azure_endpoint) # type: ignore

def get_azure_openai_instruct(deployment_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureOpenAI(deployment_name=deployment_name, temperature=temperature, api_key=api_key, azure_endpoint=azure_endpoint) # type: ignore

def get_azure_openai_embedding(deployment_name:str, api_key=None, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureOpenAIEmbeddings(azure_deployment=deployment_name, api_key=api_key, azure_endpoint=azure_endpoint) 


def get_pinecone_embedding(model_name: str, api_key=None, environment=None, index_name=None) -> Embeddings:
    api_key = api_key or os.getenv("PINECONE_API_KEY")
    environment = environment or os.getenv("PINECONE_ENVIRONMENT")
    index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
    
    if not api_key or not environment:
        raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set in environment variables")
    
    async def create_embeddings():
        embedding_model = PineconeEmbeddings(model=model_name)
        # embedding_model.pinecone_api_key = api_key
        embedding_model.pinecone_index_name = index_name
        embedding_model.pinecone_environment = environment
        embedding_model.embedding_dimension = 1536  # Adjust this based on the specific model you're using
        return embedding_model
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(create_embeddings())

# Groq models
def get_groq_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("groq")
    return ChatGroq(model_name=model_name, temperature=temperature, api_key=api_key) # type: ignore


# def get_embedding_openai(api_key=None):
#     api_key = api_key or get_api_key("openai")
#     return OpenAIEmbeddings(api_key=api_key) #type: ignore
