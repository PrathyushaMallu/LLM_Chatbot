"""
Main Streamlit application for the chatbot interface.
"""

import streamlit as st
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from config.settings import settings
from config.logging_config import setup_logging
from app.frontend.components.chat_interface import ChatInterface
from app.frontend.components.sidebar import Sidebar
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService


# Configure Streamlit page
st.set_page_config(
    page_title=settings.app_name,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logger = setup_logging(settings.log_level, settings.log_file)


class ChatbotApp:
    """Main chatbot application class."""
    
    def __init__(self):
        """Initialize the chatbot application."""
        self.chat_service = ChatService()
        self.llm_service = LLMService()
        self.chat_interface = ChatInterface()
        self.sidebar = Sidebar()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        # Messages are list of dicts: {role, content, timestamp, meta}
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Current conversation id (persisted when saving)
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = None

        # Basic user id
        if "user_id" not in st.session_state:
            st.session_state.user_id = "user_" + str(datetime.now().timestamp()).replace(".", "")

        # Saved conversations
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = {}

        # Model config for LLM calls
        if "model_config" not in st.session_state:
            st.session_state.model_config = {
                "model": getattr(settings, "openai_model", "gpt-3.5-turbo"),
                "temperature": getattr(settings, "temperature", 0.7),
                "max_tokens": getattr(settings, "max_tokens", 4000)
            }

        # API / LLM connection status
        if "api_status" not in st.session_state:
            st.session_state.api_status = {"connected": False, "last_checked": None, "details": None}

        # UI helpers
        if "typing" not in st.session_state:
            st.session_state.typing = False

        if "session_start" not in st.session_state:
            st.session_state.session_start = datetime.now()

        # Register a cleanup callback on session end
        if "cleanup_registered" not in st.session_state:
            st.session_state.cleanup_registered = True
            # No direct streamlit API for session end; we rely on explicit user actions to clear
            # Provide a small helper function available in session_state for explicit cleanup
            def _cleanup():
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.session_state.chat_history = {}
                st.session_state.api_status = {"connected": False, "last_checked": None, "details": None}
            st.session_state._cleanup = _cleanup
    
    async def send_message(self, user_message: str) -> str:
        """
        Send message to chatbot and get response.
        
        Args:
            user_message: User's message
        
        Returns:
            Bot's response message
        """
        try:
            # Log outgoing request from frontend (include model config)
            logger.info({
                "frontend_request": {
                    "user_id": st.session_state.user_id,
                    "conversation_id": st.session_state.conversation_id,
                    "message": user_message,
                    "model_config": st.session_state.get("model_config")
                }
            })

            # Process message through chat service
            response = await self.chat_service.process_message(
                message=user_message,
                conversation_id=st.session_state.conversation_id,
                user_id=st.session_state.user_id
            )

            # Log service response at frontend side (truncate message for logs)
            resp_payload = {
                "conversation_id": response.conversation_id,
                "message_id": response.message_id,
                "model_used": response.model_used,
                "provider_used": response.provider_used,
                "tokens_used": response.tokens_used,
                "processing_time": response.processing_time,
                "message_preview": (response.message[:1000] + "...[truncated]") if response.message and len(response.message) > 1000 else response.message
            }
            logger.info({"frontend_response": resp_payload})
            
            # Update session state
            st.session_state.conversation_id = response.conversation_id
            
            return response.message
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def run(self):
        """Run the main application."""
        # App header
        st.title(f"🤖 {settings.app_name}")
        st.markdown(f"*Version {settings.version}*")
        
        # Sidebar
        self.sidebar.render()
        
        # Main chat interface
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            self.chat_interface.render(self.send_message)
        
        # Footer
        with st.container():
            st.markdown("---")
            st.markdown(
                f"<div style='text-align: center; color: #666;'>"
                f"Powered by {settings.openai_model} | "
                f"Built with Streamlit & FastAPI"
                f"</div>",
                unsafe_allow_html=True
            )


def main():
    """Main application entry point."""
    try:
        app = ChatbotApp()
        app.run()
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()