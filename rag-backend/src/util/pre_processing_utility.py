import json
import os

import pandas as pd

from models.enums import InformationTier
from util.config_loader import load_config
from util.metadata_extraction import extract_metadata
from models.activity import ActivityMetadata, Activity

TIER_TEMPLATES = {
    InformationTier.TITLE_ONLY: "The activity {title} is looking for a volunteer.",
    InformationTier.TITLE_SOFTSKILL: "The activity {title} is looking for a volunteer possessing these skills: {skills}.",
    InformationTier.TITLE_DESC: "The activity {title}, described by: {description}, is looking for a volunteer.",
    InformationTier.TITLE_DESC_SOFTSKILL: ("The activity {title}, described by: {description}, "
                                      "is looking for a volunteer possessing these skills: {skills}."),
    InformationTier.MaT_TITLE_ONLY: "{mat_prefix}\nThe activity {title} is looking for a volunteer.",
    InformationTier.MaT_TITLE_SOFTSKILL: "{mat_prefix}\nThe activity {title} is looking for a volunteer possessing these skills: {skills}.",
    InformationTier.MaT_TITLE_DESC: "{mat_prefix}\nThe activity {title}, described by: {description}, is looking for a volunteer.",
    InformationTier.MaT_TITLE_DESC_SOFTSKILL: ("{mat_prefix}\nThe activity {title}, described by: {description}, "
                                      "is looking for a volunteer possessing these skills: {skills}."),
}

MaT_PREFIX_TEMPLATE = "Metadata: [Region: {region}] [Timeframe: {timeframe}]"

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

    # build sentences/text snippets from csv rows
    def process_data(self) -> list[Activity]:
        activities = []
        for row in self.df.head(20).itertuples():
            formatted_skills = str(row.transversalSkillList).replace("'", '').replace("[", '').replace("]", '')
            extr_metadata: ActivityMetadata = extract_metadata(row.description)

            activity = Activity(
                id=str(row.task_id),
                text_variations={
                    tier: template.format(
                        mat_prefix=MaT_PREFIX_TEMPLATE.format(
                            region=extr_metadata.region,
                            timeframe=extr_metadata.timeframe
                        ),
                        title=row.title,
                        description=row.description,
                        skills=formatted_skills
                    )
                    for tier, template in TIER_TEMPLATES.items()
                },
                metadata=extr_metadata,
                soft_skills=formatted_skills.split(",")
            )
            activities.append(activity)

        self.__save_as_json(activities)
        return activities

    def __save_as_json(self, data: list[Activity]):
        serialized_data = [activity.model_dump(mode="json") for activity in data]

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(serialized_data, f, indent=4, ensure_ascii=False)

    def load_processed_data(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"File not found: {self.json_path}")

        with open(self.json_path, "r") as f:
            data = json.load(f)

        return [Activity(**item) for item in data]
