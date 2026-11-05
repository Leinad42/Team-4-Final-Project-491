"""Clean district exports without altering originals. Run: python clean_data.py."""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).parent / '.python_packages'))
import pandas as pd

KEYS = {
    'schools': ['school_code'], 'school_calendar': ['calendar_date'],
    'students': ['student_id'], 'courses': ['course_code'],
    'sections': ['section_id'], 'term_grades': ['student_id', 'course_code', 'term'],
    'tutors': ['tutor_id'], 'tutoring_referrals': ['student_id', 'subject_area'],
    'tutoring_sessions': ['session_id'],
}
ENUMS = {
    'locale': ['City', 'Suburb', 'Town', 'Rural'], 'gender': ['F', 'M'],
    **{c: ['Y', 'N'] for c in ['title_i', 'econ_disadvantaged', 'english_learner', 'iep', 'bus_rider']},
    'subject_area': ['Mathematics', 'English Language Arts', 'Science', 'Social Studies', 'World Languages', 'Health and PE', 'Electives'],
    'attendance': ['Present', 'Absent'], 'referred_by': ['Teacher', 'Counselor', 'Parent', 'Self'],
    'session_day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
    'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'day_type': ['instructional', 'exam', 'holiday', 'break', 'teacher_workday', 'weekend', 'summer'],
    'tutor_type': ['Certified teacher', 'Paraprofessional', 'College tutor'],
    'start_time': ['15:45', '16:35'], 'length': ['year (3 terms)'],
}
RANGES = {'grade_level': (9, 12), 'prior_year_gpa': (0, 4), 'enrollment': (0, None),
          'econ_disadvantaged_pct': (0, 100), 'credits': (0, None),
          'term': (1, 3), 'absences': (0, None), 'minutes': (0, 45)}
INTEGER = {'grade_level', 'enrollment', 'term', 'absences', 'minutes'}


