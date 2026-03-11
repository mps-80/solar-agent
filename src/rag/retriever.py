"""
RAG Retriever for policy documents using LangChain
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from src.utils.config import Config


class PolicyRetriever:
    """Retrieve relevant policies using RAG"""

    def __init__(self, documents: List[Document] = None, model_name: str = None):
        """
        Initialize policy retriever.

        Args:
            documents: List of policy documents to index
            model_name: Groq model name to use for QA
        """
        self.documents = documents or []
        self.model_name = model_name or Config.GROQ_MODEL
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None

        if self.documents:
            self._setup_vector_store()

    def _setup_vector_store(self) -> None:
        """Create and index vector store from documents"""
        # Split documents into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
        )

        splits = text_splitter.split_documents(self.documents)
        print(f"Created {len(splits)} document chunks")

        # Create embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL
        )

        # Create vector store
        self.vector_store = FAISS.from_documents(
            splits, 
            embeddings
        )
        print("Vector store created successfully")

        # Setup retriever
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": Config.TOP_K_RESULTS}
        )

    def query(self, query: str) -> str:
        """
        Query the policy documents.

        Args:
            query: Question about solar policies

        Returns:
            Answer from RAG pipeline
        """
        if not self.retriever:
            return "Vector store not initialized. Load documents first."

        try:
            # Retrieve relevant documents
            docs = self.retriever.invoke(query)
            
            if not docs:
                return "No relevant policies found for your query."

            # Format context
            context = "\n\n".join([doc.page_content for doc in docs])
            
            return context
        except Exception as e:
            return f"Error querying policies: {str(e)}"

    def get_qa_chain(self):
        """
        Get retrieval chain for Q&A.

        Returns:
            Retrieval chain
        """
        if not self.retriever:
            raise ValueError("Vector store not initialized")

        if not self.qa_chain:
            llm = ChatGroq(
                model=self.model_name,
                temperature=Config.LLM_TEMPERATURE,
            )
            
            # Create prompt template
            prompt = PromptTemplate(
                template="""You are a helpful assistant for solar policy analysis. 
Answer the question based on the provided policy documents.

Policy context:
{context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            )
            
            # Build chain using LCEL
            self.qa_chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

        return self.qa_chain

    def answer_question(self, question: str) -> dict:
        """
        Answer a question about policies with sources.

        Args:
            question: Question about solar policies

        Returns:
            Dictionary with answer and source documents
        """
        try:
            if not self.retriever:
                return {
                    "answer": "Vector store not initialized",
                    "sources": []
                }
            
            qa_chain = self.get_qa_chain()
            
            # Get relevant documents using invoke
            docs = self.retriever.invoke(question)
            
            # Run the chain
            answer = qa_chain.invoke(question)
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "file": doc.metadata.get("filename", "Unknown"),
                        "content": doc.page_content[:200] + "..."
                    }
                    for doc in docs
                ]
            }
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }

    def update_documents(self, new_documents: List[Document]) -> None:
        """
        Update vector store with new documents.

        Args:
            new_documents: New policy documents to add
        """
        self.documents.extend(new_documents)
        self._setup_vector_store()
