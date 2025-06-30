# 🤖 RAG-based Complaint Handling Chatbot with REST API

## 📌 Objective

Build a **Retrieval-Augmented Generation (RAG)** chatbot integrated with a **REST API** to manage customer complaints by:

- 🗣️ Collecting complaint details via natural conversation
- 🧾 Creating complaints through a RESTful API
- 🔍 Retrieving complaint information by complaint ID
- 📚 Responding with helpful, contextual answers using a knowledge base

---

## 🚀 Key Features

### 🧠 RAG-based Chatbot
- Leverages a custom knowledge base (e.g., FAQs, policies)
- Automatically asks for missing complaint fields
- Returns a complaint confirmation with a unique ID

### 🛠️ Complaint Management API
- **POST `/complaints`** – Create a new complaint
- **GET `/complaints/{complaint_id}`** – Retrieve complaint details
- Input validation (email, phone number, etc.)
- Stores complaint data with a timestamp in a database

---

## 📂 API Endpoints

### 🔹 POST `/complaints`

Create a new complaint by sending user details.

#### 🟢 Request

**URL:**
```
POST http://127.0.0.1:8000/complaints
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Deepak",
  "phone_number": "+919876543210",
  "email": "deepak@example.com",
  "complaint_details": "My order was not delivered even after 7 days."
}
```

#### 🔵 Response

```json
{
  "complaint_id": "f12238d0",
  "message": "Complaint created successfully"
}
```

---

### 🔹 GET `/complaints/{complaint_id}`

Fetch complaint details using the generated complaint ID.

#### 🟢 Request

**URL:**
```
GET http://127.0.0.1:8000/complaints/f12238d0
```

#### 🔵 Response

```json
{
  "complaint_id": "f12238d0",
  "name": "Deepak",
  "phone_number": "+919876543210",
  "email": "deepak@example.com",
  "complaint_details": "My order was not delivered even after 7 days.",
  "created_at": "2025-06-30T03:13:41.337058"
}
```

---

## 💬 Example Chatbot Interaction

```text
User: I want to file a complaint about a delayed delivery.
Bot: I'm sorry to hear about the delay. Please provide your name.
User: Deepak
Bot: Thank you, Deepak. What is your phone number?
User: 1234567890
Bot: Got it. Please provide your email address.
User: deepak@example.com
Bot: Thanks. Can you share more details about the delayed delivery?
User: My order #12345 was supposed to arrive on May 1 but is still not here.
Bot: Your complaint has been registered with ID: XYZ123. You'll hear back soon.

User: Show details for complaint XYZ123.
Bot:
Complaint ID: XYZ123  
Name: Deepak  
Phone: 1234567890  
Email: deepak@example.com  
Details: My order #12345 was supposed to arrive on May 1 but is still not here.  
Created At: 2025-05-08 10:00:00
```

---

## ⚙️ How to Run

Start the FastAPI server using **Uvicorn**:

```bash
uvicorn main:app --reload
```

Access endpoints:

- `POST /complaints` → [http://127.0.0.1:8000/complaints](http://127.0.0.1:8000/complaints)  
- `GET /complaints/{id}` → e.g., [http://127.0.0.1:8000/complaints/f12238d0](http://127.0.0.1:8000/complaints/f12238d0)

---

## 🧰 Tech Stack

| Tool                  | Purpose                              |
| --------------------- | ------------------------------------ |
| **FastAPI**           | REST API backend                     |
| **LangChain**         | Conversational agent & RAG orchestration |
| **HuggingFace**       | Embeddings & Transformers            |
| **SQLite/PostgreSQL** | Complaint data storage               |
| **Gradio**            | Optional chatbot UI                  |
| **Python**            | Core logic and API integration       |

---

## 🙏 Acknowledgments

- **OpenAI**, **Groq API**, and **Hugging Face** – for models and embeddings
- **FastAPI** – modern Python framework for building APIs
- **LangChain** – framework for building LLM-powered agents and chains

---

