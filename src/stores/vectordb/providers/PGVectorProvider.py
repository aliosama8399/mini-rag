from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import DistanceMethodEnums, PgvectorTableEnum, PgvectorDistanceMethodEnum, PgvectorIndexTypeEnum
from typing import List
import logging
from models.db_schemes.minirag.scehmes import RetrievedDocument
from sqlalchemy.sql import text as sql_text
from sqlalchemy.exc import IntegrityError
import json

class PGVectorDBProvider(VectorDBInterface):
    def __init__(self, db_client: object, default_vector_size: int = 786, distance_method: str = None, index_threshold: int = 100):
        self.client = db_client
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        # Set distance method
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = PgvectorDistanceMethodEnum.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = PgvectorDistanceMethodEnum.DOT.value
        else:
            self.distance_method = distance_method

        self.pgvector_table_prefix = PgvectorTableEnum._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"

    async def connect(self):
        """Connect and ensure vector extension exists"""
        async with self.client() as session:
            try:
                async with session.begin():
                    # Try to create the extension
                    await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
                    await session.commit()
            except IntegrityError as e:
                # Handle the case where extension already exists
                if "already exists" in str(e).lower() or "duplicate key" in str(e).lower():
                    self.logger.info("Vector extension already exists, continuing...")
                    # Rollback the failed transaction
                    await session.rollback()
                else:
                    self.logger.error(f"Failed to create vector extension: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error during connection: {e}")
                raise

    async def disconnect(self):
        """Disconnect from the database"""
        pass

    async def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection (table) exists"""
        async with self.client() as session:
            async with session.begin():
                list_tbl = sql_text("SELECT 1 FROM pg_tables WHERE tablename = :collection_name")
                results = await session.execute(list_tbl, {"collection_name": collection_name})
                record = results.scalar_one_or_none()
        return bool(record)
    
    async def list_all_collections(self) -> List[str]:
        """List all collections with the specified prefix"""
        records = []
        async with self.client() as session:
            async with session.begin():
                list_tbl = sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(list_tbl, {"prefix": f"{self.pgvector_table_prefix}%"})
                records = results.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a collection"""
        async with self.client() as session:
            async with session.begin():
                table_info_sql = sql_text(
                    """
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                    FROM pg_tables WHERE tablename = :collection_name
                    """
                )
                count_sql = sql_text(f"SELECT COUNT(*) FROM {collection_name}")
                
                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                record_count = await session.execute(count_sql)

                table_data = table_info.fetchone()
                if not table_data:
                    return None
                
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4]
                    },
                    "record_count": record_count.scalar_one(),
                }
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection (drop table)"""
        async with self.client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection {collection_name}")
                drop_sql = sql_text(f"DROP TABLE IF EXISTS {collection_name}")
                await session.execute(drop_sql)
                await session.commit()
        return True
    
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False) -> bool:
        """Create a new collection (table)"""
        if do_reset:
            await self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collection {collection_name}")
            async with self.client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f"""CREATE TABLE {collection_name} (
                            {PgvectorTableEnum.ID.value} bigserial PRIMARY KEY,
                            {PgvectorTableEnum.TEXT.value} text,
                            {PgvectorTableEnum.VECTOR.value} vector({embedding_size}),
                            {PgvectorTableEnum.METADATA.value} JSONB DEFAULT '{{}}',
                            {PgvectorTableEnum.CHUNK_ID.value} integer,
                            FOREIGN KEY ({PgvectorTableEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id)
                        )"""
                    )
                    await session.execute(create_sql)
                    await session.commit()
            return True
        return False
    
    async def is_index_existed(self, collection_name: str) -> bool:
        """Check if vector index exists for collection"""
        index_name = self.default_index_name(collection_name)
        async with self.client() as session:
            async with session.begin():
                index_sql = sql_text(
                    "SELECT 1 FROM pg_indexes WHERE tablename = :collection_name AND indexname = :index_name"
                )
                results = await session.execute(index_sql, {"collection_name": collection_name, "index_name": index_name})
                return bool(results.scalar_one_or_none())
    
    async def create_vector_index(self, collection_name: str, index_type: str = PgvectorIndexTypeEnum.HNSW.value) -> bool:
        """Create vector index if conditions are met"""
        is_index_existed = await self.is_index_existed(collection_name=collection_name)
        if is_index_existed:  # Fixed: should return False if index already exists
            return False
            
        async with self.client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                count_result = await session.execute(count_sql)
                count = count_result.scalar_one_or_none()

                if count < self.index_threshold:    
                    return False
                
                self.logger.info(f"Creating index for collection {collection_name}")
                index_name = self.default_index_name(collection_name)
                create_index_sql = sql_text(
                    f"""CREATE INDEX {index_name} ON {collection_name} 
                        USING {index_type} ({PgvectorTableEnum.VECTOR.value} {self.distance_method})"""
                )
                await session.execute(create_index_sql)
                await session.commit()  # Added commit
                self.logger.info(f"Index {index_name} created for collection {collection_name}")
                return True

    async def reset_vector_index(self, collection_name: str, index_type: str = PgvectorIndexTypeEnum.HNSW.value) -> bool:
        """Drop and recreate vector index"""
        index_name = self.default_index_name(collection_name)
        async with self.client() as session:
            async with session.begin():
                drop_index_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
                await session.execute(drop_index_sql)
                await session.commit()

        return await self.create_vector_index(collection_name=collection_name, index_type=index_type)

    async def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: dict = None, record_id: str = None) -> bool:
        """Insert a single document"""
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
            
        if not record_id:
            self.logger.error(f"Cannot insert without chunk id")
            return False

        async with self.client() as session:
            async with session.begin():
                insert_sql = sql_text(
                    f"""INSERT INTO {collection_name} (
                        {PgvectorTableEnum.TEXT.value},
                        {PgvectorTableEnum.VECTOR.value},
                        {PgvectorTableEnum.METADATA.value},
                        {PgvectorTableEnum.CHUNK_ID.value}
                    ) VALUES (:text, :vector, :metadata, :chunk_id)"""
                )
                metajson = json.dumps(metadata, ensure_ascii=False) if metadata is not None else "{}"

                await session.execute(insert_sql, {
                    "text": text,
                    "vector": "[" + ",".join([str(v) for v in vector]) + "]",
                    "metadata": metajson,
                    "chunk_id": record_id
                })
                await session.commit()
                
        # Try to create index after insertion
        await self.create_vector_index(collection_name=collection_name)
        return True
    
    async def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50) -> bool:
        """Insert multiple documents in batches"""
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Vectors and record_ids length mismatch")
            return False
            
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)

        async with self.client() as session:
            async with session.begin():
                for i in range(0, len(vectors), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_vectors = vectors[i:i + batch_size]
                    batch_metadata = metadata[i:i + batch_size]
                    batch_record_ids = record_ids[i:i + batch_size]
                    
                    values = []
                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                        metajson = json.dumps(_metadata, ensure_ascii=False) if _metadata is not None else "{}"
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join([str(v) for v in _vector]) + "]",
                            "metadata": metajson,
                            "chunk_id": _record_id
                        })

                    batch_insert_sql = sql_text( 
                        f"""INSERT INTO {collection_name} (
                            {PgvectorTableEnum.TEXT.value},
                            {PgvectorTableEnum.VECTOR.value},
                            {PgvectorTableEnum.METADATA.value},
                            {PgvectorTableEnum.CHUNK_ID.value}
                        ) VALUES (:text, :vector, :metadata, :chunk_id)"""
                    )
                    await session.execute(batch_insert_sql, values)
                await session.commit()
                
        # Try to create index after batch insertion
        await self.create_vector_index(collection_name=collection_name)
        return True
    
    async def search_by_vector(self, collection_name: str, vector: list, limit: int) -> List[RetrievedDocument]:
        """Search for similar vectors"""
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist")
            return []
            
        vector_str = "[" + ",".join([str(v) for v in vector]) + "]"
        async with self.client() as session:
            async with session.begin():
                search_sql = sql_text(
                    f"""SELECT 
                        {PgvectorTableEnum.TEXT.value} as text, 
                        1-({PgvectorTableEnum.VECTOR.value} <=> :vector) as score
                    FROM {collection_name} 
                    ORDER BY {PgvectorTableEnum.VECTOR.value} <=> :vector
                    LIMIT :limit"""
                )
                results = await session.execute(search_sql, {"vector": vector_str, "limit": limit})
                records = results.fetchall()

        return [
            RetrievedDocument(
                text=record.text,
                score=record.score
            )
            for record in records
        ]