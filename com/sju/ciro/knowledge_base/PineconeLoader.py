"""
Author: Giancarlo Crocetti, Ryan Handley, Benjamin Hannim
Application: Conversational Intelligence for Retention Optimization (CIRO)
St John's University - 2025 - All Rights Reserved
License: This code is licensed under the Apache License, Version 2.0 (the "License").
"""

import os
import json
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from PDFExtractor import PDFExtractor

#<TO DO: add messages to a logging framework>
class PineconeUploader:
    index = None

    def __init__(self, pinecone_index_name='ciro', chunk_size=300, chunk_overlap=100, batch_size=100):
        """
        Initialize Pinecone and OpenAI clients. We expect these API kes to be available as environment variables.
        :param pinecone_index_name: Pinecone index name (defaults to the current index name 'ciro')
        """

        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # Chunking parameters
        self.chunk_size = chunk_size  # Max number of words per chunk
        self.chunk_overlap = chunk_overlap  # Overlapping words between chunks
        self.batch_size = batch_size # Batch size to reduce API calls when uploading chunks

        # OVERRIDING THE API_KEY WITH MY TESTING ONE
        self.pinecone_api_key = 'pcsk_4bLxw7_UgJTr4hZhDjozufcqjEZvPnQWGkHyjARYU7T9uVNy18fArhvpXcVVWaphDGpQki'


        if not self.pinecone_api_key or not self.openai_api_key:
            raise ValueError('Please set PINECONE_API_KEY and OPENAI_API_KEY environment variables.')

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)

        # Initialize Pinecone
        pc_db = Pinecone(api_key=self.pinecone_api_key)

        # Retrieve indexes available
        indexes = [index['name'] for index in pc_db.list_indexes()]

        # Connect to Pinecone index if avaialble
        if pinecone_index_name in indexes:
            self.index = pc_db.Index(pinecone_index_name)

    def chunk_text(self, text):
        """
        Splits text into overlapping chunks for better search accuracy.
        :param text: text to chunk
        :return: list of chunks
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i: i + self.chunk_size])
            chunks.append(chunk)

        return chunks

    def get_openai_embedding(self, text, emb_model='text-embedding-3-small'):
        """
        Generates an embedding using the recommended OpenAI's text-embedding-3-small model.
        :param text: Text to be embedded.
        :param emb_model: OpenAI embedding model to be used.
        :return: Embedded vector.
        """
        response = self.openai_client.embeddings.create(input=text, model=emb_model)
        return response.data[0].embedding

    def upload_json_to_pinecone(self, json_data):
        """
        Ingest the JSON structured data to Pinecone after generating embeddings.
        :param json_data: JSON structured data.
        """
        document_metadata = json_data["document_metadata"]
        sections = json_data["sections"]

        print(f"Uploading {len(sections)} sections to Pinecone...")

        batch = []  # Store batch for upsert

        # Process each section in the JSON
        for section in sections:
            content = section["content"]
            section_id = f"{document_metadata['source']}_page{section['page']}"

            # Split content into smaller chunks
            text_chunks = self.chunk_text(content)

            for i, chunk in enumerate(text_chunks):
                chunk_id = f"{section_id}_chunk{i+1}"

                # Generate embedding for the chunk
                embedding = self.get_openai_embedding(chunk)

                # Store metadata
                metadata = {
                    "source": document_metadata["source"],
                    "page": section["page"],
                    "summary": section["summary"],
                    "keywords": ", ".join(section["metadata"]["keywords"]),
                    "categories": ", ".join(section["metadata"]["categories"]),
                    "chunk_id": i + 1
                }

                # Add to batch
                batch.append((chunk_id, embedding, metadata))

                # Process batch when it reaches the batch size
                if len(batch) >= self.batch_size:
                    self.index.upsert(batch)
                    batch = []  # Reset batch

        # Upload remaining items if any
        if batch:
            self.index.upsert(batch)

        print("Upload completed successfully!")


# Unit Testing
if __name__ == "__main__":

    pdf_extractor = PDFExtractor()
    pdf_path = "C:/tmp/udlg2.2-text-a11y.pdf"  # Replace with the actual PDF path

    json_data = pdf_extractor.process_pdf(pdf_path)

    # Initialize PineconeUploader
    uploader = PineconeUploader(pinecone_index_name="test")

    # Upload JSON data to Pinecone
    uploader.upload_json_to_pinecone(json_data)
