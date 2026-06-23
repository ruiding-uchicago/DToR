"""OpenAI integration for the research assistant using the golden example pattern."""

import threading
import logging
from typing import Any, List, Optional
from openai import OpenAI

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
)
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import Field

# Set up logging
logger = logging.getLogger(__name__)

# Thread-local storage for OpenAI clients
thread_local = threading.local()

def get_openai_client(api_key: str):
    """Get a thread-local OpenAI client"""
    if not hasattr(thread_local, 'client') or thread_local.api_key != api_key:
        thread_local.client = OpenAI(api_key=api_key)
        thread_local.api_key = api_key
    return thread_local.client

class ChatOpenAIWrapper(BaseChatModel):
    """Chat model that uses OpenAI API with the golden example pattern."""
    
    api_key: str = Field(description="OpenAI API key")
    model: str = Field(default="gpt-4", description="OpenAI model name")
    temperature: float = Field(default=0.7, description="Temperature for sampling")
    format: Optional[str] = Field(default=None, description="Format for the response (e.g., 'json')")
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        format: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the ChatOpenAIWrapper.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use (e.g., gpt-4, gpt-3.5-turbo)
            temperature: Temperature for sampling
            format: Format for the response (e.g., "json")
            **kwargs: Additional arguments
        """
        super().__init__(
            api_key=api_key,
            model=model,
            temperature=temperature,
            format=format,
            **kwargs
        )
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response using OpenAI API."""
        
        # Get thread-local OpenAI client
        client = get_openai_client(self.api_key)
        
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for message in messages:
            if hasattr(message, 'type'):
                role = message.type
                if role == "system":
                    openai_messages.append({"role": "system", "content": message.content})
                elif role == "human":
                    openai_messages.append({"role": "user", "content": message.content})
                elif role == "ai":
                    openai_messages.append({"role": "assistant", "content": message.content})
                else:
                    # Default to user for unknown types
                    openai_messages.append({"role": "user", "content": message.content})
            else:
                # Fallback for messages without type
                openai_messages.append({"role": "user", "content": str(message.content)})
        
        # Convert messages to the input format for responses.create
        # For the golden example pattern, we need to concatenate all messages into a single input
        full_input = ""
        for message in openai_messages:
            if message["role"] == "system":
                full_input += f"System: {message['content']}\n\n"
            elif message["role"] == "user":
                full_input += f"User: {message['content']}\n\n"
            elif message["role"] == "assistant":
                full_input += f"Assistant: {message['content']}\n\n"
            else:
                full_input += f"{message['content']}\n\n"
        
        try:
            logger.info(f"Calling OpenAI API with model: {self.model}")
            logger.debug(f"Input preview: {full_input[:500]}...")
            
            # Make the API call using the golden example pattern exactly as specified
            response = client.responses.create(
                model=self.model,  # Either FOLDER_MODEL or RUN_MODEL from your example
                input=full_input  # Your prompt text
            )
            
            # Extract the response content from the complex Response object structure
            content = self._extract_content_from_response(response)
            logger.info(f"OpenAI API response received: {len(content)} characters")
            
            # Create LangChain compatible response
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise e
    
    def _extract_content_from_response(self, response):
        """Extract text content from the complex OpenAI Response object structure."""
        try:
            # Based on your actual response structure:
            # Response(output=[ResponseReasoningItem(...), ResponseOutputMessage(content=[ResponseOutputText(text="...")])])
            
            logger.info(f"Response type: {type(response)}")
            
            # Navigate through the response structure
            if hasattr(response, 'output') and response.output:
                # Iterate through output items to find the message
                for output_item in response.output:
                    # Look for ResponseOutputMessage (the actual content)
                    if (hasattr(output_item, 'type') and 
                        output_item.type == 'message' and 
                        hasattr(output_item, 'content')):
                        
                        # Extract text from ResponseOutputText items
                        for content_item in output_item.content:
                            if (hasattr(content_item, 'type') and 
                                content_item.type == 'output_text' and 
                                hasattr(content_item, 'text')):
                                
                                extracted_text = content_item.text
                                logger.info(f"✅ Successfully extracted text content ({len(extracted_text)} chars)")
                                logger.debug(f"Extracted content preview: {extracted_text[:200]}...")
                                return extracted_text
            
            # Additional fallbacks for different response structures
            
            # Try direct text attribute
            if hasattr(response, 'text') and response.text:
                logger.info("✅ Using response.text fallback")
                return response.text
            
            # Try content attribute
            if hasattr(response, 'content') and response.content:
                logger.info("✅ Using response.content fallback")
                return response.content
            
            # Try choices structure (for standard chat completions format)
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    logger.info("✅ Using choices[0].message.content fallback")
                    return choice.message.content
            
            # Last resort: convert to string but warn user
            logger.warning("⚠️  Could not extract text content, using string conversion")
            logger.warning(f"Response structure debug: {dir(response)}")
            return str(response)
            
        except Exception as e:
            logger.error(f"❌ Error extracting content from response: {str(e)}")
            logger.error(f"Response type: {type(response)}")
            logger.error(f"Available attributes: {dir(response) if hasattr(response, '__dict__') else 'None'}")
            # Emergency fallback: return string representation
            return str(response)
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "openai-wrapper"
    
    @property 
    def _identifying_params(self) -> dict:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "format": self.format,
        }