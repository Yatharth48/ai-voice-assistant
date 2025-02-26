import os
import google.cloud.dialogflow_v2 as dialogflow
from google.oauth2 import service_account

# Load Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS = "C:/Users/Yatharth/ai_voice_assistant/lithe-center-311717-a0bc84c5b67d.json"
credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = dialogflow.IntentsClient(credentials=credentials)

# Your Dialogflow project ID
DIALOGFLOW_PROJECT_ID = "lithe-center-311717"  

def create_intent(display_name, training_phrases, responses):
    """Creates a Dialogflow intent with given training phrases and responses."""
    parent = f"projects/{DIALOGFLOW_PROJECT_ID}/agent"

    training_phrases_parts = [
        dialogflow.types.Intent.TrainingPhrase.Part(text=phrase) for phrase in training_phrases
    ]
    training_phrases = [
        dialogflow.types.Intent.TrainingPhrase(parts=[part]) for part in training_phrases_parts
    ]

    message_text = dialogflow.types.Intent.Message.Text(text=responses)
    message = dialogflow.types.Intent.Message(text=message_text)

    intent = dialogflow.types.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"✅ Intent '{display_name}' created successfully!")

# Define multiple intents with training phrases and responses
intents = [
    {
        "name": "TellJoke",
        "phrases": ["Tell me a joke", "Make me laugh", "Say something funny"],
        "responses": ["Why don’t skeletons fight each other? Because they don’t have the guts!"]
    },
    {
        "name": "WeatherInfo",
        "phrases": ["What's the weather today?", "Tell me the weather", "How's the weather?"],
        "responses": ["I'm unable to check real-time weather, but you can check a weather website like weather.com."]
    },
    {
        "name": "GreetUser",
        "phrases": ["Hello", "Hey there", "Hi"],
        "responses": ["Hi! How can I assist you today?"]
    },
    {
        "name": "Goodbye",
        "phrases": ["Bye", "Goodbye", "See you later"],
        "responses": ["Goodbye! Have a great day!"]
    }
]

# Create each intent
for intent in intents:
    create_intent(intent["name"], intent["phrases"], intent["responses"])
