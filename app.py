import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="API Data Downloader", layout="wide")

st.title("API Data Downloader")
st.write("Fetch and download user data from the API")

# API endpoint
API_URL = "https://zzatem.com/api/get-user-data"

# Create a form for the API parameters
with st.form("api_form"):
    # Access token input
    access_token = st.text_input("Access Token", type="password")
    
    # User ID input
    user_id = st.number_input("User ID", min_value=1, step=1)
    
    # Data to fetch checkboxes
    st.write("Select data to fetch:")
    col1, col2 = st.columns(2)
    
    with col1:
        fetch_user_data = st.checkbox("User Data", value=True)
        fetch_followers = st.checkbox("Followers")
        fetch_following = st.checkbox("Following")
    
    with col2:
        fetch_liked_pages = st.checkbox("Liked Pages")
        fetch_joined_groups = st.checkbox("Joined Groups")
    
    # Submit button
    submit_button = st.form_submit_button("Fetch Data")

# Handle form submission
if submit_button:
    if not access_token:
        st.error("Please enter an access token")
    else:
        # Prepare fetch parameter
        fetch_items = []
        if fetch_user_data:
            fetch_items.append("user_data")
        if fetch_followers:
            fetch_items.append("followers")
        if fetch_following:
            fetch_items.append("following")
        if fetch_liked_pages:
            fetch_items.append("liked_pages")
        if fetch_joined_groups:
            fetch_items.append("joined_groups")
        
        if not fetch_items:
            st.error("Please select at least one data type to fetch")
        else:
            # Prepare request data
            fetch_param = ",".join(fetch_items)
            payload = {
                "user_id": int(user_id),
                "fetch": fetch_param
            }
            
            params = {
                "access_token": access_token
            }
            
            # Show loading spinner
            with st.spinner("Fetching data..."):
                try:
                    # Make the API request
                    response = requests.post(API_URL, params=params, data=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("api_status") == 200:
                            # Display success message
                            st.success("Data fetched successfully!")
                            
                            # Process and display each requested data type
                            for item in fetch_items:
                                if item in data:
                                    st.subheader(f"{item.replace('_', ' ').title()}")
                                    
                                    # Convert to dataframe
                                    if isinstance(data[item], list):
                                        if data[item]:  # Check if list is not empty
                                            df = pd.DataFrame(data[item])
                                            st.dataframe(df)
                                            
                                            # Add download button
                                            csv = df.to_csv(index=False).encode('utf-8')
                                            st.download_button(
                                                f"Download {item.replace('_', ' ').title()} CSV",
                                                csv,
                                                f"user_{user_id}_{item}.csv",
                                                "text/csv",
                                                key=f"download_{item}"
                                            )
                                        else:
                                            st.info(f"No {item.replace('_', ' ')} data available")
                                    elif isinstance(data[item], dict):
                                        df = pd.DataFrame([data[item]])
                                        st.dataframe(df)
                                        
                                        # Add download button
                                        csv = df.to_csv(index=False).encode('utf-8')
                                        st.download_button(
                                            f"Download {item.replace('_', ' ').title()} CSV",
                                            csv,
                                            f"user_{user_id}_{item}.csv",
                                            "text/csv",
                                            key=f"download_{item}"
                                        )
                                    else:
                                        st.json(data[item])
                                        
                                        # Add download button for JSON
                                        json_str = json.dumps(data[item], indent=2)
                                        st.download_button(
                                            f"Download {item.replace('_', ' ').title()} JSON",
                                            json_str,
                                            f"user_{user_id}_{item}.json",
                                            "application/json",
                                            key=f"download_{item}"
                                        )
                            
                            # Add download button for all data
                            all_data_json = json.dumps(data, indent=2)
                            st.download_button(
                                "Download All Data (JSON)",
                                all_data_json,
                                f"user_{user_id}_all_data.json",
                                "application/json",
                                key="download_all"
                            )
                        else:
                            st.error(f"API returned an error: {data.get('error_message', 'Unknown error')}")
                    else:
                        st.error(f"Request failed with status code: {response.status_code}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Add instructions
with st.expander("How to use"):
    st.markdown("""
    ### Instructions:
    
    1. Enter your access token
    2. Enter the user ID you want to fetch data for
    3. Select the types of data you want to fetch
    4. Click "Fetch Data"
    5. View the data and download as CSV or JSON
    
    ### API Endpoint:
    
