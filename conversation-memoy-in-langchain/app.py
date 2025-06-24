import os
import json
import logging
import mlflow
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState

load_dotenv()
logging.basicConfig(level=logging.INFO)

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
MODEL_NAME = 'qwen/qwen3-32b'
TEMPERATURE = 0

llm = ChatGroq(model=MODEL_NAME, temperature=TEMPERATURE)

def get_system_prompt():
    return SystemMessage(content="You are a HR who recruits candidates in the IT sector.")

def save_conversation(thread_id, messages):
    os.makedirs("conversations", exist_ok=True)
    with open(f"conversations/chat_{thread_id}.json", "w") as f:
        json.dump([{"role": type(m).__name__, "content": m.content} for m in messages], f, indent=2)

def log_to_mlflow(user_input, bot_response, thread_id):
    mlflow.log_param("model_name", MODEL_NAME)
    mlflow.log_param("temperature", TEMPERATURE)
    mlflow.log_param("thread_id", thread_id)

    with open("user_input.txt", "w", encoding="utf-8") as f:
        f.write(user_input)
    with open("bot_response.txt", "w", encoding="utf-8") as f:
        f.write(bot_response)

    mlflow.log_artifact("user_input.txt")
    mlflow.log_artifact("bot_response.txt")


def chat_node(state: MessagesState):
    system_message = get_system_prompt()
    response = llm.invoke([system_message] + state["messages"])
    return {"messages": state["messages"] + [response]}

builder = StateGraph(state_schema=MessagesState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")

memory = MemorySaver()
chat_app = builder.compile(checkpointer=memory)

thread_id = "session-001"
mlflow.set_experiment("Conversational_HR_Chatbot")

try:
    with mlflow.start_run(run_name=f"chat-session-{thread_id}"):
        print("HR Chatbot ready (type 'exit' to end)")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Session ended.")
                break

            state_update = {"messages": [HumanMessage(content=user_input)]}
            result = chat_app.invoke(state_update, {"configurable": {"thread_id": thread_id}})
            ai_msg = result["messages"][-1]

            print("Bot:", ai_msg.content)

            save_conversation(thread_id, result["messages"])
            log_to_mlflow(user_input, ai_msg.content, thread_id)

except KeyboardInterrupt:
    print("\nSession terminated.")


