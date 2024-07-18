from enum import Enum

class LLMEnum(Enum):
    OPENAI='OPENAI'
    COHERE='COHERE'
    

class OpenAIEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"

class CohereEnums(Enum):
    SYSTEM="SYSTEM"
    USER="USER"
    ASSISTANT="CHATBOT"
    DOCUMENT="search_document"
    QUERY="search_query"

class DocumentTypeEnum(Enum):
    DOCUMENT="document" 
    QUERY="query"
