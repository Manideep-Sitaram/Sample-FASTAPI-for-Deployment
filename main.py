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
from typing import List

load_dotenv() 

logging.basicConfig(level=logging.INFO)

app = FastAPI()

genai.configure(api_key=os.getenv("MANIDEEP_GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name = "gemini-pro")

class UrlObjectModel(BaseModel):
    url: str
    
class PersonaTestCase(BaseModel):
    name: str
    objectives: List[str]
    page_weburl: str


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

    user_input = f""" You are an experienced ADA (Americans with Disabilities Act) tester. Your task is to generate comprehensive, action-oriented ADA test cases for the provided website's HTML code, covering all relevant personas, regardless of their applicability.  The generated test cases should be in a format suitable for providing to another LLM, which will then generate the actual test case implementation.
        Analyze the provided website's HTML code and identify the personas for which ADA test cases are required based on the website's content and structure. Generate comprehensive test cases only for the relevant personas in the specified output format.

        Visual Impairment: A user with visual impairment who relies on a screen reader.
        Auditory Impairment: A user with auditory impairment who requires captions and transcripts.
        Motor Impairment: A user with motor impairment who uses voice commands and alternative input methods.
        Cognitive Impairment: A user with cognitive impairment who has difficulty with complex navigation or processing large amounts of information.
        Neurological Impairment: A user with neurological impairment, such as seizure disorders, who is sensitive to flashing or rapidly changing content.

        Output JSON Format (if test cases are generated):
        {test_cases_generated_output}

        Output JSON Format (if no test cases are generated or no applicable personas):
        {test_cases_not_generated_output}

        Website HTML:
        ### {html_content} ###

        Please ensure that the generated test cases cover all relevant accessibility scenarios for the identified personas based on the website's HTML structure and content. If a particular persona is not applicable or relevant based on the analysis, do not include that persona.
                   """
    
    response = model.generate_content(user_input)
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
            logging.info(test_cases)
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

@app.post("/persona_testcases")
async def persona_testcases(persona_testcase: PersonaTestCase):
    
    name,objectives,page_weburl = persona_testcase
    
    output_format = """{
  "feature": "Feature: {feature_description}",
  "background": {
    "given": "Given the user is on the ADA web guidance page: {page_weburl}"
  },
  "scenarios": [
    {
      "scenario": "Scenario: {scenario_name_1}",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "{when_condition_1}"
      ],
      "then": [
        "{then_condition_1}"
      ]
    },
    {
      "scenario": "Scenario: {scenario_name_2}",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "{when_condition_2}"
      ],
      "then": [
        "{then_condition_2}"
      ]
    },
    {
      "scenario": "Scenario: {scenario_name_3}",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "{when_condition_3}"
      ],
      "then": [
        "{then_condition_3}"
      ]
    },
    {
      "scenario": "Scenario: {scenario_name_4}",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "{when_condition_4}"
      ],
      "then": [
        "{then_condition_4}"
      ]
    }
  ]
}
"""
    example_format="""{
  "feature": "Feature: Web Accessibility for Visual Impairment",
  "background": {
    "given": "Given the user is on the ADA web guidance page: https://www.ada.gov/resources/web-guidance/"
  },
  "scenarios": [
    {
      "scenario": "Scenario: Verify Image Alt Text",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "The user checks each image on the page"
      ],
      "then": [
        "All images have descriptive alt text"
      ]
    },
    {
      "scenario": "Scenario: Verify Color Contrast",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "The user checks the color contrast of the text and background"
      ],
      "then": [
        "The color contrast meets the WCAG standards"
      ]
    },
    {
      "scenario": "Scenario: Verify Keyboard Accessibility",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "The user attempts to navigate the page using only the keyboard"
      ],
      "then": [
        "All elements on the page are accessible using the keyboard"
      ]
    },
    {
      "scenario": "Scenario: Verify No Flickering Content",
      "given": [
        "The user navigates to the page"
      ],
      "when": [
        "The user checks for any flickering content on the page"
      ],
      "then": [
        "There is no flickering content on the page"
      ]
    }
  ]
}
# """
    
    prompt= f"""Generate a BDD test case feature file in JSON format for validating the compliance of a web page with the Web Content Accessibility Guidelines (WCAG) standards outlined in the American with Disabilities Act (ADA) for Persona of {name} and the test scenario Objectives: {objectives} for the {page_weburl}.
    Output Format:
    {output_format}
    
    Example Output Format:
    {example_format}
    
    
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)  

