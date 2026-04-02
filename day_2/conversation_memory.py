from ast import In
from pathlib import Path
from dotenv import load_dotenv
import os

from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from file_message_chat_history import FileChatMessageHistory

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=API_KEY,
    temperature=0.7,
    max_output_tokens=150,
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful technical assistant"),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

chain = prompt | llm

memory_store = {}

def get_in_memroy_message_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in memory_store:
        memory_store[session_id] = InMemoryChatMessageHistory()
    return memory_store[session_id]

def get_file_message_history(session_id: str) -> FileChatMessageHistory:
    file_path = Path.cwd() / f"{session_id}_chat_history.json"
    if session_id not in memory_store:
        memory_store[session_id] = FileChatMessageHistory(file_path=str(file_path))
    return memory_store[session_id]

chat = RunnableWithMessageHistory(
    chain,
    get_file_message_history,
    input_messages_key="input",
    history_messages_key="history",
)

def chat_loop():
    print("LangChain chat with managed memory. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break

        response = chat.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "ooredoo-demo"}}
        )

        print("Assistant:", response.content)

if __name__ == "__main__":
    chat_loop()