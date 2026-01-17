"""RAG service combining Azure Search with Semantic Kernel."""
import logging
import uuid
from typing import List, Dict, Optional

from app.config import settings
from app.services.language_detector import LanguageDetector
from app.services.conversation_memory import get_conversation_memory

logger = logging.getLogger(__name__)

# Conditional imports
# Note: Semantic Kernel is only needed in Azure mode
# In local mode, this import may fail due to dependency conflicts, which is OK
SEMANTIC_KERNEL_AVAILABLE = False
try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError as e:
    # Only warn if we're in Azure mode (where it's actually needed)
    # In local mode, this is expected and harmless
    if not settings.is_local_mode():
        logger.warning(
            f"Semantic Kernel not available (import error: {e}), "
            "will use direct OpenAI API fallback. This may indicate a dependency conflict."
        )
    else:
        logger.debug("Semantic Kernel not available (not needed in local mode)")

from app.services.vector_store import VectorStore
from app.services.embeddings import EmbeddingService

if not settings.is_local_mode():
    from app.services.azure_search import AzureSearchService
else:
    from app.services.local_llm import LocalLLMService


class RAGService:
    """Main RAG service orchestrating search and generation."""
    
    def __init__(self):
        """Initialize RAG service with Semantic Kernel and Azure Search."""
        self.is_local = settings.is_local_mode()
        
        if self.is_local:
            logger.info("Initializing RAG Service in LOCAL mode (using vector database)")
            # Use vector database for local RAG
            self.vector_store = VectorStore()
            self.embedding_service = EmbeddingService()
            
            # Initialize local LLM service
            try:
                self.local_llm = LocalLLMService(
                    provider=settings.local_llm_provider,
                    model_name=settings.local_llm_model,
                    base_url=settings.local_llm_base_url,
                    use_gpu=settings.local_llm_use_gpu
                )
                logger.info(f"Local LLM service initialized: {settings.local_llm_provider} ({settings.local_llm_model})")
            except Exception as e:
                logger.error(f"Failed to initialize local LLM service: {e}")
                logger.warning("Falling back to mock OpenAI service")
                from app.services.mock_openai import MockOpenAIService
                self.local_llm = MockOpenAIService()
                logger.info("Using mock OpenAI service as fallback")
            
            self.kernel = None
            self.rag_function = None
            self.search_service = None  # Not used in local mode
        else:
            logger.info("Initializing RAG Service in AZURE mode (using Azure services)")
            # Initialize Semantic Kernel
            if SEMANTIC_KERNEL_AVAILABLE:
                self.kernel = sk.Kernel()
                
                # Add Azure OpenAI chat completion
                chat_service = AzureChatCompletion(
                    service_id="default",
                    deployment_name=settings.azure_openai_deployment_name,
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                self.kernel.add_service(chat_service)
            else:
                self.kernel = None
                logger.warning("Semantic Kernel not available, will use direct OpenAI API")
            
            # Initialize Azure Search
            self.search_service = AzureSearchService()
            self.mock_openai = None
        
        # Initialize language detector
        self.language_detector = LanguageDetector()
        
        # Initialize conversation memory
        if settings.enable_conversation_memory:
            self.conversation_memory = get_conversation_memory()
        else:
            self.conversation_memory = None
        
        # Register prompt function (only in Azure mode)
        if not self.is_local:
            self._register_prompt_function()
        
        logger.info("RAG Service initialized")
    
    def _register_prompt_function(self):
        """Register the RAG prompt function with guardrails."""
        prompt_template = """
You are a helpful student support assistant. Answer the student's question based ONLY on the provided context from the knowledge base.

IMPORTANT RULES:
1. Only use information from the provided context below
2. If the context doesn't contain enough information, say "I don't have enough information to answer that question. Please contact support for assistance."
3. Do not make up or infer information not explicitly stated in the context
4. Keep your response concise and clear (under {{$max_length}} characters)
5. Respond in the same language as the student's question
6. If asked about something not in the context, politely redirect to support

Context from knowledge base:
{{$context}}

Student's question: {{$query}}

Provide a helpful, accurate response based only on the context above:
"""
        
        # Create the prompt function
        # Try different Semantic Kernel API versions for compatibility
        try:
            # Try newer API (1.30.0+)
            self.rag_function = self.kernel.create_function_from_prompt(
                function_name="answer_student_query",
                plugin_name="StudentSupport",
                prompt=prompt_template,
                description="RAG prompt with guardrails for answering student queries",
                execution_settings=sk.ExecutionSettings(
                    max_tokens=settings.max_response_length,
                    temperature=0.3
                )
            )
        except (AttributeError, TypeError):
            try:
                # Try alternative API
                from semantic_kernel.prompt_template import PromptTemplateConfig
                prompt_config = PromptTemplateConfig(
                    template=prompt_template,
                    description="RAG prompt with guardrails",
                    execution_settings={
                        "default": {
                            "max_tokens": settings.max_response_length,
                            "temperature": 0.3,
                        }
                    }
                )
                self.rag_function = self.kernel.add_function(
                    function_name="answer_student_query",
                    plugin_name="StudentSupport",
                    prompt_template_config=prompt_config
                )
            except Exception as e:
                logger.warning(f"Could not register prompt function with standard API: {e}")
                # Fallback: store template for manual use
                self.rag_function = None
                self.prompt_template = prompt_template
    
    async def process_query(
        self,
        query: str,
        language: Optional[str] = None,
        student_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Process a student query and return a response.
        
        Args:
            query: Student's question
            language: Language code or None for auto-detection
            student_id: Optional student identifier
            conversation_id: Optional conversation ID for follow-up questions
            
        Returns:
            Dictionary with response, language, confidence, sources, and conversation_id
        """
        try:
            # Handle conversation memory
            if self.conversation_memory:
                if not conversation_id:
                    # Create new conversation
                    conversation_id = self.conversation_memory.create_conversation(student_id)
                
                # Get conversation history
                conversation_context = self.conversation_memory.get_context_string(
                    conversation_id,
                    max_messages=settings.max_conversation_history
                )
                
                # Add user message to history
                self.conversation_memory.add_message(
                    conversation_id,
                    'user',
                    query
                )
            else:
                conversation_context = ""
                if not conversation_id:
                    conversation_id = str(uuid.uuid4())
            # Detect language if not provided
            if not language or language == "auto":
                language = self.language_detector.detect_language(query)
            
            # Validate language
            if not self.language_detector.is_supported(language):
                language = "en"
                logger.warning(f"Unsupported language, defaulting to English")
            
            # Retrieve relevant documents
            if self.is_local:
                # Use vector database search
                search_results = self.vector_store.search(
                    query=query,
                    n_results=5
                )
                # Convert to expected format
                search_results = [
                    {
                        'content': r.get('content', ''),
                        'title': r.get('metadata', {}).get('title', ''),
                        'source': r.get('metadata', {}).get('source', 'ICL Student Handbook'),
                        'score': r.get('score', 0.0),
                        'metadata': r.get('metadata', {})
                    }
                    for r in search_results
                ]
            else:
                # Use Azure Search
                search_results = self.search_service.search(
                    query=query,
                    language=language,
                    top=5,
                    min_score=0.5
                )
            
            if not search_results:
                logger.warning("No relevant documents found in knowledge base")
                response_dict = {
                    "response": "I don't have enough information to answer that question. Please contact our support team for assistance.",
                    "language": language,
                    "confidence": 0.0,
                    "sources": [],
                    "query_id": str(uuid.uuid4()),
                    "conversation_id": conversation_id
                }
                # Store in memory even if no results
                if self.conversation_memory and conversation_id:
                    self.conversation_memory.add_message(
                        conversation_id,
                        'assistant',
                        response_dict["response"],
                        metadata={'confidence': 0.0, 'sources': []}
                    )
                return response_dict
            
            # Build context from search results
            context = self._build_context(search_results)
            
            # Add conversation context if available
            if conversation_context:
                context = f"{conversation_context}\n\n{context}"
            
            # Calculate confidence based on search scores
            confidence = self._calculate_confidence(search_results)
            
            # Generate response using Semantic Kernel or mock service
            if self.is_local:
                response = await self._generate_response_local(query, context, language, conversation_context)
            else:
                response = await self._generate_response(query, context, language, conversation_context)
            
            # Apply guardrails
            response = self._apply_guardrails(response, context, query)
            
            # Extract source IDs
            sources = [doc.get('source', '') for doc in search_results if doc.get('source')]
            
            # Store assistant response in conversation memory
            if self.conversation_memory and conversation_id:
                self.conversation_memory.add_message(
                    conversation_id,
                    'assistant',
                    response,
                    metadata={
                        'confidence': confidence,
                        'sources': sources
                    }
                )
            
            return {
                "response": response,
                "language": language,
                "confidence": confidence,
                "sources": sources,
                "query_id": str(uuid.uuid4()),
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            error_conv_id = conversation_id if 'conversation_id' in locals() else None
            return {
                "response": "I apologize, but I encountered an error processing your question. Please try again or contact support.",
                "language": language or "en",
                "confidence": 0.0,
                "sources": [],
                "query_id": str(uuid.uuid4()),
                "conversation_id": error_conv_id
            }
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Build context string from search results."""
        context_parts = []
        for i, doc in enumerate(search_results, 1):
            title = doc.get('title', f'Document {i}')
            content = doc.get('content', '')
            context_parts.append(f"[{title}]\n{content}\n")
        return "\n---\n".join(context_parts)
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """Calculate confidence score from search results."""
        if not search_results:
            return 0.0
        
        # Use the highest score as base confidence
        max_score = max(doc.get('score', 0.0) for doc in search_results)
        
        # Normalize based on mode
        if self.is_local:
            # Local mode: ChromaDB returns scores in 0-1 range (1.0 - distance)
            # Distance is cosine distance, so score = 1.0 - distance
            # For good matches, distance is low (0.1-0.3), so score is high (0.7-0.9)
            # For poor matches, distance is high (0.7-1.0), so score is low (0.0-0.3)
            normalized = max_score  # Already in 0-1 range, use directly
            
            # Apply sigmoid-like transformation to better distinguish good vs poor matches
            # This makes scores above 0.7 more confident, scores below 0.5 less confident
            if normalized >= 0.7:
                # High similarity: boost confidence
                normalized = 0.7 + (normalized - 0.7) * 0.5  # Scale 0.7-1.0 to 0.7-0.85
            elif normalized >= 0.5:
                # Medium similarity: moderate confidence
                normalized = 0.5 + (normalized - 0.5) * 0.4  # Scale 0.5-0.7 to 0.5-0.58
            else:
                # Low similarity: reduce confidence
                normalized = normalized * 0.7  # Scale 0.0-0.5 to 0.0-0.35
        else:
            # Azure mode: Azure Search scores can vary (often 0-10 range)
            # Normalize to 0-1 range
            normalized = min(max_score / 10.0, 1.0)
        
        # Boost confidence if multiple relevant results (indicates query is well-covered)
        if len(search_results) >= 3:
            # Small boost for multiple results
            normalized = min(normalized * 1.15, 1.0)
        elif len(search_results) >= 2:
            # Smaller boost for 2 results
            normalized = min(normalized * 1.08, 1.0)
        
        # Ensure confidence is in valid range
        normalized = max(0.0, min(1.0, normalized))
        
        return round(normalized, 2)
    
    async def _generate_response(
        self,
        query: str,
        context: str,
        language: str,
        conversation_context: str = ""
    ) -> str:
        """Generate response using Semantic Kernel."""
        try:
            if self.rag_function is None:
                # Fallback: use OpenAI directly if Semantic Kernel function not available
                return await self._generate_response_fallback(query, context, language)
            
            # Create kernel arguments
            try:
                arguments = sk.KernelArguments(
                    query=query,
                    context=context,
                    max_length=str(settings.max_response_length)
                )
            except (AttributeError, TypeError):
                # Alternative argument format
                arguments = {
                    "query": query,
                    "context": context,
                    "max_length": str(settings.max_response_length)
                }
            
            # Invoke the function
            result = await self.kernel.invoke(
                function=self.rag_function,
                arguments=arguments
            )
            
            # Extract response text
            if hasattr(result, 'value'):
                response = str(result.value).strip()
            else:
                response = str(result).strip()
            
            # Ensure response length limit
            if len(response) > settings.max_response_length:
                response = response[:settings.max_response_length] + "..."
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response with Semantic Kernel: {e}")
            # Fallback to direct OpenAI call
            return await self._generate_response_fallback(query, context, language)
    
    async def _generate_response_local(
        self,
        query: str,
        context: str,
        language: str,
        conversation_context: str = ""
    ) -> str:
        """Generate response using local LLM service."""
        try:
            # Build prompt with conversation context if available
            context_section = f"Context from knowledge base:\n{context}"
            if conversation_context:
                context_section = f"{conversation_context}\n\n{context_section}"
            
            system_prompt = f"""You are a helpful student support assistant. Answer the student's question based ONLY on the provided context.

IMPORTANT RULES:
1. Only use information from the provided context below
2. If the context doesn't contain enough information, say "I don't have enough information to answer that question. Please contact support for assistance."
3. Do not make up or infer information not explicitly stated in the context
4. Keep your response concise and clear (under {settings.max_response_length} characters)
5. Respond in the same language as the student's question
6. If this is a follow-up question, use the conversation history to understand context"""
            
            user_prompt = f"""{context_section}

Student's question: {query}

Provide a helpful, accurate response based only on the context above:"""
            
            # Use local LLM service
            if hasattr(self.local_llm, 'generate_response') and hasattr(self.local_llm, 'provider'):
                # LocalLLMService (Ollama or Transformers)
                response = await self.local_llm.generate_response(
                    prompt=user_prompt,
                    max_tokens=settings.max_response_length,
                    temperature=0.3,
                    system_prompt=system_prompt
                )
            else:
                # Fallback to mock OpenAI (backward compatibility)
                print(f"Fallback to mock OpenAI: {system_prompt}")
                print(f"User prompt: {user_prompt}")
                
                full_prompt = f"""{system_prompt}

{user_prompt}"""
                response = await self.local_llm.generate_response(
                    prompt=full_prompt,
                    max_tokens=settings.max_response_length,
                    temperature=0.3
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in local response generation: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your question. Please try again or contact support."
    
    async def _generate_response_fallback(
        self,
        query: str,
        context: str,
        language: str
    ) -> str:
        """Fallback response generation using OpenAI directly."""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            
            prompt = f"""You are a helpful student support assistant. Answer the student's question based ONLY on the provided context.

IMPORTANT RULES:
1. Only use information from the provided context below
2. If the context doesn't contain enough information, say "I don't have enough information to answer that question. Please contact support for assistance."
3. Do not make up or infer information not explicitly stated in the context
4. Keep your response concise and clear (under {settings.max_response_length} characters)
5. Respond in the same language as the student's question

Context from knowledge base:
{context}

Student's question: {query}

Provide a helpful, accurate response based only on the context above:"""
            
            response = client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful student support assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.max_response_length,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in fallback response generation: {e}")
            return "I apologize, but I encountered an error processing your question. Please try again or contact support."
    
    def _apply_guardrails(
        self,
        response: str,
        context: str,
        original_query: str
    ) -> str:
        """Apply guardrails to prevent hallucination."""
        # Check if response is too generic
        generic_phrases = [
            "I don't know",
            "I'm not sure",
            "I cannot help",
            "I don't have information"
        ]
        
        # If response seems to ignore context, add disclaimer
        if any(phrase.lower() in response.lower() for phrase in generic_phrases):
            if context and len(context) > 50:
                # Context exists but model said it doesn't know
                # This might indicate hallucination prevention is working
                pass
        
        # Ensure response doesn't exceed length
        if len(response) > settings.max_response_length:
            response = response[:settings.max_response_length] + "..."
        
        # Check for empty or very short responses
        if len(response.strip()) < 10:
            return "I don't have enough information to answer that question. Please contact our support team for assistance."
        
        return response
