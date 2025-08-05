import pandas as pd 
import streamlit as st
import plotly.graph_objs as go
from plotly import express as px
import json
import sys

st.markdown("""
<style>
[data-testid="stMetric"] {
    text-align: center;
    padding: 12px 0;
    
}

[data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
    align-items: center;
}
            
div[data-testid="stVerticalBlock"]:has(div[data-testid="stDataFrame"]){
    padding-top: 4rem;
}         
</style>
""", unsafe_allow_html=True)

## Utility functions
@st.cache_data(ttl=1800)
def load_data(path,sep):
    return pd.read_csv(path, sep=sep)
 
def get_sum_cols(df,cols):
    return df[cols].sum(axis=1)

def wrap_scatter(x_axis,y_axis,trace_name,trace_color):
    return go.Scatter(
    x=x_axis,
    y=y_axis,
    name=trace_name,
    line=dict(color=trace_color)
    ) 
    
def get_growth_color(enrollment_growth):
    if enrollment_growth <= 0:
        return "red"
    elif enrollment_growth < 0.3:
        return "orange"
    else:
        return "green"
    
def get_student_count(col_name, semester):
    if filtered_df.empty:
        return 0
    return filtered_df[col_name].where(filtered_df['semester'] == semester).dropna().iloc[0]
    
def get_delta_growth(first_value, last_value):
    if first_value == 0:
        if last_value == 0:
            return 0
        return 1 
    return (last_value - first_value) / first_value

def get_coefficent_variance():
    coefficent_variance = filtered_df['total_students'].std() / filtered_df['total_students'].mean()
    return None if pd.isna(coefficent_variance) else coefficent_variance

def get_numberColConfig(label):
        return st.column_config.NumberColumn(
                        label=label, format="localized")

def boldify_text(text):
    return "**"+text+"**"

def get_enrollment_stability_and_color(coefficient_variance):
    def get_stability_color(stability):
        if stability < 0.2:
            return "red"
        elif stability > 0.7:
            return "green"
        else:
            return "orange"
    if coefficient_variance is not None:
        stability = 1/(1+coefficient_variance)
        return f"{stability:.2}", get_stability_color(stability)
    return "No Data", "red"
    
# to handle the output of some characters
sys.stdout.reconfigure(encoding='utf-8')

st.set_page_config(layout="wide")

tab1, tab2, tab3 = st.tabs(["**ITCS Hamburg 2025 Quiz**", "**Dynamic Students Graph**",
                                   "**Germany Student Distribution Map**"])

df = load_data('data/Bildung.csv',';')

# avoid NaNs in result
cols = ['germans_male', 'germans_female', 'foreigns_male', 'foreigns_female']
df[cols] = df[cols].fillna(0)
    
with tab1:
    ####
    # task 1: in which wintersemester were there the most students?
    df['total_students'] = get_sum_cols(df,cols)
    totals_students_by_ws = df.groupby('semester', as_index=True)['total_students'].sum()

    semester_with_most_students   = totals_students_by_ws.idxmax()
    student_count = totals_students_by_ws.max()
    totals_students_by_ws = totals_students_by_ws.reset_index()

    fig = go.Figure()

    fig.add_trace(wrap_scatter(totals_students_by_ws["semester"],totals_students_by_ws["total_students"],
                                "Total Students","blue"))
    
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
        yaxis_title="Total German Students",
        legend_title="Legend",
    )
    st.plotly_chart(fig)

    ####
    # task 2: program with the most international students

    fig = go.Figure()
    
    df['international_students'] = get_sum_cols(df,['foreigns_male','foreigns_female'])

    studienBereich = df.groupby('program')['international_students'].sum()

    foreign_program = studienBereich.idxmax()
    student_count   = int(studienBereich.max())

    studienBereich = studienBereich.reset_index()

    fig.add_trace(wrap_scatter(studienBereich['program'],studienBereich['international_students'],
                                "International students per semester","blue"))

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
        yaxis_title="Total International Students",
        legend_title="Legend",
    )

    st.plotly_chart(fig)

    ####
    # task 3: the percentage of female students in the program with the most female students
    fig = go.Figure()
    df['total_female'] = get_sum_cols(df,['germans_female', 'foreigns_female'])

    femaleMajority = df.groupby('program', as_index=True)[['total_female', 'total_students']].sum()
    femaleMajority['female_percentage'] = femaleMajority['total_female']/femaleMajority['total_students']

    max_female_perecentage = femaleMajority['female_percentage'].max()
    female_dominated_program = femaleMajority[femaleMajority['female_percentage'] == max_female_perecentage].reset_index()['program'].iloc[0]

    femaleMajority = femaleMajority.reset_index()

    fig.add_trace(wrap_scatter(femaleMajority['program'],femaleMajority['female_percentage'],
                                "Female pecentage per prgoram","blue"))

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
        yaxis_title="Female Percentage",
        yaxis_tickformat=".2%",
        legend_title="Legend",
    )
    st.plotly_chart(fig)

