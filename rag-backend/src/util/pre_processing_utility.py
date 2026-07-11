import json
import os

import pandas as pd

from models.enums import InformationTier
from util.config_loader import load_config
from util.metadata_extraction import extract_metadata
from models.activity import ActivityMetadata, Activity

TITLE_ONLY_TEXT_TEMPLATE = "The activity {title} is looking for a volunteer."
TITLE_SOFTSKILL_TEXT_TEMPLATE = "The activity {title} is looking for a volunteer possessing these skills: {skills}."
TITLE_DESC_TEXT_TEMPLATE = "The activity {title}, described by: {description}, is looking for a volunteer."
TITLE_DESC_SOFTSKILL_TEXT_TEMPLATE = ("The activity {title}, described by: {description}, "
                                      "is looking for a volunteer possessing these skills: {skills}.")

config = load_config()

class PreProcessingUtility:
    def __init__(self):
        self.csv_path = config["paths"]["csv"]
        self.json_path = config["paths"]["json"]

        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"File not found: {self.csv_path}")
        try:
            self.df = pd.read_csv(self.csv_path, sep=";")
        except Exception as e:
            raise RuntimeError(f"Error parsing .csv file: {e}")

    # build sencences/text snippets from csv rows
    def process_data(self) -> list[Activity]:
        activities = []
        for row in self.df.itertuples():
            formated_skills = str(row.transversalSkillList).replace("'", '').replace("[", '').replace("]", '')
            extr_metadata: ActivityMetadata = extract_metadata(row.description)

            activity = Activity(
                id=str(row.task_id),
                text_variations={
                    InformationTier.TITLE_ONLY: TITLE_ONLY_TEXT_TEMPLATE.format(
                        title=row.title
                    ),
                    InformationTier.TITLE_SOFTSKILL: TITLE_SOFTSKILL_TEXT_TEMPLATE.format(
                        title=row.title,
                        skills=formated_skills,
                    ),
                    InformationTier.TITLE_DESC: TITLE_DESC_TEXT_TEMPLATE.format(
                        title=row.title,
                        description=row.description,
                    ),
                    InformationTier.TITLE_DESC_SOFTSKILL: TITLE_DESC_SOFTSKILL_TEXT_TEMPLATE.format(
                        title=row.title,
                        description=row.description,
                        skills=formated_skills,
                    ),
                },
                metadata=extr_metadata,
                soft_skills=formated_skills.split(",")
            )
            activities.append(activity)

        self.__save_as_json(activities)
        return activities

    def __save_as_json(self, data: list[Activity]):
        serialized_data = [activity.model_dump() for activity in data]

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(serialized_data, f, indent=4, ensure_ascii=False)

    def load_processed_data(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"File not found: {self.json_path}")

        with open(self.json_path, "r") as f:
            data = json.load(f)

        return [Activity(**item) for item in data]
