import pandas as pd 
# import streamlit as st
import plotly.graph_objs as go
import sys
sys.stdout.reconfigure(encoding='utf-8')

# sys.stdout.reconfigure(encoding='utf-8')
# on_bad_lines='skip', encoding='utf-8')

df = pd.read_csv('Bildung.csv', sep=';') 

# avoid NaNs in result
cols = ['germans_male', 'foreigns_male', 'germans_female', 'foreigns_female']
df[cols] = df[cols].fillna(0)

df['total_students'] = (
    df['germans_male']
  + df['foreigns_male']
  + df['germans_female']
  + df['foreigns_female']
)

df['total_students'] = (
    df['germans_male']
  + df['foreigns_male']
  + df['germans_female']
  + df['foreigns_female']
)

# print(df.columns.tolist())
# winter = df[df['semester'].str.upper().str.startswith('WS', na=False)]

totals_by_ws = df.groupby('semester', as_index=True)['total_students'].sum()


best_ws   = totals_by_ws.idxmax()
max_count = totals_by_ws.max()

print(f"The semester {best_ws} had the most students with a total of {max_count} students")

df['international_students'] = (
  + df['foreigns_male']
  + df['foreigns_female']
)

studienBereich = df.groupby('program')['total_students'].sum()

top_program         = studienBereich.idxmax()
top_program_count   = int(studienBereich.max())

print(f"Program with the most foreign students: {top_program!r}") 
'''
  the !r tells Python to call repr(value) instead of str(value). That means:
str(value) → a “pretty” or user‑friendly string
repr(value) → a string that, as much as possible, looks like valid Python code and shows quotes and escape sequences
'''
print(f" Total foreignstudent headcount: {top_program_count:,}")
'''
 the :, is the format‐spec for thousand separators
Inside the {} of an f‑string, anything after a : is a format spec. 
Putting a comma in there tells Python to insert commas as thousands separators for numbers.
'''

top5 = studienBereich.nlargest(5)
print(top5)

df['total_female'] = df['germans_female']+df['foreigns_female']

femaleMajority = df.groupby('program', as_index=True)[['total_female', 'total_students']].sum()
femaleMajority['female_percentage'] = round(femaleMajority['total_female']/femaleMajority['total_students']*100, 2)
# print(femaleMajority.max())
# print(femaleMajority.idxmax())
print(femaleMajority.sort_values('female_percentage',ascending=False))
print(f" Total foreign students headcount: {top_program_count:,}")
#df['female_percentage'] = df['total_female']+df['total_students']

# top_female_program         = femaleMajority.idxmax()
# top_female_program_count   = int(femaleMajority.max())
# print(top_female_program)
# print(top_female_program_count)


