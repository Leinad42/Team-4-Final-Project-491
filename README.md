# Team-4-Final-Project-491

Team Members: Nicholas Daniel, Joshua Ramachandran, William Powala
Topic: Education: The Tutoring Paradox

Files for Milestone 1 Check:

problem_questions_goals.markdown - Contains our interpretation or the problem statement along with 4 questions and the goals they seek to accomplish

Inputs and Graph.png - Our graph derived from the domain-expert inputs given with our topic

### Data Cleaning Log ###

* Students Data Set (students.csv)
    - Issues: 5 students had district entry dates before their birth dates
    - Fix: Removed the students with conflicting birth and district entry dates, leaving us with 39,995 students remaining
    - Reason: The conflicting birth and district entry dates created an impossible timeline. We chose to exclude them rather than keep the conflicting records bc those 5 had no verified corrections which was optimal over guessing the correct dates

    * Note: Missing GPAs reflect unavailable prior-school transcripts for students who entered the district in 2025, not necessarily an absence of a prior-year GPA.

* Term Grades Data Set (term_grades.csv)
    - Issues: 11,030 absence values contained text such as "2 days"
    - Fix: Standardized all absences to integers such as 2
    - Reason: Keep the formatting consistent

* Tutoring Sesssions Data Set (tutoring_sessions.csv)
    - Issues: 2,480 duplicate tutoring sessions were detected (i.e multiple sessions with the same ID), 20,623 subject labels had unneccessary whitespace, 42 records marked "Present" had inconsistent minutes
    - Fix: Deleted the duplicate sessions and trimmed the white space so subjects match correctly, set minutes to 45 assuming a student attended
    - Reason: To prevent inflated number of sessions, make the data set more readable

* The other csv files did not require any corrections
