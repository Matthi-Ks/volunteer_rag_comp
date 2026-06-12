import json
import os
import pandas as pd

from pipelines.data.metadata_extraction import extract_metadata

TITLE_ONLY_TEXT_TEMPLATE = ("The activity {title} is looking for a volunteer.")
TITLE_SOFTSKILL_TEXT_TEMPLATE = ("The activity {title} is looking for a volunteer possessing these skills: {skills}.")
TITLE_DESC_TEXT_TEMPLATE = ("The activity {title}, described by: {description}, is looking for a volunteer.")
TITLE_DESC_SOFTSKILL_TEXT_TEMPLATE = ("The activity {title}, described by: {description}, "
                                      "is looking for a volunteer possessing these skills: {skills}.")


class CSVDataUtility:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")
        try:
            self.df = pd.read_csv(self.path, sep=";")
        except Exception as e:
            raise RuntimeError(f"Error parsing .csv file: {e}")

    # build sencences/text snippets from csv rows
    def textify_csv(self):
        textified_data = []
        for row in self.df.head(2).itertuples():
            formated_skills = str(row.transversalSkillList).replace("'", '').replace("[",'').replace("]", '')

            activity = {}
            activity["id"] = row.task_id
            activity["text_variants"] = {}
            activity["text_variants"]["title_only_text"] = TITLE_ONLY_TEXT_TEMPLATE.format(title=row.title)
            activity["text_variants"]["title_softskill_text"] = TITLE_SOFTSKILL_TEXT_TEMPLATE.format(title=row.title,skills=formated_skills)
            activity["text_variants"]["title_desc_text"] = TITLE_DESC_TEXT_TEMPLATE.format(title=row.title, description=row.description)
            activity["text_variants"]["title_desc_softskill_text"] = TITLE_DESC_SOFTSKILL_TEXT_TEMPLATE.format(title=row.title, description=row.description, skills=formated_skills)
            # Todo implement metadata for filtering
            metadata = extract_metadata(row.description)
            activity["metadata"] = metadata.model_dump()

            textified_data.append(activity)

        return textified_data

    def save_as_json(self, data):
        output_path = "../../resources/processed_volunteer_data.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)