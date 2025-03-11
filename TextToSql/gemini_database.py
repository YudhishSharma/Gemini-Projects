from pyexpat import model
import time
from turtle import mode
from urllib import response

from requests import get
from spending_analysis import get_spending_analysis
from dotenv import load_dotenv

import google.generativeai as genai
import streamlit as st
import speech_recognition as sr
import os
import json

from chat_history import load_chat_history_from_file, save_chat_history_to_file
from gemini_ai import text_to_sql_using_gemini
from speech_input import get_speech_input
import prompts

# Load environment variable from .env file
load_dotenv()

# Configure GenAI key
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))


# Default Message
DEFAULT_ASSISTANT_MESSAGE = "Hi buddy!! 😊 How can I help you with your account?"



# Streamlit part
st.set_page_config(page_title = "Text To SQL")
st.header("Gemini Query Retriever")

# Store conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = load_chat_history_from_file() or [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]

# New Chat button to start new conversation
if st.button("New Chat"):
    st.session_state.clear()
    st.session_state["messages"] = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]
    save_chat_history_to_file([])
    st.success("Chat reset successfully. Start a new conversation.")
    
# Display previous chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
      
      
if user_input := st.chat_input("Enter your query"):
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    text_to_sql_using_gemini(user_input, prompts.sql_prompt)
    

if st.button("🎙 Speak"):
    speech_input = get_speech_input()
    if(speech_input):
        st.session_state["messages"].append({"role": "user", "content": speech_input})
        with st.chat_message("user"):
            st.write(speech_input)
        text_to_sql_using_gemini(speech_input, prompts.sql_prompt)   

with st.sidebar:
    st.header("💰 Spending Insights")
    spending_feedback = get_spending_analysis()
    st.write(spending_feedback)
    
    time.sleep(120)
    st.rerun()
