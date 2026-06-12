import streamlit as st
import pandas as pd
import plotly.express as px 
import io

@st.cache_data
def load_data(): 
    qc = pd.read_csv('data/qc_curated_2026-06-10.csv')
    org_data = pd.read_csv('data/org_data_taylor.csv')
    codes = pd.read_csv('data/taylor_codes_df.csv')
    return qc, org_data, codes

@st.cache_data
def convert_for_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

qc, org_data, codes = load_data()

st.title('Oslund Code Review')

relevance = st.slider("Choose Relevance Threshold", 0, 4, 2)
specificity = st.slider("Choose Specificity Threshold", 0, 4, 2)
coherence = st.slider("Choose Coherence Threshold", 0, 4, 2)
completeness = st.slider("Choose Completeness Threshold", 0, 4, 2)

filtered_qc = qc[
    (qc['relevance'] >= relevance) &
    (qc['specificity'] >= specificity) &
    (qc['coherence'] >= coherence) &
    (qc['completeness'] >= completeness)
]
filtered_codes = codes[codes['id'].isin(filtered_qc['rand_id_in_org'])]
st.write(f"Number of codes after filtering: {len(filtered_codes)}")

group_by = st.selectbox("Choose what level to group by", options=['code', 'theme', 'topic'], key='group_by')
number_to_see = st.number_input("Choose how many to see", min_value=1, max_value=len(filtered_codes[group_by].unique()), value=min(10, len(filtered_codes[group_by].unique())), step=1, key='number_to_see')
to_plot = filtered_codes.groupby(group_by).size().reset_index(name='count').sort_values('count', ascending=False).head(number_to_see).iloc[::-1]
fig = px.bar(to_plot, y=group_by, x='count', title=f'Count of Codes by {group_by.capitalize()}', orientation='h')
st.plotly_chart(fig, use_container_width=True)

merged_with_org = pd.merge(filtered_codes, org_data, left_on='id', right_on='randomid', how='left')
csv = convert_for_download(merged_with_org)
st.download_button(
    label="Download Filtered Data",
    data=convert_for_download(merged_with_org),
    file_name="merged_filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)