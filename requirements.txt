import streamlit as st
import pandas as pd
import requests
import json
import time
import os

st.set_page_config(page_title="User Data Viewer", layout="wide")

# Sidebar for API credentials
st.sidebar.title("API Credentials")
api_url = st.sidebar.text_input("API URL", "http://your-site.com/api/get-user-data")
access_token = st.sidebar.text_input("Access Token", type="password")

# Main content
st.title("User Data Viewer and CSV Exporter")

# User input form
with st.form("user_data_form"):
    user_id = st.number_input("User ID", min_value=1, step=1)
    
    st.write("Select data to fetch:")
    fetch_user_data = st.checkbox("User Data", value=True)
    fetch_followers = st.checkbox("Followers")
    fetch_following = st.checkbox("Following")
    fetch_liked_pages = st.checkbox("Liked Pages")
    fetch_joined_groups = st.checkbox("Joined Groups")
    
    submitted = st.form_submit_button("Fetch Data")

# Process form submission
if submitted:
    if not access_token:
        st.error("Please enter an access token in the sidebar.")
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
            st.error("Please select at least one data type to fetch.")
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
                    response = requests.post(api_url, params=params, data=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get("api_status") == 200:
                            # Store all dataframes
                            dataframes = {}
                            
                            # Process and display each requested data type
                            for item in fetch_items:
                                if item in data:
                                    st.subheader(f"{item.replace('_', ' ').title()}")
                                    
                                    # Convert to dataframe
                                    if isinstance(data[item], list):
                                        df = pd.DataFrame(data[item])
                                    elif isinstance(data[item], dict):
                                        df = pd.DataFrame([data[item]])
                                    else:
                                        st.write(data[item])
                                        continue
                                    
                                    # Store dataframe for export
                                    dataframes[item] = df
                                    
                                    # Display dataframe
                                    st.dataframe(df)
                                    
                                    # Add download button for each dataframe
                                    csv = df.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        f"Download {item} CSV",
                                        csv,
                                        f"user_{user_id}_{item}.csv",
                                        "text/csv",
                                        key=f"download_{item}"
                                    )
                            
                            # Option to download all data as a single CSV
                            if len(dataframes) > 1:
                                st.subheader("Export All Data")
                                
                                # Create a directory for combined exports
                                export_dir = "exports"
                                os.makedirs(export_dir, exist_ok=True)
                                
                                # Generate timestamp for unique filename
                                timestamp = int(time.time())
                                combined_filename = f"{export_dir}/user_{user_id}_all_data_{timestamp}.csv"
                                
                                # Save all dataframes to separate CSV files
                                for name, df in dataframes.items():
                                    df.to_csv(f"{export_dir}/user_{user_id}_{name}_{timestamp}.csv", index=False)
                                
                                st.success(f"All data exported to {export_dir} directory")
                                
                                # For large datasets, provide info on where to find the files
                                st.info("For large datasets (>10,000 records), check the exports folder in your app directory.")
                        else:
                            st.error(f"API returned an error: {data.get('error_message', 'Unknown error')}")
                    else:
                        st.error(f"Request failed with status code: {response.status_code}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Add instructions
with st.expander("How to use this app"):
    st.markdown("""
    1. Enter your API URL and access token in the sidebar
    2. Enter the user ID you want to fetch data for
    3. Select the types of data you want to fetch
    4. Click "Fetch Data" to retrieve the information
    5. View the data and download as CSV
    
    For large datasets (over 10,000 records), the app will save files to the 'exports' directory.
    """)
