from pydantic import BaseModel
from typing import List

class AccessibilityTestModel(BaseModel):
    name: str
    objectives: List[str]
    desired_automation_framework: str

# Example usage
data = {
    'name': 'Visual Impairment',
    'objectives': [
        'To verify that all images have descriptive alt text for visually impaired users.',
        'To verify that the website has sufficient color contrast.',
        'To verify that the website is keyboard accessible.',
        'To verify that the website has no flickering content.'
    ],
    'desired_automation_framework': 'Selenium'
}

test_model = AccessibilityTestModel(**data)
print(test_model)
