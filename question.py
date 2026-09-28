class Question:
    def __init__(self, name, type, intruction, criteria):
        self.name = name
        self.type = type
        self.intruction = intruction
        self.criteria:dict = criteria
        self.probabilities = None
        self.answer = None
        self.confidence = None

    def to_dict(self):
        return {
            "type": self.type,
            "instruction": self.intruction,
            "criteria": self.criteria
        }
    