from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    PROCESSING_SUCESS = "PROCESSING_SUCESS"
    NO_FILES_ERROR = "Not Found Files"
    FILE_id_ERROR = "Not Found Files with this id"
    PROJECT_NOT_FOUND = "Not Found projects"
    INSERT_INTO_VECTORDB_ERROR='INSERT_INTO_VECTORDB_ERROR'
    VECTORDB_COLLECTION_RETRIEVED='VECTORDB_COLLECTION_RETRIEVED'
    VECTORDB_SEARCH_ERROR='VECTORDB_SEARCH_ERROR'
    VECTORDB_SEARCH_SUCCESS='VECTORDB_SEARCH_SUCCESS'
   
   




