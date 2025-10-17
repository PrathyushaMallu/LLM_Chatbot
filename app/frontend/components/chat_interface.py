"""
Chat interface component for Streamlit.
"""

import streamlit as st
import asyncio
from typing import Callable, Awaitable
from datetime import datetime


class ChatInterface:
    """Chat interface component for displaying and managing chat interactions."""
    
    def __init__(self):
        """Initialize chat interface."""
        self.message_container_height = 400
    
    def render(self, send_message_callback: Callable[[str], Awaitable[str]]):
        """
        Render the chat interface.
        
        Args:
            send_message_callback: Async function to send messages
        """
        # Chat history container
        with st.container():
            st.subheader("💬 Chat")

            # Show API status (only display when connected to avoid confusing users)
            api_status = st.session_state.get("api_status", {})
            if api_status.get("connected"):
                st.success("API: Connected")

            # Display chat messages (scrollable)
            self._display_chat_history()

            # Message input
            self._render_message_input(send_message_callback)

            # Chat controls (export, save, clear)
            self._render_chat_controls()
    
    def _display_chat_history(self):
        """Display the chat message history."""
        # Create a scrollable container for messages
        with st.container():
            if st.session_state.messages:
                for idx, message in enumerate(st.session_state.messages):
                    self._render_message(
                        message.get("content", ""),
                        message.get("role", "assistant"),
                        message.get("timestamp"),
                        meta=message.get("meta"),
                        key=f"msg_{idx}"
                    )
            else:
                st.info("👋 Hello! I'm your AI assistant. How can I help you today?")
    
    def _render_message(self, content: str, role: str, timestamp: datetime = None, meta: dict = None, key: str = None):
        """
        Render a single message.
        
        Args:
            content: Message content
            role: Message role (user/assistant)
            timestamp: Message timestamp
        """
        if role == "user":
            # User message (right-aligned)
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col2:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #E3F2FD;
                            padding: 10px;
                            border-radius: 10px;
                            margin: 5px 0;
                            border-inline-start: 4px solid #2196F3;
                        ">
                            <strong>You:</strong> {content}
                            {f"<br><small style='color: #666;'>{timestamp.strftime('%H:%M')}</small>" if timestamp else ""}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            # Assistant message (left-aligned)
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Display assistant message with optional metadata
                    footer = f"<br><small style='color: #666;'>{timestamp.strftime('%H:%M')}</small>" if timestamp else ""
                    meta_html = ""
                    if meta:
                        meta_parts = []
                        if meta.get("model"): meta_parts.append(f"Model: {meta.get('model')}")
                        if meta.get("tokens"): meta_parts.append(f"Tokens: {meta.get('tokens')}")
                        if meta.get("provider"): meta_parts.append(f"Provider: {meta.get('provider')}")
                        if meta_parts:
                            meta_html = f"<br><small style='color: #999;'>{' | '.join(meta_parts)}</small>"

                    st.markdown(
                        f"""
                        <div style="
                            background-color: #F5F5F5;
                            padding: 10px;
                            border-radius: 10px;
                            margin: 5px 0;
                            border-inline-start: 4px solid #4CAF50;
                        ">
                            <strong>🤖 Assistant:</strong> {content}
                            {footer}
                            {meta_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    def _render_message_input(self, send_message_callback: Callable[[str], Awaitable[str]]):
        """
        Render message input area.
        
        Args:
            send_message_callback: Callback function for sending messages
        """
        # Responsive layout: large input on desktop, compact on mobile
        with st.form(key="message_form", clear_on_submit=True):
            cols = st.columns([6, 1])
            with cols[0]:
                user_input = st.text_area(
                    "Message input",
                    placeholder="Ask me anything...",
                    height=120,
                    key="user_input",
                    label_visibility='collapsed'
                )

            with cols[1]:
                submit_button = st.form_submit_button("Send 📤")

        # Handle message submission
        if submit_button and user_input.strip():
            # Add user message immediately for optimistic UI
            user_message = {"role": "user", "content": user_input.strip(), "timestamp": datetime.now()}
            st.session_state.messages.append(user_message)

            # Set typing indicator
            st.session_state.typing = True

            # Streaming response: call send_message_callback and stream interim tokens
            try:
                # If the callback supports async streaming, it should yield partial chunks
                # We'll support both sync return and generator-like streaming via asyncio
                response = asyncio.run(send_message_callback(user_input.strip()))

                # If response is a dict with message and meta, normalize
                assistant_content = response
                assistant_meta = None
                if isinstance(response, dict):
                    assistant_content = response.get("message") or response.get("content")
                    assistant_meta = response.get("meta")

                assistant_message = {"role": "assistant", "content": assistant_content, "timestamp": datetime.now(), "meta": assistant_meta}
                st.session_state.messages.append(assistant_message)

            except Exception as e:
                # Append error as assistant message
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}", "timestamp": datetime.now()})
                st.error(f"Error sending message: {str(e)}")
            finally:
                st.session_state.typing = False

            # Rerun to update the display
            st.rerun()
    
    def _handle_message_submission(
        self, 
        user_input: str, 
        send_message_callback: Callable[[str], Awaitable[str]]
    ):
        """
        Handle message submission.
        
        Args:
            user_input: User's input message
            send_message_callback: Callback function for sending messages
        """
        # Add user message to chat history
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            try:
                # Send message asynchronously
                response = asyncio.run(send_message_callback(user_input))
                
                # Add assistant response to chat history
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                }
                st.session_state.messages.append(assistant_message)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Rerun to update the display
        st.rerun()
    
    def _render_chat_controls(self):
        """Render chat control buttons."""
        col1, col2, col3, col4 = st.columns([1,1,1,1])

        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.success("Chat cleared")
                st.rerun()

        with col2:
            if st.button("💾 Save Chat", use_container_width=True):
                self._save_chat_history()

        with col3:
            if st.button("📋 Export Chat", use_container_width=True):
                self._export_chat_history()

        with col4:
            if st.button("🔁 Regenerate Last", use_container_width=True):
                # Attempt to regenerate the last assistant response using last user message
                last_user = next((m for m in reversed(st.session_state.messages) if m["role"]=="user"), None)
                if last_user:
                    # remove last assistant if exists
                    if st.session_state.messages and st.session_state.messages[-1]["role"]=="assistant":
                        st.session_state.messages.pop()
                    # trigger send for last_user content
                    try:
                        asyncio.run(self._regenerate(last_user["content"]))
                    except Exception as e:
                        st.error(f"Regenerate failed: {e}")
                else:
                    st.warning("No user message to regenerate from")
    
    def _save_chat_history(self):
        """Save chat history to session state."""
        try:
            # In a real application, this would save to a database
            cid = st.session_state.conversation_id or f"conv_{int(datetime.now().timestamp())}"
            st.session_state.conversation_id = cid
            st.session_state.chat_history[cid] = list(st.session_state.messages)
            st.success("Chat saved successfully!")
        except Exception as e:
            st.error(f"Error saving chat: {str(e)}")
    
    def _export_chat_history(self):
        """Export chat history as downloadable file."""
        try:
            if not st.session_state.messages:
                st.warning("No messages to export.")
                return
            
            # Create export content
            export_content = []
            export_content.append(f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            export_content.append("=" * 50)
            
            for message in st.session_state.messages:
                role = "You" if message["role"] == "user" else "Assistant"
                timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M:%S")
                export_content.append(f"[{timestamp}] {role}: {message['content']}")
                export_content.append("")
            
            export_text = "\n".join(export_content)
            
            # Offer download and show as preview
            st.download_button(
                label="📥 Download Chat",
                data=export_text,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            st.text_area("Export Preview", value=export_text, height=200)
            
        except Exception as e:
            st.error(f"Error exporting chat: {str(e)}")

    async def _regenerate(self, user_text: str):
        """Helper to regenerate a response for a previous user message."""
        # placeholder - in real app we'd call the LLM service
        st.session_state.typing = True
        try:
            # simple echo fallback
            assistant_message = {"role": "assistant", "content": f"(Regenerated) {user_text}", "timestamp": datetime.now()}
            st.session_state.messages.append(assistant_message)
        finally:
            st.session_state.typing = False