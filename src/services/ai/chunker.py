class TranscriptChunker:
    def split(self, text: str, chunk_size: int = 2800) -> list:
        if not text:   
            return []
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        while text:
            if len(text) <= chunk_size:
                chunks.append(text)
                break
            split_at = text.rfind(' ', 0, chunk_size)
            if split_at == -1: 
                split_at = chunk_size
            chunks.append(text[:split_at])
            text = text[split_at:].strip()
        return chunks