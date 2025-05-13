import streamlit as st
import requests
import pandas as pd

st.title("WooWoder API Scraper")

# API URL input
api_url = st.text_input("API URL", "https://api.woowoder.com/fetch")

# Checkbox to toggle between specific user or all users
fetch_all_users = st.checkbox("Fetch All Users", value=False)

# Optional User ID input
user_id = None
if not fetch_all_users:
    user_id = st.number_input("User ID", min_value=1, step=1, value=1)

# Items to fetch
fetch_items = st.multiselect(
    "Select items to fetch",
    ["profiles", "orders", "payments", "subscriptions", "messages", "referrals", "stats"],
    default=["profiles"]
)

# API Key
api_key = st.text_input("API Key", type="password")

# Fetch button
if st.button("Fetch Data"):
    if not api_url or not fetch_items:
        st.error("API URL and at least one fetch item are required.")
    else:
        # Prepare request payload
        fetch_param = ",".join(fetch_items)
        payload = {
            "fetch": fetch_param
        }
        if not fetch_all_users:
            payload["user_id"] = int(user_id)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                st.error("Invalid response format from API.")
            else:
                for item in fetch_items:
                    item_data = data.get(item)
                    if item_data:
                        df = pd.DataFrame(item_data)
                        st.subheader(f"{item.capitalize()} Data")
                        st.dataframe(df)

                        # File name
                        user_label = f"user_{user_id}" if user_id else "all_users"
                        csv_filename = f"woowoder_{user_label}_{item}.csv"
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"Download {item} CSV",
                            data=csv,
                            file_name=csv_filename,
                            mime='text/csv'
                        )
                    else:
                        st.warning(f"No data returned for '{item}'.")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
        except ValueError:
            st.error("Failed to parse API response.")

