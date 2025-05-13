import streamlit as st
import requests
import pandas as pd

st.title("Zzatem Multi-User Data Scraper")

# Input API endpoint and access token
base_url = st.text_input("Base API URL", "https://zzatem.com/api/v2/api/get-many-users-data")
access_token = st.text_input("Access Token", type="password")

# Input user IDs
user_ids_input = st.text_area("Enter User IDs (comma-separated)", "1,2,3,4,5")

if st.button("Fetch Data"):
    if not user_ids_input.strip():
        st.error("Please enter at least one user ID.")
    else:
        # Prepare request
        user_ids_clean = ",".join([uid.strip() for uid in user_ids_input.split(",") if uid.strip().isdigit()])
        post_data = {"user_ids": user_ids_clean}

        # Build full URL with access token
        full_url = f"{base_url}?access_token={access_token}"

        try:
            response = requests.post(full_url, data=post_data)
            response.raise_for_status()
            result = response.json()

            if result.get("api_status") == 200 and "users" in result:
                users = result["users"]
                if users:
                    df = pd.DataFrame(users)
                    st.success(f"Fetched {len(users)} users.")
                    st.dataframe(df)

                    # Download button
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "zzatem_users.csv", "text/csv")
                else:
                    st.warning("No user data returned.")
            else:
                st.error(f"API Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
