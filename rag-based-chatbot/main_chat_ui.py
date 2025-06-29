import os
import re
from datetime import datetime
from chatbot import ComplaintSession, ask_knowledge_base
from utils import clean_text, detect_intent

# Session and logging setup
session = ComplaintSession()
collecting = False
LOG_FILE = "logs/chat_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_chat(role, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{role}: {message.strip()}\n")

# Start conversation
print("Chatbot: Hi! How can I help you today?")
log_chat("Chatbot", "Hi! How can I help you today?")

while True:
    user_input = input("User: ").strip()
    log_chat("User", user_input)

    # Command keywords
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chatbot: 👋 Thank you for chatting. Goodbye!")
        log_chat("Chatbot", "Session ended by user.")
        break

    if user_input.lower() in ["restart", "start over"]:
        print("Chatbot: 🔄 Restarting the conversation. Let's begin again.")
        log_chat("Chatbot", "Session restarted.")
        session = ComplaintSession()
        collecting = False
        print("Chatbot: Hi! How can I help you today?")
        continue

    if user_input.lower() in ["help", "commands", "options"]:
        help_msg = (
            "💡 You can enter the following commands any time:\n"
            "- `restart` → Restart the session\n"
            "- `exit` → Exit the chatbot\n"
            "- `help` → Show this help message\n"
            "- Or just talk naturally! I can handle questions, complaints, and more."
        )
        print(f"Chatbot: {help_msg}")
        log_chat("Chatbot", help_msg)
        continue

    # Intent detection
    if not collecting:
        intent = detect_intent(user_input)

        if intent == "complaint":
            print("Chatbot: Let's file a complaint. Please provide your name.")
            log_chat("Chatbot", "Let's file a complaint. Please provide your name.")
            collecting = True
            continue

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
                    print("Chatbot:")
                    for key, value in result.items():
                        if key == "created_at":
                            try:
                                value = datetime.fromisoformat(value).strftime("%B %d, %Y %I:%M %p")
                            except:
                                pass
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
                        log_chat("Chatbot", f"{key.replace('_', ' ').capitalize()}: {value}")
                    note = "\nChatbot: This is the registered complaint information.\nNote: For real-time status updates, please contact support or escalation@company.com."
                    print(note)
                    log_chat("Chatbot", note)
                except:
                    err = "Chatbot: Sorry, we couldn't find that complaint ID."
                    print(err)
                    log_chat("Chatbot", err)
            else:
                msg = "Chatbot: Please provide a valid complaint ID."
                print(msg)
                log_chat("Chatbot", msg)
            continue

        else:
            response = ask_knowledge_base(user_input)
            if isinstance(response, dict):
                response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
            else:
                response_text = response
            print("Chatbot:", clean_text(response_text))
            log_chat("Chatbot", clean_text(response_text))
            continue

    if not session.is_complete():
        field = session.next_prompt()
        if field:
            success = session.set_field(field, user_input)
            if success:
                next_field = session.next_prompt()
                if next_field:
                    msg = f"Please provide your {next_field.replace('_', ' ')}."
                    print(f"Chatbot: {msg}")
                    log_chat("Chatbot", msg)
                else:
                    result = session.submit_complaint()
                    msg = f"✅ Thank you, {session.data['name']}. Your complaint has been registered with ID: {result['complaint_id']}"
                    print(f"Chatbot: {msg}")
                    log_chat("Chatbot", msg)
                    collecting = False
                    session = ComplaintSession()  # Reset
    else:
        response = ask_knowledge_base(user_input)
        if isinstance(response, dict):
            response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
        else:
            response_text = response
        print("Chatbot:", clean_text(response_text))
        log_chat("Chatbot", clean_text(response_text))
