"""
LLM service for handling language model interactions.
"""

import asyncio
import time
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import openai
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import settings
from app.models.chat_models import LLMConfig, MessageRole


class LLMService:
    """Service for LLM interactions using OpenAI API."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.logger = logging.getLogger(__name__)
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_config = LLMConfig(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        config: Optional[LLMConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            config: Optional LLM configuration override
        
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        llm_config = config or self.default_config
        
        try:
            # Validate API key
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Prepare messages for OpenAI API
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=llm_config.model,
                messages=formatted_messages,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                top_p=llm_config.top_p,
                frequency_penalty=llm_config.frequency_penalty,
                presence_penalty=llm_config.presence_penalty,
            )
            
            processing_time = time.time() - start_time
            
            # Extract response data
            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            self.logger.info(
                f"LLM response generated successfully. "
                f"Model: {llm_config.model}, "
                f"Tokens: {tokens_used}, "
                f"Time: {processing_time:.2f}s"
            )
            
            return {
                "message": assistant_message,
                "model_used": llm_config.model,
                "tokens_used": tokens_used,
                "processing_time": processing_time,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise Exception("Service temporarily unavailable due to rate limiting")
            
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"LLM service error: {str(e)}")
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Error generating LLM response: {str(e)} (Time: {processing_time:.2f}s)")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        config: Optional[LLMConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate chat response with conversation context.
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
            system_prompt: Optional system prompt
            config: Optional LLM configuration
        
        Returns:
            Dictionary containing response and metadata
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": MessageRole.SYSTEM.value,
                "content": system_prompt
            })
        else:
            # Default system prompt
            messages.append({
                "role": MessageRole.SYSTEM.value,
                "content": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."
            })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": MessageRole.USER.value,
            "content": user_message
        })
        
        return await self.generate_response(messages, config)
    
    async def validate_api_connection(self) -> bool:
        """
        Validate OpenAI API connection.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Simple test request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
            
        except Exception as e:
            self.logger.error(f"API validation failed: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available OpenAI models.
        
        Returns:
            List of available model names
        """
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo-preview"
        ]
    
    async def count_tokens(self, text: str, model: str = None) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count tokens for
            model: Model to use for counting (affects tokenization)
        
        Returns:
            Estimated token count
        """
        # Simple estimation: approximately 4 characters per token
        # This is a rough approximation - for production use tiktoken library
        return len(text) // 4