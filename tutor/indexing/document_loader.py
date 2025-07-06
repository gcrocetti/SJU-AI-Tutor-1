import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pinecone import Pinecone
from tutor.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PINECONE_INDEX_NAME,
    UPSERT_BATCH_SIZE,
    PINECONE_API_KEY,
    PINECONE_NAMESPACE,
    EMBEDDING_MODEL_NAME
)

class DocumentProcessor:
    """
    A class to process and upload documents (PDF, TXT, DOCX) to a Pinecone vector database.

    This class handles:
    1. Loading document content from a file path.
    2. Splitting the document into manageable chunks.
    3. Generating embeddings for each chunk using OpenAI.
    4. Uploading the chunks and their embeddings to a specified Pinecone index.
    """

    def __init__(self):
        """
        Initializes the DocumentProcessor with necessary configurations.

        Args:
            index_name (str): The name of the Pinecone index to upload data to.
        """
        # Validate that required environment variables are set
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        if not os.environ.get("PINECONE_API_KEY"):
            raise ValueError("PINECONE_API_KEY not found in environment variables.")

        self.pinecone_index = Pinecone(api_key=PINECONE_API_KEY).Index(PINECONE_INDEX_NAME)
        # Initialize the embedding model
        # Using "text-embedding-3-small" as it has good performance and cost-effective
        self.embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

        print("DocumentProcessor initialized successfully.")

    def _load_document(self, file_path: str) -> List[Document]:
        """
        Loads a document based on its file extension.

        Args:
            file_path (str): The path to the document file.

        Returns:
            List[Document]: A list of Document objects loaded from the file.

        Raises:
            ValueError: If the file type is not supported.
        """
        print(f"Loading document from: {file_path}")
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'")

        return loader.load()

    def _chunk_document(self, documents: List[Document]) -> List[Document]:
        """
        Splits loaded documents into smaller chunks using a text splitter.

        Best Practice: RecursiveCharacterTextSplitter is robust. It tries to split on
        semantic boundaries (paragraphs, sentences, words) first.

        Args:
            documents (List[Document]): The list of documents to be chunked.

        Returns:
            List[Document]: A list of chunked Document objects.
        """
        print(f"Chunking {len(documents)} document(s)...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Document split into {len(chunks)} chunks.")
        return chunks

    def process_and_upload(self, file_path: str, topic: str):
        """
        The main method to orchestrate the loading, chunking, and uploading process.

        Args:
            file_path (str): The path to the document file.
            topic (str): The topic associated with the document. This will be added
                         to the metadata for later filtering.
        """
        try:
            # 1. Read the document and extract text
            loaded_docs = self._load_document(file_path)
            if not loaded_docs:
                print(f"Warning: No content loaded from {file_path}. Skipping.")
                return

            # 2. Chunk the document
            chunks = self._chunk_document(loaded_docs)

            # Separate out the text (for embeddings) and the metadata (topic and source) to each chunk
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            for i, metadata in enumerate(metadatas):
                metadata["topic"] = topic
                metadata["source"] = os.path.basename(file_path)
                metadata["chunk_number"] = i

            # 3. Generate the embeddings
            embeddings = self.embedding_model.embed_documents(texts)

            print(f"Preparing to upload {len(chunks)} chunks to Pinecone index '{PINECONE_INDEX_NAME}'...")

            # 4. Upload to Pinecone
            # I did not use the "from_documents" method: you cannot upload in batches and often you will exceed the limits
            for idx in range(0, len(embeddings), UPSERT_BATCH_SIZE):
                idx_end = idx + UPSERT_BATCH_SIZE
                ids_batch = [f"doc-{idx+j}" for j in range(idx_end-idx)]
                vectors_batch = list(zip(ids_batch, embeddings[idx:idx_end], metadatas[idx:idx_end]))
                self.pinecone_index.upsert(vectors=vectors_batch, namespace=PINECONE_NAMESPACE)


            print(f"Successfully processed and uploaded '{file_path}' [{len(chunks)} chunks] to Pinecone.")

        except FileNotFoundError:
            print(f"Error: The file was not found at {file_path}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# --- Usage Example ---
if __name__ == "__main__":
    # Define the list of documents (mix of text, PDFs, or DOCX)
    docs = ['C:/tmp/AI TUTOR CONTENT 2.docx', 'C:/tmp/LST1000X EDGE COURSE OUTLINE KMARKS.docx', 'C:/tmp/LST EDGE IMMERSION WEEK SCHEDULE.docx']

    # --- Main Execution Logic ---
    try:
        # Instantiate the processor for the "ciro" index
        processor = DocumentProcessor()

        # Process a text file
        for doc in docs:
            processor.process_and_upload(
                file_path=doc,
                topic="Personal Development"
            )
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"A critical error occurred during execution: {e}")