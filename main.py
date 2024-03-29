import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv() 

logging.basicConfig(level=logging.INFO)

app = FastAPI()

genai.configure(api_key=os.getenv("MANIDEEP_GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name = "gemini-pro")

class UrlObjectModel(BaseModel):
    url: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_test_cases (html_content):
    
    test_cases_generated_output = """{
"message": []
"personas": [
    {
    "name": "[Persona]",
    "test_cases": [
        {
        "id": 1,
        "objective": "[Objective of Test Case 1]",
        "preconditions": "[Preconditions for Test Case 1]",
        "steps": [
            "[Step 1 description]",
            "[Step 2 description]",
            ...
        ]
        },
        {
        "id": 2,
        "objective": "[Objective of Test Case 2]",
        "preconditions": "[Preconditions for Test Case 2]",
        "steps": [
            "[Step 1 description]",
            "[Step 2 description]",
            ...
        ]
        },
        ...
    ]
    },
    ...
]
}"""

    
    test_cases_not_generated_output = """{
  "messages": [
    {
      "type": "ERROR",
      "detail": "ERROR occured"
    }
  ],
  "personas": []
}"""

    user_input = f"""Analyze the provided website's HTML code and identify the personas for which ADA test cases are required based on the website's content and structure. Generate comprehensive test cases only for the relevant personas in the specified output format.

                    Output JSON Format (if test cases are generated):
                    {test_cases_generated_output}
                    
                    Output JSON Format (if no test cases are generated or no applicable personas):
                    {test_cases_not_generated_output}

                    Website HTML:
                    ### {html_content} ###

                    Please ensure that the generated test cases cover all relevant accessibility scenarios for the identified personas based on the website's HTML structure and content. If a particular persona is not applicable or relevant based on the analysis, do not include test cases for that persona.
                    """
    
    
    prompt = [
    "You are a professional ADA (Americans with Disabilities Act) tester with 10 years of experience in accessibility testing for visual, auditory, motor, cognitive, and neurological impairments. You can write comprehensive ADA test cases by analyzing a website's HTML code and considering different personas with disabilities in simple English language.",
    user_input
    ]
    
    response = model.generate_content(prompt)
    return response.text   

@app.post("/send-url/")
async def receive_url(urlObject: UrlObjectModel):

    url = urlObject.url

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error accessing URL: {e}")

    if response.status_code == 200:
        try:
            test_cases = get_test_cases(response.text)
            # Assuming get_test_cases returns a JSON string
            print(test_cases)
            test_cases_json = json.loads(test_cases)
        except json.JSONDecodeError:
            test_cases_json = {"message": "Error decoding JSON response from the model"}
        except Exception as e:
            test_cases_json = {"message": f"An error occurred: {str(e)}"}
    else:
        raise HTTPException(status_code=400, detail="Could not scrape the website. Please send a valid website URL.")
    
    return test_cases_json

@app.get("/hello")

async def hello_world():
    return "Hello World"

