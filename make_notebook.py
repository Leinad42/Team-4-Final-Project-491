"""Build the exploration notebook (execution is a separate, reproducible step)."""
from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md('''# M1 requirement 5: Exploring the tutoring paradox

**Decision:** Should the district cut tutoring funding because participants fail more often?

We describe the headline comparison and repeat it inside prior-year GPA groups, a measure recorded before this school year. The unit is a student. “Attended” means at least one recorded Present session during the year; the comparison is students with no recorded attendance. Referral alone is not attendance. The outcome is at least one failing course-term during the year (F in term 1; below 60 in terms 2–3).

This descriptive analysis cannot establish tutoring's effect. Referrals target students of concern, participation is voluntary, and full-year attendance can occur after an earlier failure. A separate term-3 comparison uses only attendance before term 3.

Run `python clean_data.py` first, then run all cells from this folder. Full CSVs are used; sample files overlap them and must not be appended.'''),
    code('''from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / '.python_packages'))
from IPython.display import display
from exploration import run, rates
tables, students, summaries = run()'''),
    md('## Summary statistics and data quality\nNumeric summaries exclude missing values. Term-1 letters have no numeric percentage and are excluded from percentage summaries. Missing GPA is retained as its own comparison group; no outcomes or GPA values are imputed.'),
    code('''for name in ['student_summary', 'grade_summary', 'attendance_counts']:
    print(name)
    display(summaries[name])
import pandas as pd
audit = pd.read_csv('cleaned/cleaning_audit.csv')
display(audit[['file','step','rows_before','rows_after','affected_values','reason']])
missing = pd.read_csv('cleaned/missingness.csv')
display(missing[missing.missing.gt(0)])'''),
    md('## Headline comparison and comparison within groups\nEach table reports students, known outcomes, failures, unknown outcomes, and failure percentages among known outcomes. An observed F establishes failure; if a student has no observed F and fewer than all expected grades, the outcome stays unknown. Students with unknown attendance and no known Present session form their own exposure category.'),
    code('''display(summaries['overall_failure_rates'])
display(summaries['failure_rates_by_prior_gpa'])
display(summaries['failure_rates_by_bus_rider'])'''),
    md('## Patterns in the observed data'),
    code('''overall = summaries['overall_failure_rates']
if {'Attended', 'No recorded attendance'}.issubset(overall.index):
    gap = overall.loc['Attended','failure_pct'] - overall.loc['No recorded attendance','failure_pct']
    print(f'Overall attendance-minus-no-attendance failure gap: {gap:.2f} percentage points.')
    display(students.groupby('tutoring').prior_year_gpa.agg(['count','mean','median']))
    grouped = summaries['failure_rates_by_prior_gpa'].failure_pct.unstack('tutoring')
    grouped['gap_percentage_points'] = grouped['Attended'] - grouped['No recorded attendance']
    display(grouped)
    print('Positive gaps mean higher observed failure among attendees; negative gaps mean lower failure.')'''),
    md('## Timing sensitivity\nThe outcome below is any term-3 failure. Exposure is any attendance before 2026-02-18, the first day of term 3. Students who only attend later belong to the no-prior-attendance comparison. This avoids using later attendance to explain earlier outcomes, but referral selection and other confounding remain.'),
    code("display(summaries['term3_failure_by_preterm_attendance'])"),
    md('''## Interpretation and limits

In the supplied exports, 69.07% of attendees and 29.96% of students with no recorded attendance had at least one failing course-term, a 39.10 percentage-point gap. After grouping by prior GPA, the gap is 0.95 points for GPA >1–2, 12.45 points for >2–3, and 3.80 points for >3–4. The lowest band has 100% failure in both groups and only three nonattendees. Thus the headline gap shrinks substantially within bands but does not reverse. These results do not establish that tutoring causes harm or that it helps; baseline selection explains part of the observed difference, with other differences unresolved.

Compare the overall gap with the gap in each GPA group. A reversal would support a selection explanation for the headline; mixed or unchanged gaps should be reported as such. Prior GPA distributions show whether attendees started with different achievement. GPA bands are coarse and do not eliminate differences within groups. Missing GPA may reflect unavailable transfer transcripts and should not be treated as average achievement.

Bus-rider groups explore the district's lack of late buses, but bus assignment does not directly measure transport availability. Repeated course grades are collapsed to student outcomes so a student is counted once per comparison. No significance or causal claim is justified by these descriptive comparisons alone. Quarantined records and unknown outcomes may affect the comparison; inspect the audit and missingness tables before drawing conclusions.

The export excludes students who left the district and does not record referral reasons or private tutoring. Retain funding decisions pending a design that accounts for baseline achievement, referral timing, subject and attendance barriers. Figures and summary tables are saved in `analysis_outputs/`.'''),
]
nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
               'language_info': {'name': 'python'}}
nbf.write(nb, Path(__file__).parent / 'exploration.ipynb')
