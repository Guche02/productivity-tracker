import streamlit as st
import requests
import pandas as pd
import altair as alt

API_BASE_URL = "http://localhost:8000/users" 

st.set_page_config(page_title="Productivity Tracker", layout="centered")

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "view_chart" not in st.session_state:
    st.session_state.view_chart = False

def show_login():
    st.title("🔐 Login to Productivity Tracker")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

        if login:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.access_token = token
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password")

def show_register():
    st.title("📝 Create an Account")
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            response = requests.post(f"{API_BASE_URL}/create", json={
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                st.success("Account created! Now login.")
            else:
                st.error(response.json().get("detail", "Error creating account"))

def show_chat_interface():
    st.title("🤖 Productivity Chatbot")
    st.markdown("Ask about your productivity or summarize your day.")

    with st.sidebar:
        st.markdown("## Account")

        if st.button("📈 View Last 7 Days Productivity"):
            st.session_state.view_chart = True  

        if st.button("🔓 Logout"):
            st.session_state.access_token = None
            st.session_state.messages = []
            st.session_state.view_chart = False  
            st.success("Logged out successfully.")
            st.rerun()

    if st.session_state.view_chart:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        try:
            res = requests.get(f"{API_BASE_URL}/productivity-history", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data:
                    df = pd.DataFrame(data)
                    df["date"] = pd.to_datetime(df["date"])
                    metrics = ["overall", "exercise", "study", "meditation", "hobby", "rest_time"]

                    st.markdown("### 📊 Select Productivity Metric")
                    metric = st.selectbox("Choose a category to view:", metrics)

                    df[metric] = pd.to_numeric(df[metric].astype(str).str.strip(), errors="coerce")
                    filtered_df = df.dropna(subset=[metric])

                    if filtered_df.empty:
                        st.warning(f"No valid data for **{metric}** in the past 7 days.")
                    else:
                        chart = alt.Chart(filtered_df).mark_bar().encode(
                            x=alt.X("date:T", title="Date"),
                            y=alt.Y(f"{metric}:Q", title="Score"),
                            tooltip=["date:T", f"{metric}:Q"]
                        ).properties(
                            title=f"📊 {metric.replace('_', ' ').title()} Scores (Last 7 Days)",
                            width=600,
                            height=400
                        )
                        st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No productivity data available.")
            else:
                st.error("Failed to fetch productivity history.")
        except Exception as e:
            st.error(f"API error: {e}")

    if not st.session_state.messages:
        welcome_message = (
            "Hi there, I am your productivity assistant! 😊\n\n"
            "Tell me about your day, or would you like to view your previous scores?"
        )
        st.session_state.messages.append(("Bot", welcome_message))

    for sender, msg in st.session_state.messages:
        with st.chat_message("user" if sender == "You" else "assistant"):
            st.markdown(msg)

    user_input = st.chat_input("What's your productivity update today?")
    if user_input:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        try:
            res = requests.post(
                f"{API_BASE_URL}/productivity",
                params={"user_input": user_input},
                headers=headers
            )
            if res.status_code == 200:
                result = res.json()
                message = result["message"]

                st.session_state.messages.append(("You", user_input))
                st.session_state.messages.append(("Bot", message))

                with st.chat_message("user"):
                    st.markdown(user_input)
                with st.chat_message("assistant"):
                    st.markdown(message)

                    if "scores" in result:
                        st.markdown("### 📊 Your Productivity Scores")
                        for key, value in result["scores"].items():
                            st.markdown(f"**{key.replace('_', ' ').title()}**")
                            st.progress(value / 5)
            else:
                st.error(res.json().get("detail", "Something went wrong"))
        except Exception as e:
            st.error(f"API error: {e}")

if st.session_state.access_token:
    show_chat_interface()
else:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        show_login()
    with tab2:
        show_register()