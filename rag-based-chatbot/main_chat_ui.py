from chatbot import ComplaintSession, ask_knowledge_base

session = ComplaintSession()

print("Chatbot: Hi! How can I help you today?")
while True:
    user_input = input("User: ")

    # Check for complaint query
    if "show details for complaint" in user_input.lower():
        complaint_id = user_input.strip().split()[-1]
        details = session.get_complaint_details(complaint_id)
        print("Chatbot:", details)
        continue

    if not session.is_complete():
        field = session.next_prompt()
        if field:
            session.set_field(field, user_input)
            if session.next_prompt():
                print(f"Chatbot: Please provide your {session.next_prompt().replace('_', ' ')}.")
            else:
                result = session.submit_complaint()
                print(f"Chatbot: Your complaint has been registered with ID: {result['complaint_id']}")
    else:
        print("Chatbot:", ask_knowledge_base(user_input))
