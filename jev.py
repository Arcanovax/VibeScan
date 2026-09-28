import json
import requests
from question import Question


class Jev:

    def __init__(self, api_key):
        self.api_key = api_key
        self.questions: dict[str, Question] = {}
        self.register_questions()

    def register_question(self, question: Question):
        self.questions[question.name] = question

    def scan(self, content: str):
        questions_json = {
            name: question.to_dict()
            for name, question in self.questions.items()
        }

        response = requests.post(
            url="https://api.typesafe.ai/v1/systemone",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "jev-latest",
                "state": content,
                "questions": questions_json,
            }),
        )

        response.raise_for_status()

        answers = response.json().get("answers", {})

        # IMPORTANT :
        # On crée un nouveau dictionnaire pour CE scan.
        results = {}

        for name, answer in answers.items():

            question = self.questions[name]

            # On crée une copie de la Question
            result = Question(
                name=question.name,
                type=question.type,
                intruction=question.intruction,
                criteria=question.criteria,
            )

            result.answer = answer.get("choice")
            result.probabilities = answer.get("probabilities")
            result.confidence = answer.get("confidence")

            results[name] = result

        return results

    def register_questions(self):
        self.register_question(Question(
            name="is_made_by_ai",
            type="choice",
            intruction=(
                "You are an expert at detecting AI-generated code (ChatGPT, Claude, Copilot). "
                "Decide whether this code was written by an AI.\n"
                "Strong AI signals: comments that restate what the line does, uniform full docstrings "
                "on every function, 'Step 1 / Step 2' comments, excessive error handling, "
                "generic names (process_data, result, data), perfectly homogeneous style, emojis in logs.\n"
                "Strong human signals: typos, inconsistent naming, commented-out code, forgotten debug prints, "
                "informal or non-English comments, irregular style.\n"
                "Rules: answer true ONLY if at least 3 strong AI signals are present. "
                "If there are no clear signals, answer false. "
                "Short or simple code is not evidence of AI."
            ),
            criteria={
                "true": "At least 3 strong AI signals are present in the code",
                "false": "Few or no AI signals, or clear human signals are present",
            },
        ))

        self.register_question(Question(
            name="obvious_comments",
            type="choice",
            intruction="Does the code contain comments that merely restate what the line below them does?",
            criteria={
                "true": "Yes, several such comments",
                "false": "No, or very rare",
            },
        ))

        self.register_question(Question(
            name="uniform_docstrings",
            type="choice",
            intruction="Does every function have a complete docstring in the same format (Args/Returns/Raises)?",
            criteria={
                "true": "Yes, all functions",
                "false": "No, inconsistent or missing",
            },
        ))

        self.register_question(Question(
            name="step_comments",
            type="choice",
            intruction="Are there numbered step comments ('Step 1', 'Step 2') or decorative section separators?",
            criteria={
                "true": "Yes",
                "false": "No",
            },
        ))

        self.register_question(Question(
            name="over_defensive",
            type="choice",
            intruction="Is the error handling or input validation excessive for the size and purpose of the code?",
            criteria={
                "true": "Yes, excessive",
                "false": "No, proportionate",
            },
        ))

        self.register_question(Question(
            name="human_traces",
            type="choice",
            intruction="Are there human traces: typos, commented-out code, forgotten debug prints, inconsistent names, casual comments?",
            criteria={
                "true": "Yes",
                "false": "No",
            },
        ))

