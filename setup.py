"""Setup script for the RAG Student Support System."""
from setuptools import setup, find_packages

setup(
    name="rag-student-support",
    version="1.0.0",
    description="Multilingual RAG system for student support via WhatsApp",
    author="Your Organization",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-dotenv>=1.0.0",
        "azure-search-documents>=11.4.0",
        "semantic-kernel>=0.9.0",
        "openai>=1.3.0",
        "azure-identity>=1.15.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "langdetect>=1.0.9",
        "python-multipart>=0.0.6",
        "httpx>=0.25.2",
        "tenacity>=8.2.3",
    ],
    python_requires=">=3.10",
)
