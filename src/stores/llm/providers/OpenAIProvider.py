from ..LLMInterface import LLMInterface
from openai import OpenAI
import logging
from ..LLMEnum import OpenAIEnums
class OpenAIProvider(LLMInterface):

    def __init__(self, api_key:str, default_input_max_characters:int=1000,default_generation_max_output_tokens:int=1000,
                 default_generation_temperature:float=0.1, api_url:str = None):
                     
        self.api_key=api_key
        self.api_url=api_url
        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output_tokens=default_generation_max_output_tokens
        self.default_generation_temperature=default_generation_temperature
        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None

        self.client= OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )

        self.logger= logging.getLogger(__name__)
        
    def set_generation_model(self, model_id:str):
            self.generation_model_id=model_id

    def set_embedding_model(self, model_id:str,embedding_size:int):
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size

    def process_text(self, text:str):
          return text[:self.default_input_max_characters].strip()
        

    def generate_text(self,prompt:str,chat_history:list=[], max_output_tokens:int=None,
                      temprature:float=None):
         
         if not self.client:
                self.logger.error("openai client wasn't set")

         if not self.generation_model_id:
                self.logger.error("openai generation_model_id  wasn't set")
        
         max_output_tokens =max_output_tokens if max_output_tokens else self.default_generation_max_output
         temprature = temprature if temprature else self.default_generation_temprature

         chat_history.append(
               self.construct_prompt(prompt=prompt,role= OpenAIEnums.USER.value )
         )

         response= self.client.chat.completions.create(
               model= self.generation_model_id,
               messages=chat_history,
               max_tokens= max_output_tokens,
               temperature=temprature

         )

         if not response or not response.choices or len(response.choices)==0 or not response.choices[0]:
                self.logger.error('Error while generate text with Openai')
                return None
         
         return response.choices[0].message['content']




    def embedding_text(self, text:str, document_type:str=None):
         
         if not self.client:
                self.logger.error("openai client wasn't set")

         if not self.embedding_model_id:
                self.logger.error("openai embedding_model_id wasn't set")

        
         response =self.client.embeddings.create(
              model= self.embedding_model_id,
              input=text,
         )

         if not response or not response.data or len(response.data)==0 or not response.data[0].embedding:
                self.logger.error('error while embedding text with openai')
                return None
         
         return response.data[0].embedding
                
     
    def construct_prompt(self, prompt:str,role:str):
          return{
                "role":role,
                "conent": self.process_text(prompt)
          }
          
