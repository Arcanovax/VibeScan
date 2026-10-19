import json
import requests
from .question import Question


class Jev:

    def __init__(self, api_key):
        self.api_key = api_key
        self.questions: dict[str, Question] = {}
        self.register_questions()

    def register_question(self, question: Question):
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

        response.raise_for_status()

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

    def register_questions(self):
        q = self.register_question

        q(Question(
            name="assistant_residue",
            type="choice",
            intruction=(
                "Does the code contain leftovers of a chat assistant's output? Examples: "
                "'Here is the updated code', 'Certainly!', 'As an AI', markdown fences inside the file, "
                "'# rest of the code remains unchanged', '# ... existing code ...', "
                "'# Add your logic here' left as the only body."
            ),
            criteria={
                "true": "Clear chat-assistant residue is present",
                "false": "No such residue",
            },
        ))

        q(Question(
            name="step_comments",
            type="choice",
            intruction=(
                "Are there numbered or sequential step comments ('Step 1', '# 1.', 'First,... Next,... Finally,...') "
                "or decorative section banners (e.g. '# ===== Helpers =====') in code that is not long enough to need them?"
            ),
            criteria={"true": "Yes", "false": "No"},
        ))

        q(Question(
            name="emoji_inside",
            type="choice",
            intruction=(
                "Do log messages, print statements, exceptions or comments contain emojis or "
                "decorative symbols (checkmarks, rockets, warning signs)?"
            ),
            criteria={"true": "Yes", "false": "No"},
        ))

        q(Question(
            name="uniform_docstrings",
            type="choice",
            intruction=(
                "Does every function (including trivial private helpers) have a complete docstring "
                "in the exact same format (Args/Returns/Raises), with wording that reads as templated?"
            ),
            criteria={
                "true": "Yes, all or nearly all, perfectly uniform",
                "false": "No: missing, partial, or varying in format",
            },
        ))

        q(Question(
            name="narrating_comments",
            type="choice",
            intruction=(
                "Do several comments merely restate what the next line already says "
                "(e.g. '# increment counter' above 'counter += 1')?"
            ),
            criteria={
                "true": "Yes, several (3 or more)",
                "false": "No, or one or two at most",
            },
        ))

        q(Question(
            name="over_defensive",
            type="choice",
            intruction=(
                "Is error handling or input validation disproportionate to the size and purpose "
                "of the code (try/except around trivial operations, type checks on every argument, "
                "validation of values that can never be invalid)?"
            ),
            criteria={"true": "Yes, clearly excessive", "false": "No, proportionate"},
        ))

        q(Question(
            name="generic_naming",
            type="choice",
            intruction=(
                "Are most identifiers generic and domain-free (data, result, response, process_data, "
                "handle_request, helper) even where a domain-specific name would be natural?"
            ),
            criteria={"true": "Yes, mostly generic", "false": "No, names reflect the domain"},
        ))



        q(Question(
            name="debug_leftovers",
            type="choice",
            intruction=(
                "Are there forgotten debug prints, commented-out code blocks, dead code, "
                "or unused imports/variables left behind?"
            ),
            criteria={"true": "Yes", "false": "No"},
        ))

        q(Question(
            name="informal_or_typos",
            type="choice",
            intruction=(
                "Are there typos, slang, jokes, frustration ('wtf', 'fix later'), "
                "or comments in a language other than English?"
            ),
            criteria={"true": "Yes", "false": "No"},
        ))

        q(Question(
            name="inconsistent_style",
            type="choice",
            intruction=(
                "Is the style inconsistent in a way that suggests several moments or authors: "
                "mixed naming conventions, mixed quote styles, uneven comment density, "
                "mixed formatting?"
            ),
            criteria={"true": "Yes, noticeably", "false": "No, homogeneous"},
        ))

        q(Question(
            name="obvius_character",
            type="choice",
            intruction=(
                "Does this code contain characters that AI assistants typically produce but people "
                "rarely type on a keyboard? Look in comments, docstrings, string literals and "
                "print or log messages."
            ),
            criteria={
                "true": (
                    "At least one clear case: an em dash (\u2014) or en dash (\u2013) used as punctuation, "
                    "curly quotes (\u2018 \u2019 \u201c \u201d), the ellipsis character (\u2026), arrows (\u2192), "
                    "emojis or symbols (\u2705 \u274c \U0001F680 \u26A0\uFE0F \u2728), or decorative separator "
                    "lines made of box-drawing characters (\u2500\u2500\u2500 or \u2550\u2550\u2550)."
                ),
                "false": (
                    "None of these. Only plain ASCII punctuation (hyphen -, straight quotes, three dots ...) "
                    "and normal accents for the language of the file."
                ),
            },
        ))
