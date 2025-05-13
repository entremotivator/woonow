import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Zzatem API v2 - Multi User Data", layout="wide")
st.title("🧑‍💻 Zzatem API v2 - Multi-User Data Scraper")

# Input server key and user IDs
server_key = st.text_input("🔑 Server Key (API v2)", type="password", help="Paste your API v2 Server Key here")
user_ids_input = st.text_area("👥 Enter User IDs (comma-separated)", "1,2,3,4,5")

if st.button("🚀 Fetch User Data"):
    if not server_key:
        st.error("Please enter your Server Key.")
    elif not user_ids_input.strip():
        st.error("Please enter one or more user IDs.")
    else:
        # Clean user IDs
        user_ids_clean = ",".join([uid.strip() for uid in user_ids_input.split(",") if uid.strip().isdigit()])
        post_data = {"user_ids": user_ids_clean}
        
        # Full URL with server key as access_token
        endpoint = f"https://zzatem.com/api/v2/api/get-many-users-data?access_token={server_key}"

        try:
            # Make the POST request
            response = requests.post(endpoint, data=post_data)
            response.raise_for_status()
            result = response.json()

            # Check if successful
            if result.get("api_status") == 200 and "users" in result:
                users = result["users"]
                if users:
                    df = pd.DataFrame(users)
                    st.success(f"✅ Successfully fetched {len(users)} users.")
                    st.dataframe(df)

                    # Optional download
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", csv, "zzatem_users.csv", "text/csv")
                else:
                    st.warning("⚠️ No users found.")
            else:
                st.error(f"❌ API Error: {result.get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"🔌 Connection error: {e}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
