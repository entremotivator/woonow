import streamlit as st
import pandas as pd
import requests
import json
import time
import io  # Moved to top for consistency

# Configure the page
st.set_page_config(
    page_title="Woowoder User Data API Client",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5E35B1;
    }
    .success-message {
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="main-header">Woowoder User Data API Client</p>', unsafe_allow_html=True)
st.markdown("Fetch, view, and download user data from the Woowoder API server")

# API endpoint
API_URL = "https://zzatem.com/api/get-user-data"

# Sidebar for API configuration
with st.sidebar:
    st.markdown('<p class="sub-header">API Configuration</p>', unsafe_allow_html=True)

    access_token = st.text_input("Access Token", type="password")

    if 'access_token' not in st.session_state:
        st.session_state.access_token = ""

    if access_token:
        save_token = st.checkbox("Remember token for this session", value=True)
        if save_token:
            st.session_state.access_token = access_token

    if not access_token and st.session_state.access_token:
        access_token = st.session_state.access_token
        st.info("Using saved access token")

    st.markdown("---")

    with st.expander("Advanced Options"):
        request_timeout = st.slider("Request Timeout (seconds)", 5, 60, 30)
        max_retries = st.slider("Max Retries", 0, 5, 2)
        show_raw_json = st.checkbox("Show Raw JSON Response", value=False)

# Main form for data fetching
with st.form("user_data_form"):
    st.markdown('<p class="sub-header">Fetch User Data</p>', unsafe_allow_html=True)

    user_id = st.number_input("User ID", min_value=1, step=1, value=1)

    st.write("Select data to fetch:")
    col1, col2 = st.columns(2)

    with col1:
        fetch_user_data = st.checkbox("User Data", value=True)
        fetch_followers = st.checkbox("Followers")
        fetch_following = st.checkbox("Following")

    with col2:
        fetch_liked_pages = st.checkbox("Liked Pages")
        fetch_joined_groups = st.checkbox("Joined Groups")

    submit_button = st.form_submit_button("Fetch Data")

# Handle form submission
if submit_button:
    if not access_token:
        st.error("Please enter an access token in the sidebar")
    else:
        fetch_items = []
        if fetch_user_data: fetch_items.append("user_data")
        if fetch_followers: fetch_items.append("followers")
        if fetch_following: fetch_items.append("following")
        if fetch_liked_pages: fetch_items.append("liked_pages")
        if fetch_joined_groups: fetch_items.append("joined_groups")

        if not fetch_items:
            st.error("Please select at least one data type to fetch")
        else:
            payload = {
                "user_id": int(user_id),
                "fetch": ",".join(fetch_items)
            }
            params = {"access_token": access_token}

            with st.spinner("Fetching data from Woowoder API..."):
                try:
                    session = requests.Session()
                    retries = requests.packages.urllib3.util.retry.Retry(
                        total=max_retries,
                        backoff_factor=0.5
                    )
                    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
                    session.mount('https://', adapter)

                    start_time = time.time()
                    response = session.post(
                        API_URL,
                        params=params,
                        data=payload,
                        timeout=request_timeout
                    )
                    request_time = time.time() - start_time

                    if response.status_code == 200:
                        data = response.json()

                        if show_raw_json:
                            with st.expander("Raw JSON Response"):
                                st.json(data)

                        if data.get("api_status") == 200:
                            st.markdown(
                                f'<div class="success-message">Data fetched successfully in {request_time:.2f} seconds!</div>',
                                unsafe_allow_html=True
                            )

                            if len(fetch_items) > 1:
                                tabs = st.tabs([item.replace('_', ' ').title() for item in fetch_items])
                            else:
                                tabs = [st.container()]

                            for i, item in enumerate(fetch_items):
                                if item in data:
                                    with tabs[i]:
                                        st.markdown(f"### {item.replace('_', ' ').title()}")

                                        if isinstance(data[item], list):
                                            if data[item]:
                                                df = pd.DataFrame(data[item])
                                                st.dataframe(df, use_container_width=True)

                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    csv = df.to_csv(index=False).encode('utf-8')
                                                    st.download_button(
                                                        f"Download as CSV",
                                                        csv,
                                                        f"woowoder_user_{user_id}_{item}.csv",
                                                        "text/csv",
                                                        key=f"download_csv_{item}"
                                                    )

                                                with col2:
                                                    buffer = io.BytesIO()
                                                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                                        df.to_excel(writer, index=False, sheet_name=item[:31])
                                                    buffer.seek(0)
                                                    st.download_button(
                                                        f"Download as Excel",
                                                        buffer,
                                                        f"woowoder_user_{user_id}_{item}.xlsx",
                                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                        key=f"download_excel_{item}"
                                                    )
                                            else:
                                                st.info(f"No {item.replace('_', ' ')} data available")
                                        elif isinstance(data[item], dict):
                                            df = pd.DataFrame([data[item]])
                                            st.dataframe(df, use_container_width=True)

                                            col1, col2 = st.columns(2)
                                            with col1:
                                                csv = df.to_csv(index=False).encode('utf-8')
                                                st.download_button(
                                                    f"Download as CSV",
                                                    csv,
                                                    f"woowoder_user_{user_id}_{item}.csv",
                                                    "text/csv",
                                                    key=f"download_csv_{item}"
                                                )

                                            with col2:
                                                json_str = json.dumps(data[item], indent=2)
                                                st.download_button(
                                                    f"Download as JSON",
                                                    json_str,
                                                    f"woowoder_user_{user_id}_{item}.json",
                                                    "application/json",
                                                    key=f"download_json_{item}"
                                                )
                                        else:
                                            st.json(data[item])
                                            json_str = json.dumps(data[item], indent=2)
                                            st.download_button(
                                                f"Download as JSON",
                                                json_str,
                                                f"woowoder_user_{user_id}_{item}.json",
                                                "application/json",
                                                key=f"download_json_{item}"
                                            )

                            # Combined export
                            st.markdown("---")
                            st.markdown("### Download Complete Dataset")
                            col1, col2 = st.columns(2)

                            with col1:
                                all_data_json = json.dumps(data, indent=2)
                                st.download_button(
                                    "Download All Data (JSON)",
                                    all_data_json,
                                    f"woowoder_user_{user_id}_all_data.json",
                                    "application/json",
                                    key="download_all_json"
                                )

                            with col2:
                                buffer = io.BytesIO()
                                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                    for item in fetch_items:
                                        if item in data:
                                            if isinstance(data[item], list) and data[item]:
                                                pd.DataFrame(data[item]).to_excel(writer, sheet_name=item[:31], index=False)
                                            elif isinstance(data[item], dict):
                                                pd.DataFrame([data[item]]).to_excel(writer, sheet_name=item[:31], index=False)
                                buffer.seek(0)
                                st.download_button(
                                    "Download All Data (Excel)",
                                    buffer,
                                    f"woowoder_user_{user_id}_all_data.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="download_all_excel"
                                )
                        else:
                            st.error(f"API returned an error: {data.get('error_message', 'Unknown error')}")
                    else:
                        st.error(f"Request failed with status code: {response.status_code}")
                        if response.text:
                            st.code(response.text)
                except requests.exceptions.Timeout:
                    st.error(f"Request timed out after {request_timeout} seconds. Try increasing the timeout in Advanced Options.")
                except requests.exceptions.ConnectionError:
                    st.error("A connection error occurred. Please check your internet connection or API URL.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
