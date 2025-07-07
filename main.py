import pandas as pd
import sys

# to handle the output of some characters
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('Bildung.csv', sep=';') 

# avoid NaNs in result
cols = ['germans_male', 'foreigns_male', 'germans_female', 'foreigns_female']
df[cols] = df[cols].fillna(0)


# task 1: in which wintersemester were there the most students?
df['total_students'] = (
    df['germans_male']
  + df['foreigns_male']
  + df['germans_female']
  + df['foreigns_female']
)

total_students_by_ws = df.groupby('semester', as_index=True)['total_students'].sum()

semester_with_most_students   = total_students_by_ws.idxmax()
student_count = total_students_by_ws.max()

print(f"The semester {semester_with_most_students!r} had the most students with a total of {student_count:,} students")

# task 2: which field of study had the most foreign students?
df['international_students'] = (
  + df['foreigns_male']
  + df['foreigns_female']
)

studienBereich = df.groupby('program')['total_students'].sum()

foreign_program = studienBereich.idxmax()
student_count   = int(studienBereich.max())

print(f"The program {foreign_program!r} has the most foreign students, with a total of: {student_count:,} students")

# task 3: how high is the female student percentage in the study field with the most female students
df['total_female'] = df['germans_female']+df['foreigns_female']

femaleMajority = df.groupby('program')[['total_female', 'total_students']].sum()
femaleMajority['female_percentage'] = femaleMajority['total_female']/femaleMajority['total_students']


print(f"The percentage of female students in the program {femaleMajority['female_percentage'].idxmax()!r} -which has the most female students- is: {femaleMajority['female_percentage'].max():.2%}")



