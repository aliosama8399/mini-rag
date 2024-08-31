from .VectorDBEnum import VectorDBEnum
from .providers import QdrantDBProvider
from controllers.BaseController import BaseController
class VectorDBProviderFactory:
    def __init__(self,config: dict) :

        self.config=config
        self.base_controller= BaseController()


    def create(self, providers: str):
        if providers == VectorDBEnum.QDRANT.value:
                db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)

                return QdrantDBProvider(
                    db_path = db_path,
                    distance_method = self.config.VECTOR_DB_DISTANCE_METHOD,
            )

        
        return None      