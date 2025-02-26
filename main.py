import os
import json
import logging
from pymongo import MongoClient
from fastapi import FastAPI, Query, Request
from pydantic import BaseModel
from google.oauth2 import service_account
import google.cloud.dialogflow_v2 as dialogflow
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Debug: Print all environment variables to check if MONGO_URI is set
logger.info(f"🔍 ENV VARIABLES: {os.environ}")

# Get MongoDB URI from Environment Variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ ERROR: MONGO_URI environment variable is not set!")

# Connect to MongoDB Atlas
try:
    mongo_client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = mongo_client["ai_voice_assistant"]
    chat_history_collection = db["chat_logs"]
    logger.info("✅ MongoDB Connected Successfully!")
except Exception as e:
    logger.error(f"❌ MongoDB Connection Failed: {str(e)}")

# Initialize FastAPI app
app = FastAPI()

# Load Google credentials from environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials_json:
    credentials_info = json.loads(google_credentials_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
else:
    raise ValueError("❌ ERROR: Google credentials are not set in environment variables!")

session_client = dialogflow.SessionsClient(credentials=credentials)
DIALOGFLOW_PROJECT_ID = "lithe-center-311717"
DIALOGFLOW_LANGUAGE_CODE = "en"

# Define request model
class VoiceInput(BaseModel):
    text: str
    session_id: str

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the AI Voice Assistant API using Dialogflow & MongoDB!"}

@app.post("/process_voice")
async def process_voice(input_data: VoiceInput, request: Request):
    """Process user input with Dialogflow and store chat history in MongoDB"""
    try:
        logger.info(f"Received request: {await request.json()}")
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, input_data.session_id)
        text_input = dialogflow.types.TextInput(text=input_data.text, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(session=session, query_input=query_input)
        ai_message = response.query_result.fulfillment_text
        detected_intent = response.query_result.intent.display_name
        
        chat_log = {
            "session_id": input_data.session_id,
            "timestamp": datetime.utcnow(),
            "user_message": input_data.text,
            "detected_intent": detected_intent,
            "bot_response": ai_message
        }
        chat_history_collection.insert_one(chat_log)
        
        logger.info(f"Response sent: {chat_log}")
        return {"response": ai_message, "intent": detected_intent}
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        return {"error": str(e)}

@app.get("/get_chat_history")
async def get_chat_history(session_id: str, limit: int = Query(10, description="Number of messages to retrieve")):
    """Retrieve past conversations for a specific session_id"""
    try:
        logger.info(f"Retrieving chat history for session_id: {session_id}")
        chat_logs = chat_history_collection.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
        chat_history = [
            {
                "timestamp": log["timestamp"],
                "user_message": log["user_message"],
                "detected_intent": log["detected_intent"],
                "bot_response": log["bot_response"]
            }
            for log in chat_logs
        ]
        logger.info(f"Chat history retrieved: {chat_history}")
        return {"session_id": session_id, "chat_history": chat_history}
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return {"error": str(e)}
