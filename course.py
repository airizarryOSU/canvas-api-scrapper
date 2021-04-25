# Filename    : course.py
# Date        : 2021-04-07
# Description : Authenticates the Canvas API with a specific API token and
#               downloads all Exploration pages as txt files in a directory
#               named after the course's ID number in the current working
#               directory.
# Config      : create a local.env file: export canvas_token=xxxxxxxxxyyyyyyyyyzzzzzzzz,
#               in python terminal or terminal, then run: source local.env
# Usage       : python course.py course_id
# Note        : course_id is the integer that appears in html path for the canvas page
#               e.g. (https://oregonstate.instructure.com/courses/1811085)

import json
import os
import sys
from bs4 import BeautifulSoup

import requests


class Course:
    """Class to interact with a Canvas Course through the Canvas REST API."""

    EXPLORATION_SEARCH_STRING = "exploration"
    CANVAS = "canvas.oregonstate.edu"

    # Use 2 digit places since each quarter is at most 10 weeks long.
    TXT_FILE_BASE_NAME = "{}_module_{:02d}_{}.txt"

    def __init__(self, course_id, canvas_token_environment_variable="canvas_token"):
        """Create new object of type Course and find its exploration pages.

        Parameters
        ----------
        course_id: str
            Numerical course ID string for the OSU course.

        canvas_token_environment_variable: str
            Name of environent variable storing API token user.
        """
        self.canvas_token = os.environ.get(canvas_token_environment_variable)
        self.course_id = course_id
        self.explorations = []  # 2D list of Exploration page dictionaries.
        self.find_exploration_pages()

    def request_from_api(self, url_to_request):
        """Make an authenticated call to Canvas API."""
        return json.loads(
            requests.get(
                url_to_request,
                headers={"Authorization": f"Bearer {self.canvas_token}"}
            ).text
        )

    def find_exploration_pages(self):
        """Populate self.explorations.

        Adds any exploration pages found as elements of a 2D list where each
        row corresponds to the module the exploration was found.

        Returns
        -------
        None

        """
        for module_number, module in enumerate(self.get_module_list()):
            self.explorations.append([])
            self.get_explorations_for_module(module_number, module)

    def get_module_list(self):
        """Get list of all module dictionaries for course.

        Module dictionaries can be used for navigating to each module's items.
        """
        URL = f"https://{self.CANVAS}/api/v1/courses/{self.course_id}/modules"
        return self.request_from_api(URL)

    def get_module_items(self, module):
        """Get list of items in the module

        Warning
        -------
        API does not to return module 10's items.

        Parameters
        ----------
        module: dict
            Module to search.

        Returns
        -------
        list
            List of module item dictionaries.
        """
        return self.request_from_api(module["items_url"])

    def get_explorations_for_module(self, module_number, module):
        """Find all exploration pages in module and add them to the module_number
        row of member self.explorations.

        Parameters
        ----------
        module_number: int
            Number corresponding to the module. "Getting Started" module has
            module_number equal to 0.
        module: dict
            Module dictionary to search for items.

        Returns
        -------
        None

        """
        for item in self.get_module_items(module):
            if self.EXPLORATION_SEARCH_STRING in item["title"].lower():
                print(f"Found: '{item['title']}'")
                self.explorations[module_number].append(item)

    def download_all_explorations_to_txt(self, directory=None):
        """Downloads all explorations to specified directory.

        Parameters
        ----------
        directory: str
            Creates directory if non-existent. If None, then creates a
            directory with same name as self.course_id and saves file there.

        Returns
        -------
        None

        """
        # Default location.
        if directory is None:
            directory = os.path.join(os.path.curdir, self.course_id)

        # Check paths.
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                raise FileExistsError("Specified path exists and is not directory.")
        else:
            os.mkdir(directory)

        for module_num, row in enumerate(self.explorations):
            for exploration in row:
                self.write_to_txt(module_num, exploration["url"], directory)

    def write_to_txt(self, module_num, url_exploration, directory):
        """Writes given downloaded page to an TXT file in specified directory.

        Parameters
        ----------
        url_exploration: str
            API url for the exploration page.
        directory: str
            Path to directory to save exploration to.

        Returns
        -------
        None

        """
        res = self.request_from_api(url_exploration)
        base_name = self.process_title_into_valid_filename(module_num, res["title"])
        path_name = os.path.join(directory, base_name)

        soup = BeautifulSoup(res["body"], "html5lib")

        with open(path_name, "w") as outfile:
            outfile.write(soup.get_text())
            print(f"Wrote: '{path_name}'")

    def process_title_into_valid_filename(self, module_num, title):
        """Form a reasonably well-behaved base filename for the TXT file.

        Parameters
        ----------
        module_num: int
            Module number of the exploration.
        title: str
            Exploration's title.

        Returns
        -------
        str
            Filename containing the course_id, module_num, and title.
        """
        return (
            (self.TXT_FILE_BASE_NAME.format(course_id, module_num, title))
            .replace(" ", "_")  # Prevent spaces in filename.
            .replace(os.path.sep, "_")  # Prevent accidental directories.
            .lower()  # Only allow lower case filenames.
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise IndexError("USAGE: python course.py course_id [canvas_token]")
    course_id = sys.argv[1]

    course = Course(course_id) if len(sys.argv) < 3 else Course(course_id, sys.argv[2])
    explorations = course.explorations
    course.download_all_explorations_to_txt()
