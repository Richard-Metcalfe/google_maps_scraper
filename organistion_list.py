from organisation import Organisation   
from dataclasses import field, asdict
import pandas as pd
import os
from pathlib import Path

class OrganisationList:
    """
    holds list of Business Organistion objects and save to both excel and csv
    """
    def __init__(self, directory_path: Path):
        self.output_directory = directory_path
        self.business_list: list[Organisation] = []
    
    def dataframe(self):
        """transform business_list to pandas dataframe

        Returns: pandas dataframe
        """
        return pd.json_normalize(
            (asdict(org) for org in self.business_list), sep="_"
        )

    def check_path_exists(self):
        """checks if output directory exists, if not creates it
        """
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def save_to_excel(self, filename):
        """saves pandas dataframe to excel (xlsx) file

        Args:
            filename (str): filename
        """
        self.check_path_exists()
        self.dataframe().to_excel(f"{self.output_directory}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file

        Args:
            filename (str): filename
        """
        self.check_path_exists()
        self.dataframe().to_csv(f"{self.output_directory}/{filename}.csv", index=False)