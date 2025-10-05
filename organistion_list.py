from organisation import Organisation   
from dataclasses import field, asdict
import pandas as pd
import os
from pathlib import Path
from collections import UserList


class OrganistionList(UserList):
    def __init__(self, iterable = None):
        super().__init__(iterable if iterable is not None else [])

    def read_from_csv(self, file: Path):
        """reads from csv file and returns OrganisationList object

        Args:
            file (pathlib.Path): path to csv file
            Returns: OrganisationList object
        """
        if not os.path.exists(file):
            raise FileNotFoundError(f"File {file} does not exist")
        
        df = pd.read_csv(file, keep_default_na=False)
        data = df.values.tolist()

        for row in data:
            org = Organisation(
                organisation_name=row[0],
                organisation_location=row[1],
                contact_number=row[2],
                website=row[3],
                average_review_count=row[4],
                average_review_points=row[5],
                email=row[6] if len(row) > 6 else None
            )
            self.append(org)

    def print(self):
        """prints organistion list as pandas dataframe
        """
        print("Organistion Count: {}".format(len(self)))
        for org in self:
            print(org)

    def dataframe(self):
            """transform organistion list to pandas dataframe

            Returns: pandas dataframe
            """
            data = list(asdict(item) for item in self)
            return pd.json_normalize(data, sep="_")
   
    def check_path_exists(self, directory_path: Path):
        """checks if output directory exists, if not creates it
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def save_to_excel(self, directory_path: Path, filename):
        """saves pandas dataframe to excel (xlsx) file

        Args:
            filename (str): filename
        """
        self.check_path_exists(directory_path)
        file = directory_path.joinpath("{}.xlsx".format(filename))
        self.dataframe().to_excel(file, index=False)

    def save_to_csv(self, directory_path: Path, filename):
        """saves pandas dataframe to csv file

        Args:
            filename (str): filename
        """
        self.check_path_exists(directory_path)
        file = directory_path.joinpath("{}.csv".format(filename))
        self.dataframe().to_csv(file, index=False)