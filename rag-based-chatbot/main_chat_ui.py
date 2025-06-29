import os
from chatbot import ComplaintSession, ask_knowledge_base
from utils import clean_text
import re 
from datetime import datetime


session = ComplaintSession()

session = ComplaintSession()
collecting = False  # Flag to start collection only after intent

# Log directory
LOG_FILE = "logs/chat_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_chat(role, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{role}: {message.strip()}\n")

def detect_intent(user_input: str):
    ui = user_input.strip().lower()

    # ✅ Recognize raw 8-digit hex complaint ID
    if re.fullmatch(r'[a-f0-9]{8}', ui):
        return "status"

    if re.search(r'\bfile.*complaint\b|\bregister.*issue\b|\bproblem with order\b', ui):
        return "complaint"
    if re.search(r'\bcomplaint\s*id[: ]*\w+|\bshow\s+details\s+for\s+complaint\b|\bstatus\s+of\s+(complaint\s+)?id\b', ui):
        return "status"
    if "last complaint" in ui:
        return "last_status"

    return "question"

print("Chatbot: Hi! How can I help you today?")

while True:
    user_input = input("User: ").strip()
    log_chat("User", user_input)

    # Intent detection
    if not collecting:
        intent = detect_intent(user_input)

        if intent == "complaint":
            print("Chatbot: I'm sorry to hear that. Let's file a complaint. Please provide your name.")
            log_chat("Chatbot", "I'm sorry to hear that. Let's file a complaint. Please provide your name.")
            collecting = True
            continue


        elif intent == "status":
            user_input_clean = user_input.strip().lower()
            log_chat("user_input_clean", user_input_clean)

            # Extract complaint ID: full match or match from sentence
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

                except Exception as e:
                    print("Chatbot: Sorry, something went wrong while retrieving the complaint.")
                    log_chat("Chatbot", "Sorry, something went wrong while retrieving the complaint.")

            else:
                print("Chatbot: Please provide a valid complaint ID.")
                log_chat("Chatbot", "Please provide a valid complaint ID.")

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
                    print(f"Chatbot: Please provide your {next_field.replace('_', ' ')}.")
                else:
                    result = session.submit_complaint()
                    print(f"Chatbot: ✅ Thank you, {session.data['name']}. Your complaint has been registered with ID: {result['complaint_id']}")
                    log_chat("Chatbot", f"✅ Thank you, {session.data['name']}. Your complaint has been registered with ID: {result['complaint_id']}")
                    collecting = False
                    session = ComplaintSession()  # Reset
    else:
        response = ask_knowledge_base(user_input)
        # If response is a dict, extract the string value (assume key 'output' or 'result' or first str value)
        if isinstance(response, dict):
            response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
        else:
            response_text = response
        print("Chatbot:", clean_text(response_text))        
