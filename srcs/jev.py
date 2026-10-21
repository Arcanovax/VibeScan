import json
import requests
from .question import Question, QUESTIONS


class Jev:

    def __init__(self, api_key):
        self.api_key = api_key
        self.questions: dict[str, Question] = {}
        for question in QUESTIONS:
            self.questions[question.name] = question

    def get_response(self, questions, content):
        questions_json = {
            name: question.to_dict()
            for name, question in questions.items()
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
        return response

    def scan(self, content: str):
        response = self.get_response(self.questions, content)
        answers = response.json().get("answers", {})

        results = {}

        for name, answer in answers.items():

            question = self.questions[name]

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

    def get_final_score(self, report):
        name = "final_answer"
        response = self.get_response({name: Question(
                name="narrating_comments",
                type="score",
                intruction=(
                    report
                ),
                criteria=[
                    "it's made by a human",
                    "it's made with ia or helped by ia",
                ],
            )}, report)

        score = response.json().get("answers", {}).get(name).get('score')
        return score
