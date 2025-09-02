from dataclasses import dataclass


@dataclass
class ChunkStoreEmbeding:
    file_path: str
    chunks: list
