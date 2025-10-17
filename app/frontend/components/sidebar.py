"""
Sidebar component for Streamlit application.
"""

import streamlit as st
from datetime import datetime
import requests
from typing import Dict, Any

from config.settings import settings


class Sidebar:
    """Sidebar component for application controls and settings."""
    
    def __init__(self):
        """Initialize sidebar component."""
        pass
    
    def render(self):
        """Render the sidebar with controls and information."""
        with st.sidebar:
            self._render_header()
            self._render_model_settings()
            self._render_conversation_info()
            self._render_statistics()
            self._render_help_section()
    
    def _render_header(self):
        """Render sidebar header."""
        st.markdown("## 🛠️ Settings")
        st.markdown("---")
    
    def _render_model_settings(self):
        """Render model configuration settings."""
        st.markdown("### 🤖 Model Settings")
        # Provider selection
        provider = st.selectbox(
            "Provider:",
            ["gemini", "openai"],
            index=["gemini", "openai"].index(getattr(settings, "default_llm_provider", "gemini")),
            help="Choose the LLM provider"
        )

        # Model selection based on provider
        if provider == "openai":
            available_models = [
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-4",
                "gpt-4-turbo-preview"
            ]
        else:
            # Gemini models (use configured default if present)
            gemini_default = getattr(settings, "gemini_model", "gemini-2.5-flash")
            available_models = [gemini_default, "gemini-pro", "gemini-pro-vision"]

        # Ensure current session model exists in list
        current_model = st.session_state.model_config.get("model", settings.openai_model)
        if current_model not in available_models:
            available_models.insert(0, current_model)

        selected_model = st.selectbox(
            "Model:",
            available_models,
            index=available_models.index(current_model if current_model in available_models else 0),
            help="Choose the AI model for responses"
        )
        
        # Temperature setting
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.model_config.get("temperature", settings.temperature),
            step=0.1,
            help="Controls randomness: 0 = focused, 2 = creative"
        )
        
        # Max tokens setting
        max_tokens = st.slider(
            "Max Tokens:",
            min_value=100,
            max_value=4000,
            value=st.session_state.model_config.get("max_tokens", settings.max_tokens),
            step=100,
            help="Maximum length of the response"
        )
        
        # Update session state, include provider
        st.session_state.model_config = {
            "provider": provider,
            "model": selected_model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.model_config = {
                "model": settings.openai_model,
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens
            }
            st.rerun()
        
        st.markdown("---")
    
    def _render_conversation_info(self):
        """Render current conversation information."""
        st.markdown("### 💬 Conversation Info")
        
        # Conversation ID
        if st.session_state.conversation_id:
            st.text_input(
                "Conversation ID:",
                value=st.session_state.conversation_id[:12] + "...",
                disabled=True,
                help="Current conversation identifier"
            )
        else:
            st.info("No active conversation")
        
        # User ID
        st.text_input(
            "User ID:",
            value=st.session_state.user_id[:12] + "...",
            disabled=True,
            help="Your user identifier"
        )
        
        # Message count
        message_count = len(st.session_state.messages)
        st.metric("Messages", message_count)

        # Conversation save/load
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("🆕 New Conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.success("Started new conversation!")
                st.rerun()

        with col2:
            if st.button("💾 Save Conversation", use_container_width=True):
                # Save into session_state.chat_history
                cid = st.session_state.conversation_id or f"conv_{int(datetime.now().timestamp())}"
                st.session_state.conversation_id = cid
                st.session_state.chat_history[cid] = list(st.session_state.messages)
                st.success("Conversation saved")

        # Load or delete saved conversations
        saved = list(st.session_state.chat_history.keys())
        if saved:
            sel = st.selectbox("Saved Conversations", ["--select--"] + saved)
            if sel and sel != "--select--":
                if st.button("🔄 Load", use_container_width=True):
                    st.session_state.messages = list(st.session_state.chat_history.get(sel, []))
                    st.session_state.conversation_id = sel
                    st.success(f"Loaded {sel}")
                    st.rerun()
                if st.button("🗑️ Delete", use_container_width=True):
                    if sel in st.session_state.chat_history:
                        del st.session_state.chat_history[sel]
                        st.success(f"Deleted {sel}")
                        st.rerun()
        
        st.markdown("---")
    
    def _render_statistics(self):
        """Render usage statistics."""
        st.markdown("### 📊 Statistics")
        
        # Calculate basic statistics
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("User", user_messages)
            
        with col2:
            st.metric("Assistant", assistant_messages)
        
        # Session duration
        if "session_start" not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        session_duration = datetime.now() - st.session_state.session_start
        duration_minutes = int(session_duration.total_seconds() / 60)
        
        st.metric("Session (min)", duration_minutes)
        
        st.markdown("---")
    
    def _render_help_section(self):
        """Render help and information section."""
        st.markdown("### ❓ Help")
        
        with st.expander("💡 Tips"):
            st.markdown("""
            **How to use:**
            - Type your message in the chat box
            - Adjust model settings for different responses
            - Use 'New Conversation' to start fresh
            - Export your chat for later reference
            
            **Model Tips:**
            - Lower temperature = more focused responses
            - Higher temperature = more creative responses
            - Adjust max tokens for longer/shorter replies
            """)
        
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            - If responses are slow, try a smaller max tokens value
            - If responses seem repetitive, increase temperature
            - For errors, check your internet connection
            - Clear cache and refresh if the app becomes unresponsive
            """)
        
        with st.expander("ℹ️ About"):
            st.markdown(f"""
            **{settings.app_name}**
            
            Version: {settings.version}
            
            This chatbot uses OpenAI's GPT models to provide 
            intelligent responses to your questions and conversations.
            
            Built with:
            - 🚀 FastAPI (Backend)
            - 🎨 Streamlit (Frontend)
            - 🤖 OpenAI GPT (AI)
            """)
        
        # API Status check
        st.markdown("### 🔍 System Status")
        
        if st.button("🩺 Check API Status", use_container_width=True):
            with st.spinner("Checking..."):
                tried = []
                success = False
                details = None
                # Candidate ports to try: configured, common defaults
                candidate_ports = [getattr(settings, "port", 8000), 8000, 8001]
                # Candidate paths to try: root health and API-prefixed provider health
                candidate_paths = ["/health", f"{settings.api_v1_str}/gemini/health", f"{settings.api_v1_str}/health"]

                for port in candidate_ports:
                    for path in candidate_paths:
                        url = f"http://127.0.0.1:{port}{path}"
                        tried.append(url)
                        try:
                            resp = requests.get(url, timeout=2)
                            if resp.status_code == 200:
                                # Prefer JSON details when available
                                try:
                                    details = resp.json()
                                except Exception:
                                    details = resp.text

                                st.session_state.api_status = {
                                    "connected": True,
                                    "last_checked": datetime.utcnow().isoformat(),
                                    "details": details,
                                    "checked_url": url
                                }
                                st.success(f"✅ API is healthy (checked {url})")
                                success = True
                                break
                            else:
                                # Keep trying other endpoints
                                continue
                        except Exception as e:
                            # ignore and try next candidate
                            details = str(e)
                            continue
                    if success:
                        break

                if not success:
                    st.session_state.api_status = {
                        "connected": False,
                        "last_checked": datetime.utcnow().isoformat(),
                        "details": details,
                        "tried": tried
                    }
                    st.error(f"❌ API not reachable. Tried: {', '.join(tried[:3])}...")
    
    def _get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        model_info = {
            "gpt-3.5-turbo": {
                "description": "Fast and efficient for most tasks",
                "context_length": "4K tokens",
                "strengths": "Speed, cost-effective"
            },
            "gpt-3.5-turbo-16k": {
                "description": "Extended context version of GPT-3.5",
                "context_length": "16K tokens",
                "strengths": "Longer conversations, document analysis"
            },
            "gpt-4": {
                "description": "Most capable model with advanced reasoning",
                "context_length": "8K tokens",
                "strengths": "Complex tasks, accuracy, reasoning"
            },
            "gpt-4-turbo-preview": {
                "description": "Latest GPT-4 with improved performance",
                "context_length": "128K tokens",
                "strengths": "Latest features, large contexts"
            }
        }
        
        return model_info.get(model_name, {
            "description": "Unknown model",
            "context_length": "Unknown",
            "strengths": "Unknown"
        })