def clean(input_dir=Path('.'), output_dir=Path('cleaned')):
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit, rejected, tables = [], [], {}

    def record(name, step, before, after, reason, changed=0):
        audit.append(dict(file=name, step=step, rows_before=before, rows_after=after,
                          affected_values=int(changed), reason=reason))
        print(f'{name}: {step}: {before:,} -> {after:,} rows; {changed:,} affected values. {reason}')

    def quarantine(name, df, mask, reason):
        mask = mask.fillna(False)
        bad = df.loc[mask].copy()
        if len(bad):
            bad['source_file'] = name
            bad['rejection_reason'] = reason
            rejected.append(bad)
        result = df.loc[~mask].copy()
        record(name, 'quarantine', len(df), len(result), reason, len(bad))
        return result

    for name, key in KEYS.items():
        path = input_dir / f'{name}.csv'
        if not path.exists() and name == 'tutoring_sessions':
            path = input_dir / f'{name}.csv.gz'
        df = pd.read_csv(path, dtype='string', keep_default_na=False, encoding='utf-8-sig')
        record(name, 'load', len(df), len(df), f'Loaded {path.name}; sample exports are overlapping previews, excluded.')
        df.columns = df.columns.str.strip()
        changed = 0
        for c in df:
            old = df[c].copy()
            df[c] = df[c].str.strip().str.replace(r'\s+', ' ', regex=True)
            df[c] = df[c].mask(df[c].str.casefold().isin(['', 'na', 'n/a', 'null', 'none', 'nan']))
            changed += (~old.fillna('<NA>').eq(df[c].fillna('<NA>'))).sum()
        record(name, 'text and missing markers', len(df), len(df), 'Trim whitespace, collapse repeated spaces, standardize explicit missing markers.', changed)
        changed = 0
        for c, values in ENUMS.items():
            if c not in df:
                continue
            old = df[c].copy()
            df[c] = df[c].str.casefold().map({v.casefold(): v for v in values}).astype('string')
            changed += (~old.fillna('<NA>').eq(df[c].fillna('<NA>'))).sum()
        record(name, 'categories', len(df), len(df), 'Normalize category case; unrecognized labels become missing, never guessed.', changed)
        changed = 0
        if 'absences' in df:
            old = df['absences'].copy()
            df['absences'] = df['absences'].str.replace(r'^(\d+) days?$', r'\1', regex=True)
            record(name, 'absence formatting', len(df), len(df), 'Remove day/days suffix from counts; preserve the recorded integer.', old.ne(df['absences']).sum())
        for c, (low, high) in RANGES.items():
            if c not in df:
                continue
            values = pd.to_numeric(df[c], errors='coerce')
            invalid = values.lt(low) | (values.gt(high) if high is not None else False)
            if c in INTEGER:
                invalid |= values.mod(1).ne(0)
            changed += (df[c].notna() & (values.isna() | invalid)).sum()
            df[c] = values.mask(invalid).astype('Int64' if c in INTEGER else 'Float64')
        for c in [c for c in df if c.endswith('_date')]:
            values = pd.to_datetime(df[c], format='ISO8601', errors='coerce')
            changed += (df[c].notna() & values.isna()).sum()
            df[c] = values.dt.strftime('%Y-%m-%d').astype('string')
        record(name, 'types and ranges', len(df), len(df), 'Parse ISO dates and numeric fields; invalid or out-of-range values become missing.', changed)
        for c, pattern in {'student_id': r'\d{7}', 'school_code': r'417\d{3}',
                           'tutor_id': r'E\d{6}', 'teacher_id': r'E\d{6}',
                           'referring_staff_id': r'E\d{6}'}.items():
            if c in df:
                df[c] = df[c].str.upper()
                bad = df[c].notna() & ~df[c].str.fullmatch(pattern, na=False)
                record(name, f'validate {c}', len(df), len(df), 'Malformed identifier becomes missing; preserve identifiers as text.', bad.sum())
                df.loc[bad, c] = pd.NA
        before = len(df)
        df = df.drop_duplicates()
        record(name, 'exact duplicates', before, len(df), 'Keep one copy of identical normalized rows.', before - len(df))
        df = quarantine(name, df, df[key].isna().any(axis=1), 'Missing or invalid natural key.')
        df = quarantine(name, df, df.duplicated(key, keep=False), 'Conflicting natural key: quarantine every conflicting version rather than choose arbitrarily.')
        if name == 'term_grades':
            raw = df.term_grade.str.upper()
            percent = pd.to_numeric(raw.str.removesuffix('%'), errors='coerce')
            valid_numeric = percent.between(0, 100) & percent.mod(1).eq(0) & df.term.isin([2, 3])
            letter = raw.isin(['A', 'B', 'C', 'D', 'F']) & df.term.eq(1)
            df['grade_percent'] = percent.where(valid_numeric).astype('Float64')
            df['failed'] = pd.Series(pd.NA, index=df.index, dtype='boolean')
            df.loc[letter, 'failed'] = raw.loc[letter].eq('F')
            df.loc[valid_numeric, 'failed'] = percent.loc[valid_numeric].lt(60)
            df['term_grade'] = raw.where(letter | valid_numeric)
            record(name, 'grade scale', len(df), len(df), 'Term 1: F fails; terms 2–3: percent <60 fails. No invented letter-grade percentages.', (~(letter | valid_numeric)).sum())
        if name == 'tutoring_sessions':
            expected = df.attendance.map({'Present': 45, 'Absent': 0})
            mismatch = df.attendance.notna() & df.minutes.ne(expected).fillna(True)
            df['minutes_inconsistent'] = mismatch
            df.loc[mismatch, 'minutes'] = expected[mismatch]
            record(name, 'attendance minutes', len(df), len(df), 'Attendance is the source for documented 45/0 minute rule; flag repairs.', mismatch.sum())
        tables[name] = df

    # Validate relationships after all parent tables have been cleaned.
    for name, df in tables.items():
        for col, parent in [('school_code', 'schools'), ('student_id', 'students'),
                            ('course_code', 'courses'), ('section_id', 'sections'), ('tutor_id', 'tutors')]:
            if col in df and name != parent:
                df = quarantine(name, df, df[col].isna() | ~df[col].isin(tables[parent][col]), f'Missing or unknown {col} reference to {parent}.')
        tables[name] = df
    sessions = tables['tutoring_sessions']
    referrals = tables['tutoring_referrals']
    linked = sessions.merge(referrals[['student_id', 'subject_area', 'referral_date', 'session_day', 'start_time', 'tutor_id']],
                            on=['student_id', 'subject_area'], how='left', suffixes=('', '_ref'), validate='many_to_one')
    cal = tables['school_calendar'].set_index('calendar_date')
    date = pd.to_datetime(linked.session_date)
    valid = (linked.referral_date.notna() & linked.session_date.map(cal.day_type).eq('instructional')
             & date.ge(pd.Timestamp('2025-08-18'))
             & date.ge(pd.to_datetime(linked.referral_date) + pd.Timedelta(days=3))
             & date.dt.day_name().eq(linked.session_day)
             & linked.tutor_id.eq(linked.tutor_id_ref) & linked.start_time.eq(linked.start_time_ref))
    # Align merged validation results to the original index.
    tables['tutoring_sessions'] = quarantine('tutoring_sessions', sessions, pd.Series(~valid.fillna(False).to_numpy(), index=sessions.index), 'Session violates calendar, referral, tutor or weekly schedule rules.')
    for name, df in tables.items():
        for c in ['prior_year_gpa', 'attendance', 'failed']:
            if c in df:
                df[f'{c}_missing'] = df[c].isna()
        df.to_csv(output_dir / f'{name}.csv', index=False)
        record(name, 'save / missing policy', len(df), len(df), 'Keep missing optional values; exclude unknown outcomes only from relevant analyses. No GPA/outcome imputation.')
    pd.DataFrame(audit).to_csv(output_dir / 'cleaning_audit.csv', index=False)
    if rejected:
        pd.concat(rejected, ignore_index=True, sort=False).to_csv(output_dir / 'quarantined_rows.csv', index=False)
    else:
        pd.DataFrame(columns=['source_file', 'rejection_reason']).to_csv(output_dir / 'quarantined_rows.csv', index=False)
    pd.DataFrame([{'file': name, 'column': c, 'rows': len(df), 'missing': int(df[c].isna().sum())}
                  for name, df in tables.items() for c in df]).to_csv(output_dir / 'missingness.csv', index=False)
    return tables


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=Path(__file__).parent)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).parent / 'cleaned')
    args = parser.parse_args()
    clean(args.input_dir, args.output_dir)
