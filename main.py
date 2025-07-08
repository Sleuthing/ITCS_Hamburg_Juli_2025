import pandas as pd 
import plotly.graph_objs as go
import sys

# to handle the output of some characters
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('./Bildung.csv', sep=';') 

# avoid NaNs in result
cols = ['germans_male', 'foreigns_male', 'germans_female', 'foreigns_female']
df[cols] = df[cols].fillna(0)

df['total_students'] = (
    df['germans_male']
  + df['foreigns_male']
  + df['germans_female']
  + df['foreigns_female']
)

####
# task 1: in which wintersemester were there the most students?
totals_students_by_ws = df.groupby('semester', as_index=True)['total_students'].sum()

semester_with_most_students   = totals_students_by_ws.idxmax()
student_count = totals_students_by_ws.max()

fig = go.Figure()

totals_students_by_ws = totals_students_by_ws.reset_index()

fig.add_trace(go.Scatter(
    x=totals_students_by_ws["semester"],
    y=totals_students_by_ws["total_students"],
    mode="lines+markers",
    name="Total Students",
    line=dict(color="blue")
))

fig.add_trace(go.Scatter(
    x=[semester_with_most_students],
    y=[student_count],
    mode="markers+text",
    textposition="top center",
    marker=dict(size=20, color="red", symbol="star"),
    name="Most students per semester"
))

fig.update_layout(
    title="Total Students per Semester",
    xaxis_title="Semester",
    yaxis_title="Total Students",
    legend_title="Legend",
)

fig.show()

####
# task 2: program with the most international students

fig = go.Figure()

df['international_students'] = (
  + df['foreigns_male']
  + df['foreigns_female']
)

studienBereich = df.groupby('program')['international_students'].sum()

foreign_program         = studienBereich.idxmax()
student_count   = int(studienBereich.max())

studienBereich = studienBereich.reset_index()

fig.add_trace(go.Scatter(
    x=studienBereich['program'],
    y=studienBereich['international_students'],
    mode="lines+markers",
    line=dict(color="blue"),
    name="International students per semester"
))

fig.add_trace(go.Scatter(
    x=[foreign_program],
    y=[student_count],
    mode="markers+text",
    textposition="top center",
    marker=dict(size=20, color="green", symbol="star"),
    name="Most international students"
))

fig.update_layout(
    title="Total International Students per Program",
    xaxis_title="Program",
    yaxis_title="Total International Students",
    legend_title="Legend",
)

fig.show()

####
# task 3: the percentage of female students in the program with the most female students

fig = go.Figure()

df['total_female'] = df['germans_female']+df['foreigns_female']

femaleMajority = df.groupby('program', as_index=True)[['total_female', 'total_students']].sum()
femaleMajority['female_percentage'] = femaleMajority['total_female']/femaleMajority['total_students']

max_female_perecentage = femaleMajority['female_percentage'].max()
female_dominated_program = femaleMajority[femaleMajority['female_percentage'] == max_female_perecentage].reset_index()['program'].iloc[0]

femaleMajority = femaleMajority.reset_index()

fig.add_trace(go.Scatter(
    x=femaleMajority['program'],
    y=femaleMajority['female_percentage'],
    mode="lines+markers",
    line=dict(color="blue"),
    name="Female pecentage per prgoram"
))

fig.add_trace(go.Scatter(
    x=[female_dominated_program],
    y=[max_female_perecentage],
    mode="markers+text",
    textposition="top center",
    marker=dict(size=20, color="purple", symbol="star"),
    name="Most female students"
))

fig.update_layout(
    title="Percentage of female students per program",
    xaxis_title="Program",
    yaxis_title="Percentage",
    yaxis_tickformat=".2%",
    legend_title="Legend",
)

fig.show()
