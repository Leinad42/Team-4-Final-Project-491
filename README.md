# Team-4-Final-Project-491

Team Members: Nicholas Daniel, Joshua Ramachandran, William Powala
Topic: Education: The Tutoring Paradox

Problem Statement: A school is looking to improve its passing rates and the solution was to implement a free tutoring program - students that counselors and parents are referred to the program and the students are free to choose whether or not to participate. While the expectation was that the mentorship improved student grades, the reality was that students were more likely to fail the class they were mentored in. Should the school cut the program’s funding?

### Questions For Testing ###
* Does a higher number of attended tutoring sessions correlate with grade improvement?
  - Goal: Show correlation between time that students were tutored and their grades
* Does being a bus-rider put a student at an advantage or disadvantage?
  - Goal: Show the correlation between a student requiring a bus ride at EOD and grades resulting from tutoring.
* Does a school’s economic disadvantage rate correlate with weaker grade improvements from tutoring?
  - Goal: Show correlation between percentage of economically disadvantaged students in schools and the quality of tutoring they can afford
* Does a large number of absences affect the benefit a student would receive from tutoring
  - Goal: Show correlation between student’s attendance during tutoring and their grades




### Files for Milestone 1 Check ###
- `cleaned` - A folder containing all the cleaned datasets once `clean_data.py` has been run
- `clean_data.py` — Loads the original datasets, fixes formatting and inconsistencies, handles missing values, removes duplicates, and saves cleaned datasets. Prints row counts and reasons for each cleaning step.
- `cleaning_run.log` — Saved output from the cleaning script showing each step, row counts before and after, and reasons for changes.
- `exploration.ipynb` — Exploration notebook with summary statistics, visualizations, and interpretations. Compares failure rates between tutoring attendees and students with no recorded attendance, both overall and within prior-GPA groups.
- `exploration.py` — Contains the calculations and plotting functions used by the exploration notebook. Keep this file alongside the notebook.
- `make_notebook.py` — Generates the exploration notebook structure. Running it replaces the notebook and clears its saved outputs; it is not needed for normal analysis.
- `students_cleaned.csv` — Cleaned student records used for analysis. Missing prior-year GPAs are preserved rather than filled with guessed values.
- `hypothesis.md` — Contains our specific problem that we narrowed from our topic and the two hypotheses we will be testing along with how we will test them.




## AI Use Disclosure

We used OpenAI Codex to generate the initial data-cleaning script,
exploration code, and notebook; execute and check the code, assist
with documentation, and interpreting exploratory results.

The generated files include clean_data.py, exploration.py,
exploration.ipynb, and make_notebook.py. Cleaning logs, cleaned datasets,
charts, and summary tables were produced by running this code against
the supplied district datasets.

The team is responsible for reviewing the code, verifying the results,
and understanding and explaining the submitted work.


