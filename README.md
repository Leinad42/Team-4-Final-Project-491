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

### Revised Questions for Testing ###
* Among referred students, is a higher proportion of scheduled tutoring sessions attended associated with improved grades in the tutored subject?
  - Goal: Examine the relationship between tutoring attendance and academic outcomes while accounting for prior achievement and referral timing.
* Among referred students, do bus-riders attend a smaller proportion of scheduled tutoring sessions than non-bus riders?
  - Goal: Investigate whether bus-rider status is associated with reduced tutoring attendance.
* Does the relationship between tutoring attendance and subsequent grades differ across schools with different economic disadvantage rates?
  - Goal: Examine differences across school contexts without assuming differences in tutoring funding or quality.
* Among referred students with similar prior achievement and tutoring attendance, are higher course absences associated with higher subsequent failure rates?
  - Goal: Examine whether missed class periods help explain academic outcomes separately from missed tutoring sessions.

### Files for Milestone 1 Check ###
- `cleaning_run.log ` - text record of what happened when `clean_data.py` ran.
- `cleaned` - A folder containing all the cleaned datasets once `clean_data.py` has been run
- `clean_data.py` — Loads the original datasets, fixes formatting and inconsistencies, handles missing values, removes duplicates, and saves cleaned datasets. Prints row counts and reasons for each cleaning step.
- `cleaning_run.log` — Saved output from the cleaning script showing each step, row counts before and after, and reasons for changes.
- `exploration.ipynb` — Exploration notebook with summary statistics, visualizations, and interpretations. Compares failure rates between tutoring attendees and students with no recorded attendance, both overall and within prior-GPA groups.
- `exploration.py` — Contains the calculations and plotting functions used by the exploration notebook. Keep this file alongside the notebook.
- `make_notebook.py` — Generates the exploration notebook structure. Running it replaces the notebook and clears its saved outputs; it is not needed for normal analysis.
- `students_cleaned.csv` — Cleaned student records used for analysis. Missing prior-year GPAs are preserved rather than filled with guessed values.
- `hypothesis.md` — Contains our specific problem that we narrowed from our topic and the two hypotheses we will be testing along with how we will test them.

### Files for Milestone 2 Check ###
- `hypothesis1_experements.ipynb` — Contains the experiments we ran to test our first hypothesis
- `hypothesis2_experements.ipynb` — Contains the experiments we ran to test our second hypothesis
- `hypothesis1_outputs` — A folder containing the outputs of our experiments pertaining to our first hypothesis once `hypothesis1_experiments.ipynb` has been run
- `hypothesis2_outputs` — A folder containing the outputs of our experiments for our first hypothesis once `hypothesis2_experements.ipynb` has ran
- `analysis_outputs` — A folder that contains the analysis of our initial outputs

## Reproducing the cleaning, exploration, and Milestone 2 experiments

### Environment and supplied data

Open the project folder as the working directory and use the same Python interpreter for terminal commands and notebook execution. The recorded experiments used Python 3.14.7, NumPy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, and MLflow 3.18.0. The output folders contain `config.json` files with package versions, settings, and SHA-256 fingerprints of the cleaned inputs.

Install dependencies in your chosen Python environment if they are not already available:

```powershell
python -m pip install numpy==2.5.4 pandas==3.1.1 scikit-learn==1.9.1 mlflow==3.18.0 matplotlib scipy joblib ipykernel nbformat
```

This command does not create a virtual environment. In the notebook editor, select the corresponding Python kernel. The scripts also support a local `.python_packages` directory; if present, its packages can take precedence, so verify the versions actually imported against the recorded configurations.

To reproduce cleaning from the original district exports, place these supplied files in the project folder: `schools.csv`, `school_calendar.csv`, `students.csv`, `courses.csv`, `sections.csv`, `term_grades.csv`, `tutors.csv`, `tutoring_referrals.csv`, and `tutoring_sessions.csv` (or `tutoring_sessions.csv.gz`). Do not append the overlapping sample exports. Alternatively, specify their location:

