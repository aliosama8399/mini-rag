from ..LLMInterface import LLMInterface
from ..LLMEnum import CohereEnums,DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMInterface):
     def __init__(self, api_key:str, default_input_max_characters:int=1000,default_generation_max_output:int=1000,
                 default_generation_temperature:float=0.1):
                      
        self.api_key=api_key
        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output=default_generation_max_output
        self.default_generation_temperature=default_generation_temperature
        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None

        self.client= cohere.Client(api_key=self.api_key)
        self.logger= logging.getLogger(__name__)
        
        self.enums=CohereEnums
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
                    self.logger.error("Cohere client wasn't set")

        if not self.generation_model_id:
                self.logger.error("Cohere generation_model_id  wasn't set")
        

        max_output_tokens =max_output_tokens if max_output_tokens else self.default_generation_max_output
        temprature = temprature if temprature else self.default_generation_temperature
 
        response= self.client.chat(
               model= self.generation_model_id,
               chat_history=chat_history,
               message=self.process_text(prompt),
               temperature=temprature,
               max_tokens=max_output_tokens
               )


        if not response or not response.text:
                self.logger.error('Error while generate text with COHERE')
                return None
         
        return response.text          
     
     def embedding_text(self, text:str, document_type:str=None):
        
        if not self.client:
            self.logger.error("cohere client wasn't set")

        if not self.embedding_model_id:
            self.logger.error("cohere embedding_model_id wasn't set")

        input_type= CohereEnums.DOCUMENT.value
        if document_type==DocumentTypeEnum.QUERY.value:
             input_type=CohereEnums.QUERY.value




        response =self.client.embed(
            model= self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type=input_type,
            embedding_types=['float'],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error('error while embedding text with cohere')
            return None
        
        return response.embeddings.float[0]
      
     def construct_prompt(self, prompt:str,role:str):
        return{
            "role":role,
            "text": self.process_text(prompt)
    }
    