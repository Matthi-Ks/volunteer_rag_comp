from models.enums import QuestionVariant

class QueryPreprocessingService:

    # strip input text of unwanted symbols and formating
    @staticmethod
    def query_preprocessing(variations: dict[QuestionVariant,str]) -> dict[QuestionVariant,str]:
        # todo maybe implement regex to only allow a-zA-Z0-9
        for key in variations.keys():
            variations[key] = " ".join(variations[key].lower().strip().split())
        return variations