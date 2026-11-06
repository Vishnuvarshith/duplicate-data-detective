import re
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Duplicate Data Detective", page_icon="🕵️", layout="wide")

st.title("🕵️ Duplicate Data Detective")
st.write("Upload a CSV file to find duplicate email addresses and names, review the records, and download a cleaned file.")

def normalize_email(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()

def normalize_name(value):
    if pd.isna(value):
        return ""
    # Ignore capitalization and repeated spaces when comparing names.
    return re.sub(r"\s+", " ", str(value).strip()).casefold()

def find_column(columns, requested):
    """Find a likely matching column without depending on capitalization."""
    lookup = {str(col).strip().casefold(): col for col in columns}
    for candidate in requested:
        if candidate in lookup:
            return lookup[candidate]
    return None

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("No file uploaded yet. You can try the sample file in the project’s sample_data folder.")
    st.subheader("What this app does")
    st.markdown(
        "- Finds repeated email addresses (case-insensitive).\\n"
        "- Finds repeated names (ignores capitalization and extra spaces).\\n"
        "- Shows duplicate rows and summary metrics.\\n"
        "- Removes duplicate records and lets you download the cleaned CSV."
    )
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Could not read this CSV file: {error}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV has no records.")
    st.stop()

st.subheader("1. Preview your data")
st.caption(f"{len(df):,} rows · {len(df.columns):,} columns")
st.dataframe(df.head(20), use_container_width=True)

email_col = find_column(df.columns, ["email", "e-mail", "email address"])
name_col = find_column(df.columns, ["name", "full name", "fullname", "customer name"])

st.subheader("2. Choose columns")
column_names = ["— None —"] + list(df.columns)

email_choice = st.selectbox(
    "Email column",
    column_names,
    index=column_names.index(email_col) if email_col in df.columns else 0,
)
name_choice = st.selectbox(
    "Name column",
    column_names,
    index=column_names.index(name_col) if name_col in df.columns else 0,
)

email_col = None if email_choice == "— None —" else email_choice
name_col = None if name_choice == "— None —" else name_choice

if email_col is None and name_col is None:
    st.warning("Select at least an email column or a name column to detect duplicates.")
    st.stop()

email_duplicate_mask = pd.Series(False, index=df.index)
name_duplicate_mask = pd.Series(False, index=df.index)

if email_col:
    email_keys = df[email_col].map(normalize_email)
    email_duplicate_mask = email_keys.ne("") & email_keys.duplicated(keep=False)

if name_col:
    name_keys = df[name_col].map(normalize_name)
    name_duplicate_mask = name_keys.ne("") & name_keys.duplicated(keep=False)

any_duplicate_mask = email_duplicate_mask | name_duplicate_mask
duplicate_rows = df.loc[any_duplicate_mask].copy()

st.subheader("3. Duplicate detection")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total records", f"{len(df):,}")
c2.metric("Duplicate email rows", f"{int(email_duplicate_mask.sum()):,}")
c3.metric("Duplicate name rows", f"{int(name_duplicate_mask.sum()):,}")
c4.metric("Rows flagged", f"{int(any_duplicate_mask.sum()):,}")

duplicate_percentage = (any_duplicate_mask.sum() / len(df)) * 100
st.metric("Duplicate percentage", f"{duplicate_percentage:.2f}%")

if any_duplicate_mask.any():
    st.warning("Potential duplicate records are shown below. Check them before using the cleaned file.")
    st.dataframe(duplicate_rows, use_container_width=True)
else:
    st.success("No duplicates were detected using the selected columns.")

if email_col:
    with st.expander("Email duplicate summary"):
        email_summary = (
            df.assign(_normalized_email=df[email_col].map(normalize_email))
              .query("_normalized_email != ''")
              .groupby("_normalized_email")
              .size()
              .reset_index(name="Occurrences")
              .query("Occurrences > 1")
              .sort_values("Occurrences", ascending=False)
              .rename(columns={"_normalized_email": "Normalized email"})
        )
        st.dataframe(email_summary, use_container_width=True)

if name_col:
    with st.expander("Name duplicate summary"):
        name_summary = (
            df.assign(_normalized_name=df[name_col].map(normalize_name))
              .query("_normalized_name != ''")
              .groupby("_normalized_name")
              .size()
              .reset_index(name="Occurrences")
              .query("Occurrences > 1")
              .sort_values("Occurrences", ascending=False)
              .rename(columns={"_normalized_name": "Normalized name"})
        )
        st.dataframe(name_summary, use_container_width=True)

st.subheader("4. Clean the data")
st.write("Choose how duplicate records should be identified. The app keeps the first matching record.")
dedupe_options = []
if email_col:
    dedupe_options.append("Email")
if name_col:
    dedupe_options.append("Name")
dedupe_options.append("Entire row")

dedupe_by = st.radio("Remove duplicates based on", dedupe_options, horizontal=True)

if dedupe_by == "Email":
    keys = df[email_col].map(normalize_email)
    keep_mask = keys.eq("") | ~keys.duplicated(keep="first")
elif dedupe_by == "Name":
    keys = df[name_col].map(normalize_name)
    keep_mask = keys.eq("") | ~keys.duplicated(keep="first")
else:
    keep_mask = ~df.duplicated(keep="first")

cleaned_df = df.loc[keep_mask].copy()
removed_count = len(df) - len(cleaned_df)

m1, m2, m3 = st.columns(3)
m1.metric("Cleaned records", f"{len(cleaned_df):,}")
m2.metric("Records removed", f"{removed_count:,}")
m3.metric("Records remaining", f"{len(cleaned_df):,}")

st.dataframe(cleaned_df.head(20), use_container_width=True)

csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download cleaned CSV",
    data=csv_bytes,
    file_name="cleaned_data.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption("Note: duplicate detection is based on the columns and matching rules you select. Review results before deleting important records.")
