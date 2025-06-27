from chatbot import ComplaintSession, ask_knowledge_base
from utils import clean_text

session = ComplaintSession()

session = ComplaintSession()
collecting = False  # Flag to start collection only after intent

print("Chatbot: Hi! How can I help you today?")
while True:
    user_input = input("User: ").strip()

    # Intent detection
    if not collecting:
        if "complaint" in user_input.lower():
            print("Chatbot: I'm sorry to hear that. Let's file a complaint. Please provide your name.")
            collecting = True
            continue
        else:
            # Try using RAG to answer normal questions
            response = ask_knowledge_base(user_input)
                 # If response is a dict, extract the string value (assume key 'output' or 'result' or first str value)
            if isinstance(response, dict):
                response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
            else:
                response_text = response

            print("Chatbot:", clean_text(response_text))   
            # print("Chatbot:", clean_text(response))
            continue

    # Collect complaint details after intent is confirmed
    if not session.is_complete():
        field = session.next_prompt()
        if field:
            session.set_field(field, user_input)
            if session.next_prompt():
                print(f"Chatbot: Please provide your {session.next_prompt().replace('_', ' ')}.")
            else:
                result = session.submit_complaint()
                print(f"Chatbot: Your complaint has been registered with ID: {result['complaint_id']}")
                collecting = False
                session = ComplaintSession()  # Reset for next conversation
    else:
        # print("Chatbot:", clean_text(ask_knowledge_base(user_input)))

        response = ask_knowledge_base(user_input)

        # If response is a dict, extract the string value (assume key 'output' or 'result' or first str value)
        if isinstance(response, dict):
            response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
        else:
            response_text = response

        print("Chatbot:", clean_text(response_text))        







# print("Chatbot: Hi! How can I help you today?")
# while True:
#     user_input = input("User: ")

#     # Check for complaint query
#     if "show details for complaint" in user_input.lower():
#         complaint_id = user_input.strip().split()[-1]
#         details = session.get_complaint_details(complaint_id)
#         print("Chatbot:", details)
#         continue

#     if not session.is_complete():
#         field = session.next_prompt()
#         if field:
#             session.set_field(field, user_input)
#             if session.next_prompt():
#                 print(f"Chatbot: Please provide your {session.next_prompt().replace('_', ' ')}.")
#             else:
#                 result = session.submit_complaint()
#                 print(f"Chatbot: Your complaint has been registered with ID: {result['complaint_id']}")
#     else:
#         response = ask_knowledge_base(user_input)

        # # If response is a dict, extract the string value (assume key 'output' or 'result' or first str value)
        # if isinstance(response, dict):
        #     response_text = response.get("output") or response.get("result") or next((v for v in response.values() if isinstance(v, str)), "")
        # else:
        #     response_text = response

        # print("Chatbot:", clean_text(response_text))        