with tab2:
    col1, col2 = st.columns([1, 1],gap='medium',vertical_alignment='center') #border=True
    selected_program = col1.selectbox("Choose a program:", df['program'].unique())
    fig = go.Figure()

    semesters = df['semester'].unique()

    start_semester, end_semester = col2.select_slider(
        "Select semester range:",
        semesters[::-1],
        value=(semesters[0], semesters[-1])
    )
    all_states = col1.checkbox("In all states?", value=True)
    if all_states:
        selected_states = df['state_name'].unique()
    else:
        selected_states = col1.multiselect(
            label="Selected states:", options=df['state_name'].unique(), default=df['state_name'].unique(),
        )
    all_unis = col2.checkbox("Across all university types?", value=True)
    if all_unis:
        university_types = df['university_type'].unique()
    else:
        university_types = col2.segmented_control(
            label="Selected university types:", options=df['university_type'].unique(), default=df['university_type'].unique(),
            selection_mode="multi"
        )
            
    filtered_df = df[(df['program'] == selected_program) & (start_semester <= df['semester'])\
                    & (df['semester'] <= end_semester) & (df['state_name'].isin(selected_states))\
                    & (df['university_type'].isin(university_types))]
    filtered_df = filtered_df.groupby('semester')[cols].sum().reset_index()
    filtered_df['total_students'] =  get_sum_cols(filtered_df,cols)
    
    # plotting the student counts
    fig.add_trace(wrap_scatter(filtered_df['semester'],filtered_df['germans_male'],
                                "German Male (DE-M)","blue"))

    fig.add_trace(wrap_scatter(filtered_df['semester'],filtered_df['germans_female'],
                                "German Female (DE-F)","pink"))
    
    fig.add_trace(wrap_scatter(filtered_df['semester'],filtered_df['foreigns_male'],
                                "Foreigns Male (INT-M)","navy"))

    fig.add_trace(wrap_scatter(filtered_df['semester'],filtered_df['foreigns_female'],
                                "Foreigns Female (INT-F)","purple"))

    fig.add_trace(wrap_scatter(filtered_df['semester'],filtered_df['total_students'],
                                "Total students","green"))

    fig.update_layout(
        title=f"Student Trends in {selected_program} within the semesters of {start_semester} and {end_semester}",
        xaxis_title="Semester",
        yaxis_title="Student count",
        legend_title="Legend",
    )
    col1, col2 = st.columns([1,3])
    col2.plotly_chart(fig)
    
    enrollment_stability, stability_color = get_enrollment_stability_and_color(get_coefficent_variance())
    col1.metric(f":{stability_color}[**Stability of enrollment**]", enrollment_stability)
    
    first_semester_total_students = get_student_count('total_students', start_semester)
    last_semester_total_students = get_student_count('total_students', end_semester)
    
    enrollment_growth = get_delta_growth(first_semester_total_students, last_semester_total_students)
    col1.metric(f":{get_growth_color(enrollment_growth)}[**Total Enrollment Growth**]", f"{enrollment_growth:.2%}")
    
    col1_1, col1_2 = col1.columns([1,1])
    col1_3, col1_4 = col1.columns([1,1])
    show_individual_growths = col1.checkbox("Show indivdual metrics of growth?")
    if show_individual_growths:

        DEMa_growth, DEFema_growth, INTMa_growth, INTFema_growth = [get_delta_growth(get_student_count(col_name, start_semester),
                                        get_student_count(col_name, end_semester)) for col_name in cols]
        col1_1.metric(f":{get_growth_color(DEMa_growth)}[**DE-M Growth**]", f"{DEMa_growth:.2%}")
        col1_2.metric(f":{get_growth_color(DEFema_growth)}[**DE-F Growth**]", f"{DEFema_growth:.2%}")
        col1_3.metric(f":{get_growth_color(INTMa_growth)}[**INT-M Growth**]", f"{INTMa_growth:.2%}")
        col1_4.metric(f":{get_growth_color(INTFema_growth)}[**INT-F Growth**]", f"{INTFema_growth:.2%}")
    
    show_dataframe = st.checkbox("Show dataframe?")
    
    if show_dataframe:
        st.dataframe(filtered_df,hide_index=True,column_config={
                    "total_students":  get_numberColConfig("Total Students"),
                    "foreigns_male": get_numberColConfig("Foreigners Male"),
                    "germans_male": get_numberColConfig("German Male"),
                    "foreigns_female": get_numberColConfig("Foreigners Female"),
                    "germans_female": get_numberColConfig("German Female"),
                    "semester": st.column_config.TextColumn(
                        "Semester")
                    })

with tab3:
    st.markdown('## Total students per German state over all semesters and programs')
    col1,col2 = st.columns([3,1.3])
    
    with open("data/2_hoch.geo.json","r", encoding="utf-8") as f:
        deutschland_laender = json.load(f)
    choro_df = df.groupby('state_name')['total_students'].sum().reset_index()

    choro_df.loc[5,'state_name'] = 'Sachsen'

    stateName2Code = {
        feat["properties"]["name"]: feat["properties"]["id"]
        for feat in deutschland_laender["features"]
    }

    choro_df['state_code'] = choro_df['state_name'].apply(lambda name: stateName2Code[name])

    choro = px.choropleth(
        choro_df,
        geojson=deutschland_laender,
        locations="state_code",
        featureidkey="properties.id",
        color="total_students",
        center={"lat": 51.1657, "lon": 10.4515},
        scope="europe",
        hover_name="state_name",
        height=750,
        width=100,
    )

    choro.update_geos(
        fitbounds="locations",
        projection_scale=8.5,
        visible=False,
        bgcolor="rgba(0,0,0,0)"
    )
    
    col2.dataframe(choro_df.sort_values(by="total_students"),
                column_order=("state_name", "total_students"),
                hide_index=True,
                height=590,
                column_config={
                    "state_name": st.column_config.TextColumn(
                        "States",
                    ),
                    "total_students": st.column_config.ProgressColumn(
                        "Total Students",
                        format="%f",
                        min_value=0,
                        max_value=max(choro_df.total_students),
                    )}
                )
    
    col1.plotly_chart(choro)