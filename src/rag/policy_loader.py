"""
Policy document loader for RAG pipeline
"""

import os
from pathlib import Path
from typing import List, Dict
import PyPDF2
from langchain_core.documents import Document


class PolicyLoader:
    """Load and prepare solar policy documents for RAG"""

    def __init__(self, policy_dir: str = "data/policies"):
        """
        Initialize policy loader.

        Args:
            policy_dir: Directory containing policy documents
        """
        self.policy_dir = policy_dir
        self.documents: List[Document] = []

    def load_policies(self, location: str = None) -> List[Document]:
        """
        Load policy documents from directory, optionally filtered by location.

        Args:
            location: Optional location to filter policies (e.g., "Karnataka", "California")
                     If provided, loads location-specific policies first, then general policies

        Returns:
            List of Document objects with policy content
        """
        self.documents = []

        if not os.path.exists(self.policy_dir):
            print(f"Policy directory not found: {self.policy_dir}")
            return self.documents

        # First, try to load location-specific policies if location is provided
        if location:
            self._load_location_specific_policies(location)

        # Then load general policies
        self._load_general_policies()

        print(f"Loaded {len(self.documents)} policy documents")
        return self.documents

    def _load_location_specific_policies(self, location: str) -> None:
        """
        Load policies specific to a location.

        Supports two directory structures:
        1. Subdirectories: data/policies/karnataka/
        2. File naming: data/policies/*karnataka*.pdf or *.txt

        Args:
            location: Location name (e.g., "Karnataka", "California")
        """
        location_lower = location.lower()

        # Check for location subdirectory
        location_dir = os.path.join(self.policy_dir, location_lower)
        if os.path.exists(location_dir):
            # Load from location-specific directory
            for file in Path(location_dir).glob("*.pdf"):
                self._load_pdf(str(file), location_tag=location)
            for file in Path(location_dir).glob("*.txt"):
                self._load_text(str(file), location_tag=location)

        # Check for location-specific files in main directory
        for file in Path(self.policy_dir).glob(f"*{location_lower}*.pdf"):
            self._load_pdf(str(file), location_tag=location)
        for file in Path(self.policy_dir).glob(f"*{location_lower}*.txt"):
            self._load_text(str(file), location_tag=location)

    def _load_general_policies(self) -> None:
        """Load general (non-location-specific) policies from main directory."""
        # Load PDF files
        for file in Path(self.policy_dir).glob("*.pdf"):
            # Skip if already loaded as location-specific
            if file not in [Path(doc.metadata.get("source", "")) for doc in self.documents]:
                self._load_pdf(str(file))

        # Load text files
        for file in Path(self.policy_dir).glob("*.txt"):
            # Skip if already loaded as location-specific
            if file not in [Path(doc.metadata.get("source", "")) for doc in self.documents]:
                self._load_text(str(file))

    def _load_pdf(self, file_path: str, location_tag: str = None) -> None:
        """Load PDF file and extract text"""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                for page_num, page in enumerate(reader.pages):
                    content += f"\n--- Page {page_num + 1} ---\n"
                    content += page.extract_text()

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "type": "pdf",
                        "filename": os.path.basename(file_path),
                        "location": location_tag,
                    },
                )
                self.documents.append(doc)
                location_info = f" ({location_tag})" if location_tag else ""
                print(f"Loaded PDF: {os.path.basename(file_path)}{location_info}")
        except Exception as e:
            print(f"Error loading PDF {file_path}: {str(e)}")

    def _load_text(self, file_path: str, location_tag: str = None) -> None:
        """Load text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path,
                    "type": "text",
                    "filename": os.path.basename(file_path),
                    "location": location_tag,
                },
            )
            self.documents.append(doc)
            location_info = f" ({location_tag})" if location_tag else ""
            print(f"Loaded text: {os.path.basename(file_path)}{location_info}")
        except Exception as e:
            print(f"Error loading text file {file_path}: {str(e)}")

    def get_documents(self) -> List[Document]:
        """Get all loaded documents"""
        return self.documents
