import gradio as gr
import re
from datetime import datetime
import time
# Assuming chatbot.py and utils.py are in the same directory
from chatbot import ComplaintSession, ask_knowledge_base
from utils import clean_text, detect_intent

# Global state for the chatbot session
chat_state = {"session": ComplaintSession(), "collecting": False}

# The main function that handles user input and generates bot responses
def chatbot_interface(user_input, history):
    # history is a list of tuples (user_message, bot_message)
    # It's automatically managed by gr.ChatInterface

    session = chat_state["session"]
    collecting = chat_state["collecting"]
    bot_response = ""

    # Initial bot message if the chat is just starting (optional, can be set in gr.ChatInterface)
    if not history:
        # You might want to remove this if you set initial_chatbot_message in gr.ChatInterface
        # This part handles the initial interaction if the user sends something first
        pass

    # --- Intent Detection and Initial Responses ---
    if not collecting:
        intent = detect_intent(user_input)

        if intent == "complaint":
            bot_response = "I'm sorry to hear that. Let's file a complaint. Please provide your name."
            chat_state["collecting"] = True
            # No need to append to chat_log, gr.ChatInterface handles history automatically
            return bot_response # Return only the bot's current message

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
                    details = [
                        f"**{key.replace('_', ' ').capitalize()}**: {datetime.fromisoformat(value).strftime('%B %d, %Y %I:%M %p') if key == 'created_at' else value}"
                        for key, value in result.items()
                    ]
                    bot_response = "Here are the complaint details:\n" + "\n".join(details)
                except Exception as e:
                    # In a real app, log the exception: print(f"Error retrieving complaint: {e}")
                    bot_response = "Sorry, something went wrong while retrieving the complaint details. Please ensure the ID is correct."
            else:
                bot_response = "Please provide a valid 8-character complaint ID to check the status."

            return bot_response

        else:
            # Fallback to knowledge base if no specific intent is detected
            response = ask_knowledge_base(user_input)
            if isinstance(response, dict):
                response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
            else:
                response_text = response
            bot_response = clean_text(response_text)
            return bot_response

    # --- Complaint Collection Flow ---
    if collecting and not session.is_complete():
        field = session.next_prompt()
        if field:
            success = session.set_field(field, user_input)
            if success:
                next_field = session.next_prompt()
                if next_field:
                    bot_response = f"Please provide your **{next_field.replace('_', ' ')}**."
                else:
                    # All fields collected, submit the complaint
                    result = session.submit_complaint()
                    bot_response = f"✅ Thank you, **{session.data['name']}**. Your complaint has been successfully registered with ID: **{result['complaint_id']}**.\n\nYou can use this ID to check the status later."
                    chat_state["collecting"] = False # Reset state
                    chat_state["session"] = ComplaintSession() # Start a new session
            else:
                bot_response = f"That doesn't seem like a valid **{field.replace('_', ' ')}**. Please try again."

        return bot_response

    # If collecting is true but session is complete (shouldn't happen with proper flow)
    # or if the initial intent wasn't handled and collecting wasn't set,
    # this part would be reached, but with the current logic, the flow should
    # ideally be captured by the above conditions.
    # As a fallback, if collecting is true and session is complete, or if something
    # goes off-path, default to knowledge base or a general response.
    # For robustness, we'll keep the knowledge base call here as a final fallback.
    response = ask_knowledge_base(user_input)
    if isinstance(response, dict):
        response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
    else:
        response_text = response
    bot_response = clean_text(response_text)
    return bot_response

# Gradio Interface setup using gr.ChatInterface
gr.ChatInterface(
    chatbot_interface,
    title="📬 Complaint Resolution Assistant",
    description="I'm here to help you file new complaints or check the status of existing ones. Just type your query!",
    theme=gr.themes.Soft(), # A modern and soft theme
    examples=[
        ["I want to file a complaint"],
        ["Check my complaint id 4541553b"],
        ["What are your operating hours?"],
        ["How do I reset my password?"],
    ],
 
    submit_btn="Send Message", # Customize the submit button text
    autofocus=True, # Automatically focus on the input box
   
).queue().launch(
    # share=True # Uncomment to share your app publicly (temporarily)
)