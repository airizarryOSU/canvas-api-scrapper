# canvas-api-scrapper
Python scrapper for Canvas API

## Filename    
course.py
## Date
2021-04-07
## Description
Authenticates the Canvas API with a specific API token anddownloads all Exploration pages as txt files in a directory named after the course's ID number in the current working directory.
## Config
create a `local.env` file: `export canvas_token=xxxxxxxxxyyyyyyyyyzzzzzzzz`, in python terminal or terminal, then run: `source local.env`
## Usage
`python course.py course_id`
## Note
course_id is the integer that appears in html path for the canvas page e.g. (https://oregonstate.instructure.com/courses/1811085)
