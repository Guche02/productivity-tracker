import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000/users"  # Adjust as needed

st.set_page_config(page_title="Productivity Tracker", layout="centered")

# Session state initialization
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------- Login/Register Forms ------------------- #
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

    # Sidebar logout button
    with st.sidebar:
        st.markdown("## Account")
        if st.button("🔓 Logout"):
            st.session_state.access_token = None
            st.session_state.messages = []
            st.success("Logged out successfully.")
            st.rerun()

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
        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }
        try:
            res = requests.post(
                f"{API_BASE_URL}/productivity",
                params={"user_input": user_input},
                headers=headers
            )
            if res.status_code == 200:
                result = res.json()
                message = result["message"]

                # Append and show new messages
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

# ------------------- Main Page Layout ------------------- #
if st.session_state.access_token:
    show_chat_interface()
else:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        show_login()
    with tab2:
        show_register()
