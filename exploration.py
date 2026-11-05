"""Reusable computations for exploration.ipynb; run to regenerate figures/tables."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.python_packages'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
import pandas as pd
import matplotlib.pyplot as plt


def load():
    return {name: pd.read_csv(ROOT / 'cleaned' / f'{name}.csv',
                             dtype={'student_id': 'string', 'school_code': 'string'})
            for name in ['students', 'term_grades', 'tutoring_sessions', 'tutoring_referrals',
                         'schools', 'courses', 'sections', 'tutors', 'school_calendar']}


def student_comparison(tables, term=None):
    grades, sessions = tables['term_grades'].copy(), tables['tutoring_sessions'].copy()
    if term is not None:
        grades = grades[grades.term.eq(term)]
        # Exposure precedes the start of term 3, avoiding sessions after its outcomes.
        sessions = sessions[sessions.session_date.lt('2026-02-18')]
    # A student with any observed F is a known failure; a student with no F and
    # missing grades is unknown, rather than being silently counted as passing.
    outcomes = grades.groupby('student_id').agg(
        observed_grades=('failed', 'count'), expected_grades=('failed', 'size'),
        any_failure=('failed', 'max'))
    outcomes['any_failure'] = outcomes['any_failure'].astype('boolean')
    expected = 18 if term is None else 6
    unknown = outcomes.any_failure.ne(True) & outcomes.observed_grades.lt(expected)
    outcomes.loc[unknown, 'any_failure'] = pd.NA
    result = tables['students'].merge(outcomes, on='student_id', how='left', validate='one_to_one')
    present = sessions[sessions.attendance.eq('Present')]
    uncertain = set(sessions.loc[sessions.attendance.isna(), 'student_id']) - set(present.student_id)
    result['tutoring'] = result.student_id.isin(present.student_id).map({True: 'Attended', False: 'No recorded attendance'})
    result.loc[result.student_id.isin(uncertain), 'tutoring'] = 'Unknown attendance'
    result['gpa_band'] = pd.cut(result.prior_year_gpa, [-0.01, 1, 2, 3, 4],
                                labels=['0–1', '>1–2', '>2–3', '>3–4']).astype('string').fillna('Missing GPA')
    return result


def rates(frame, groups):
    result = frame.groupby(groups, observed=True, dropna=False).agg(
        students=('student_id', 'size'), known_outcomes=('any_failure', 'count'),
        failures=('any_failure', 'sum'))
    result['unknown_outcomes'] = result.students - result.known_outcomes
    result['failure_pct'] = 100 * result.failures / result.known_outcomes.replace(0, float('nan'))
    return result


def run():
    out = ROOT / 'analysis_outputs'
    out.mkdir(exist_ok=True)
    tables = load()
    students = student_comparison(tables)
    overall = rates(students, ['tutoring'])
    grouped = rates(students, ['gpa_band', 'tutoring'])
    sensitivity = rates(student_comparison(tables, term=3), ['gpa_band', 'tutoring'])
    summaries = {
        'overall_failure_rates': overall, 'failure_rates_by_prior_gpa': grouped,
        'term3_failure_by_preterm_attendance': sensitivity,
        'student_summary': tables['students'][['prior_year_gpa', 'grade_level']].describe(),
        'grade_summary': tables['term_grades'][['grade_percent', 'absences']].describe(),
        'attendance_counts': tables['tutoring_sessions'].attendance.value_counts(dropna=False).to_frame('sessions'),
        'failure_rates_by_bus_rider': rates(students, ['bus_rider', 'tutoring']),
    }
    for name, table in summaries.items():
        table.to_csv(out / f'{name}.csv')
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    overall.failure_pct.plot.bar(ax=axes[0], color='#4477AA', rot=15)
    axes[0].set_title('Any failing course during the year')
    grouped.failure_pct.unstack('tutoring').plot.bar(ax=axes[1], rot=0)
    axes[1].set_title('Same comparison within prior-GPA groups')
    for ax in axes:
        ax.set_ylabel('Students with a failure (%)')
        ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(out / 'failure_comparison.png', dpi=160)
    plt.show()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for group, frame in students.groupby('tutoring'):
        axes[0].hist(frame.prior_year_gpa.dropna(), bins=20, alpha=.55, label=group)
    axes[0].set(xlabel='Prior-year GPA', ylabel='Students', title='Prior achievement and tutoring participation')
    axes[0].legend()
    missing = pd.read_csv(ROOT / 'cleaned' / 'missingness.csv')
    missing['missing_pct'] = 100 * missing.missing / missing.rows
    top = missing[missing.missing.gt(0) & ~missing.column.str.endswith('_missing')].nlargest(12, 'missing_pct')
    axes[1].barh(top.file + '.' + top.column, top.missing_pct)
    axes[1].set(xlabel='Missing (%)', title='Missing values retained after cleaning')
    fig.tight_layout()
    fig.savefig(out / 'gpa_and_missingness.png', dpi=160)
    plt.show()
    fig, ax = plt.subplots(figsize=(9, 4))
    sensitivity.failure_pct.unstack('tutoring').plot.bar(ax=ax, rot=0)
    ax.set(title='Term-3 failures vs attendance before term 3', ylabel='Students with a failure (%)', ylim=(0, 100))
    fig.tight_layout()
    fig.savefig(out / 'term3_sensitivity.png', dpi=160)
    plt.show()
    return tables, students, summaries


if __name__ == '__main__':
    run()
