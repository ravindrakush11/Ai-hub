# gradio_app.py
import gradio as gr
import re
from datetime import datetime
from chatbot import ComplaintSession, ask_knowledge_base
from utils import clean_text, detect_intent
# from main_chat_ui import 

chat_state = {"session": ComplaintSession(), "collecting": False, "chat_log": []}

def chatbot_interface(user_input):
    session = chat_state["session"]
    collecting = chat_state["collecting"]
    chat_log = chat_state["chat_log"]
    bot_response = ""

    chat_log.append(("User", user_input))

    if not collecting:
        intent = detect_intent(user_input)

        if intent == "complaint":
            bot_response = "I'm sorry to hear that. Let's file a complaint. Please provide your name."
            chat_state["collecting"] = True
            chat_log.append(("Chatbot", bot_response))
            return format_chat(chat_log)

        elif intent == "status":
            user_input_clean = user_input.strip().lower()
            if re.fullmatch(r'[a-f0-9]{8}', user_input_clean):
                complaint_id = user_input_clean
            else:
                match = re.search(r'\b([a-f0-9]{8})\b', user_input_clean)
                complaint_id = match.group(1) if match else None

            if complaint_id:
                try:
                    result = session.get_complaint_details(complaint_id)
                    details = [f"{key.replace('_', ' ').capitalize()}: {datetime.fromisoformat(value).strftime('%B %d, %Y %I:%M %p') if key == 'created_at' else value}" for key, value in result.items()]
                    bot_response = "\n".join(details)
                except:
                    bot_response = "Sorry, something went wrong while retrieving the complaint."
            else:
                bot_response = "Please provide a valid complaint ID."

            chat_log.append(("Chatbot", bot_response))
            return format_chat(chat_log)

        else:
            response = ask_knowledge_base(user_input)
            if isinstance(response, dict):
                response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
            else:
                response_text = response
            bot_response = clean_text(response_text)
            chat_log.append(("Chatbot", bot_response))
            return format_chat(chat_log)

    if not session.is_complete():
        field = session.next_prompt()
        if field:
            success = session.set_field(field, user_input)
            if success:
                next_field = session.next_prompt()
                if next_field:
                    bot_response = f"Please provide your {next_field.replace('_', ' ')}."
                else:
                    result = session.submit_complaint()
                    bot_response = f"✅ Thank you, {session.data['name']}. Your complaint has been registered with ID: {result['complaint_id']}"
                    chat_state["collecting"] = False
                    chat_state["session"] = ComplaintSession()
            else:
                bot_response = f"Please re-enter a valid {field.replace('_', ' ')}."

        chat_log.append(("Chatbot", bot_response))
        return format_chat(chat_log)

    response = ask_knowledge_base(user_input)
    if isinstance(response, dict):
        response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
    else:
        response_text = response
    bot_response = clean_text(response_text)
    chat_log.append(("Chatbot", bot_response))
    return format_chat(chat_log)

def format_chat(log):
    return "\n".join([f"🧑 {u}: {m}" if u == "User" else f"🤖 {u}: {m}" for u, m in log])

gr.Interface(
    fn=chatbot_interface,
    inputs=gr.Textbox(lines=2, placeholder="Type your message..."),
    outputs=gr.Textbox(lines=20, label="Chat History"),
    title="📬 Complaint Resolution Assistant (RAG-based)",
    allow_flagging="never"
).launch(
    # server_name="0.0.0.0",
    # server_port=7860,
    share=True,
    inbrowser=True
)
