import streamlit as st
from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import json
from dotenv import load_dotenv
import os
import shutil


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

# Gemini
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# Local imports
import data_injection as datas
import application_logic as app_logic


DATA_PATH = "static/data"
CHROMA_PATH = "chroma"
load_dotenv(dotenv_path=".env.local")

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents

def update_text_docs():
    db_records = datas.get_table_data()

    string_data = """
    A Streamlit dashboard visualizing teenage pregnancy trends in Rwanda for teenager ranging from 15 to 19, 
    based on data from the Rwanda Demographic and Health Surveys conducted in 2010-2011, 2014-2015, and 2019-2020.
    This dashboard provides an overview of the data from these years, Note that: datasets are from NISR website and DHS Program website.
    illustrating changes in teenage pregnancy rates over time.
    
    Terms and explanations:
    hello, hi, hey, greetings, what's u, howdy: These are greetings, response is "I'm ready to answer your questions. Do you have any questions about the teenage pregnancy data I have access to?"
    bye, goodbye, see you, take care: these are words user use to indicate that they are about to close chat, respnse is "Goodbye! Let me know if you need help with anything else."
    Survey rounds in Rwanda: take period of five years between each.
    """
    string_district = ""

    # Generate data for districts
    survey_grouping = app_logic.records_grouped_by(db_records, "survey_round")
    for survey_name, survey_records in survey_grouping.items():    
        grouped_districts = app_logic.create_upload_summary(survey_records, "district")
        string_district+= app_logic.get_districts_string(grouped_districts, survey_name)

    # Generate data for country
    string_country = ""

    country_grouping = app_logic.records_grouped_by(db_records, "country")
    for country, records in country_grouping.items():    
        grouped_countries = app_logic.create_upload_summary(records, "country")
        string_country += app_logic.get_country_string(grouped_countries, country)

    string_data += string_district + string_country
    with open(DATA_PATH + "/pregnancy_summary.txt", "w") as file:
        file.write(string_data)

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.environ["GOOGLE_API_KEY"])

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(chunks, get_embeddings(), persist_directory=CHROMA_PATH)
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

def data_template(user_input):
    return f"Based on the following input, provide the most relevant information: {user_input}"



def query_data(query, conversation_history):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0, 
        api_key=os.environ["GOOGLE_API_KEY"],
        name="Datawizards Assistant"
    )
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)

    # Add history to the query for continuity
    full_query = "\n".join([f"{msg['role'].capitalize()}: {msg['prompt']}" for msg in conversation_history])
    full_query += f"\nUser: {query}"

    retriever_output = qa.run(data_template(full_query))
    return retriever_output

@st.dialog("Datawizard Assistant")
def chat_with_assistant():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    st.write("Welcome back!")
    history_messages = st.session_state.chat_messages

    messages = st.container(height=300)
    for chat in history_messages:
        messages.chat_message(chat["role"]).write(chat["prompt"])

    if prompt := st.chat_input("Prompt a question!"):    
        # Update chat conversation
        messages.chat_message("user").write(prompt)

        with messages:
            with st.spinner("Generating a Response!"):
                # Handle specific query
                if "what is your name" in prompt.lower():
                    ai_response = "I'm Datawizards Assistant."
                else:
                    ai_response = query_data(prompt, history_messages)

                messages.chat_message("ai").write(ai_response)

                # Update global session state
                st.session_state.chat_messages.append({
                    "role": "user",
                    "prompt": prompt
                })

                st.session_state.chat_messages.append({
                    "role": "ai",
                    "prompt": ai_response
                })


def main():
    # Update Text Document
    update_text_docs()
    chromadb.api.client.SharedSystemClient.clear_system_cache()

    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)