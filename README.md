# ICF Exam Preparation Quiz App

A simple web-based quiz application using Python and Flask to help preparation for ICF Exam. This app displays multiple-choice questions, provides feedback, and shows the final score.

## Features
- Presents multiple-choice questions one at a time
- Shows feedback after each question, including correct and incorrect answers
- Tracks and displays the total and correct answers
- Shows a final score and an option to restart the quiz

## Questions source
The questions are constructed using the following sources of information:
- Introducing the ICF ACC Credential Exam
- Sample ACC Exam Questions
- ICF Code of Ethics 
- ICF Core Competencies
- ICF Core Competencies Markers
- ICF ETHICS FAQs 
- ICF CORE VALUES

## Setup
### Prerequisites
- Python 3.x
- Flask

### Installation
Clone the repository:

`git clone https://github.com/<your-username/your-repositor>y.git`

Install the required Python packages:

`pip install -r requirements.txt`

## Virtual Environment 
### Create Virtual Environment
`python -m venv venv`
### Activate Virtual Environment
`venv/bin/activate`
`.\venv\Scripts\activate`
### Deactivate Virtual Environment
`deactivate`

## Configuration
Persistent Secret Key:
* For production deployments, it’s crucial to have a persistent secret key to avoid invalidating user sessions when the application restarts.
* Set SECRET_KEY in the environment to ensure stability.
Fallback (Development):
* Generating a random key with os.urandom is useful for local development and testing environments but is not recommended for production.

Always use a fixed, secure secret key in production, stored in a safe place like environment variables or a secret management tool.


## Create the db for production
```python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Usage
Start the Flask server:
`python app.py`

Then go to http://127.0.0.1:5000 in your browser to start the quiz.

## File Overview
* app.py: The main Flask application file, containing the routes and core logic for the quiz application.
* quiz_data.py: Holds the collection of quiz questions, answer options, correct answers, and explanations.
* static/:
  * styles.css: The CSS stylesheet that defines the visual styles for the application.
* templates/:
  * quiz.html: Renders the user interface for displaying the multiple-choice quiz questions and answer options.
  * result.html: Displays the feedback to the user after they submit an answer, indicating if it was correct or incorrect.
  * finish.html: Shows the final score and provides an option to restart the quiz.
* requirements.txt: Lists the Python package dependencies required to run the application.

## Adding New Questions
To add questions, open quiz_data.py and add a dictionary to the quiz list in this format:
```python
{
    "question": "Sample question?",
    "options": {
        "A": "Option 1",
        "B": "Option 2",
        "C": "Option 3",
        "D": "Option 4"
    },
    "answer": "B",
    "explanation": "Explanation for the correct answer."
}
```

## Disclaimer
This mock exam and associated materials are created solely for the author training and educational purposes. This is NOT an official International Coaching Federation (ICF) product or examination. The content provided is based on publicly available information about the ICF ACC credentialing process and should not be considered as a substitute for official ICF study materials, training, or examination preparation resources. 

While every effort has been made to ensure accuracy and alignment with ICF standards, this material:
- Is not endorsed by, affiliated with, or approved by the International Coaching Federation (ICF)
- Has been generated using artificial intelligence to create the exam questions
- Should not be considered a guarantee of success on the actual ICF ACC credentialing exam
- May not reflect the most current ICF standards, competencies, or examination format
- Is to be used at the user's own risk and discretion

Users are strongly encouraged to:
- Refer to official ICF resources and materials 
- Participate in ICF-accredited training programs
- Consult the ICF website for the most up-to-date information
- Verify all information independently

The creator and distributor of this material assume no responsibility or liability for any errors or omissions in the content or for the results obtained from the use of this information.



## License
This project is licensed under the MIT License.