```powershell
python clean_data.py --input-dir "C:\path\to\district_exports" --output-dir cleaned
```

With the original exports in the project folder, `python clean_data.py` is sufficient. It prints cleaning counts and reasons and writes the cleaned tables, audit, quarantined rows, and missingness report to `cleaned/`. The experiments can also be run directly from the supplied cleaned tables; their input fingerprints must match the recorded inputs.

### Exploration

Open `exploration.ipynb` from the project folder and run its cells in order. It calls `exploration.py`, displays summary tables and figures, and writes supporting CSVs and images to `analysis_outputs/`. Saved notebook outputs can be reviewed without running any cells.

### Course MLflow connection

The tracking server is `http://10.0.100.20:5000`. Use campus network access or the course WireGuard VPN with a route to that address. Browser access alone does not verify artifact transfers; each experiment notebook checks authentication and artifact upload/download before fitting models.

Run the notebook's imports/setup and connection cells, then enter your course username and password at the prompts. Do not put credentials in notebook source or committed files. Use the original experiment names when reviewing or refreshing existing records:

- Hypothesis 1: `Tutoring_Paradox_Hypothesis1`
- Hypothesis 2: `hypothesis2` (enter this explicitly; the notebook's suggested default is different).

### Running the hypothesis experiments

For a fresh reproduction, use a separate copy of the project with the same code and cleaned inputs, without pre-existing `hypothesis1_outputs/` or `hypothesis2_outputs/` directories. Retain the submitted outputs unchanged in the original copy. Use separately named MLflow experiments for the reproduction so its new run IDs can be distinguished from the submitted runs.

1. Run `hypothesis1_experiments.ipynb` in order. It constructs student-subject records, generates the fixed student-grouped development/test split and three validation folds, compares logistic Models A and B, estimates attendance uncertainty with 200 student bootstraps, selects by mean validation log loss, scores the selected model on the final test once, and exports the run table.
2. Run `hypothesis2_experiments.ipynb` in order after H1 has generated its output files. It verifies the same cleaned inputs and reuses H1's exact split/fold assignments. It compares a mean baseline with linear Models A and B using validation MAE, estimates the adjusted bus-rider attendance difference with student-clustered standard errors, scores the selected model once on the final test, and exports runs and a written summary.
3. Save both notebooks after execution so their numeric results and figures remain visible. Random seed 4913 and the pre-term-3 cutoff of February 18, 2026 are fixed. Preprocessing is fitted on training data only. All subject records for a student remain in the same partition/fold.

H2's `uncertainty_method_revision.json` documents why student-clustered CR1 standard errors replaced the interrupted bootstrap procedure. The older H2 configuration's `bootstraps` field describes the original plan; the revision file and clustered result identify the final uncertainty method. Historical bootstrap runs are not combined with the final clustered confidence interval.

### Reviewing or refreshing the submitted results

The `hypothesis1_outputs/` and `hypothesis2_outputs/` folders contain the split manifests, configurations, model files, validation results, hypothesis verdicts, final-test results, and exported `mlflow_run_table.csv` files. H2 also includes a validation summary, descriptive comparisons, uncertainty-method revision, clustered interval figure, and results summary.

Do not rerun the final-test cells in the submitted workspace. Each `final_test_started.json` file protects the once-only test evaluation. Do not delete these markers simply to repeat a score. Saved outputs can be read without training or server access. To refresh only a run-table export after a kernel restart, run imports/setup, log into the correct experiment, and run the final export cell; training and final testing are unnecessary.

If the H2 clustered-association upload is interrupted, reconnect to the same experiment and rerun that cell. Its separate `clustered_association_checkpoint.json` preserves the completed fit and result for reuse. The earlier bootstrap checkpoints are historical recovery files, not the final uncertainty evidence.

Numerical comparisons should use the saved metric tables and recorded settings; MLflow assigns new run IDs on new runs. Confirm that IDs in the submitted validation and final-test tables appear in their corresponding exported run table. A matching score alone does not establish matching run provenance. Both analyses are observational and do not establish causal effects.



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


