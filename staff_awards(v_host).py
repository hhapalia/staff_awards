import streamlit as st
import pandas as pd
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

mongo_uri = st.secrets["mongo"]["uri"]
mongo_db = st.secrets["mongo"]["database"]
mongo_collection = st.secrets["mongo"]["collection"]
mongo_staff_collection = st.secrets["mongo"]["staff_collection"]

client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = client[mongo_db]
collection = db[mongo_collection]
staff_collection = db[mongo_staff_collection]

awards = [
    "Human GPT",
    "The Butterfly Award – Everyone’s friend, everywhere",
    "The Jugaadu Genius – Always has a clever fix for everything",
    "The Brainstorm Boss – Always bursting with ideas",
    "The Win-Win Warrior – Makes sure no one loses",
    "Master Multitasker",
    "The Unsung Hero Award – Quietly making the biggest difference",
    "The Accidental Comedian – Unintentionally hilarious.",
    "The Creative Catalyst – For the teacher who inspires creativity in the classroom, sparking innovation in every lesson.",
    "Unofficial Therapist",
    "The Chill Pill Award – Calms every storm with zen-like vibes",
    "The One-Liner Legend – Drops truth bombs and punchlines effortlessly",
    "The WiFi Whisperer – Tech issues vanish when they enter",
    "The Detail Detective – Spots errors no one else ever does",
    "The “Heart Before Haste” Award – Makes people feel heard",
    "The Ice Cream in Chaos Award – Sweetness in stressful times",
    "The Grammar Guardian – Typos fear them",
    "Fitness Freak",
    "The EBA Champion – Keeps emotional bank accounts full",
    "The Untangled Thinker – Simplifies even the messiest mess",
    "Silent Storm",
    "Social Media Star",
    "Sunshine Award – Lights up the team’s mood",
    "The No-Filter Educator – Whatever’s in the head, comes out the mouth.",
    "The Anchor Award – Keeps the team grounded",
    "The Mentor Magician – Gives advice that actually lands"
]

# Load staff data
# staff_df = pd.read_csv("teams_password.csv")
staff_df = pd.DataFrame(list(staff_collection.find({}, {"_id": 0})))

##############################

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.voter_name = ""
    st.session_state.team = ""

# Login screen
if not st.session_state.logged_in:
    st.title("🔐 Staff Login")
    #username = st.number_input("Username (reg_id)", placeholder="enter RegId", step=1)
    #password = st.number_input("Password", placeholder="enter RegId",step=1)
    username = st.text_input("Username").strip()
    password = st.text_input("Password").strip()
    login_btn = st.button("Login")

    staff_df["reg_id"] = staff_df["reg_id"].astype(str).str.strip()

    if login_btn:
        user_row = staff_df[staff_df["reg_id"] == username]
        if not user_row.empty and username == password:
            st.session_state.logged_in = True
            st.session_state.voter_name = user_row.iloc[0]["staff_name"]
            st.session_state.team = user_row.iloc[0]["team"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")
else:
    # Voting Screen
    st.title("🏆 Team Awards Voting")
    voter = st.session_state.voter_name
    team = st.session_state.team
    team_members = staff_df[(staff_df["team"] == team) & (staff_df["staff_name"] != voter)]

    st.subheader(f"Welcome, {voter} 👋 (Team: {team})")
    st.markdown("**Select an award for each of your teammates:**")

    # Check if already voted
    existing_vote = collection.find_one({"voter": voter})
    if existing_vote:
        st.info("✅ You have already submitted your votes.")
    else:
        votes = []
        with st.form("award_form"):
            for _, row in team_members.iterrows():
                selected_award = st.selectbox(
                    f"{row['staff_name']}",
                    ["-- Select Award --"] + awards,
                    key=row['staff_name']
                )
                votes.append({"staff": row["staff_name"], "award": selected_award})

            submitted = st.form_submit_button("Submit Votes")

        if submitted:
            if any(v["award"] == "-- Select Award --" for v in votes):
                st.error("Please select an award for everyone.")
            else:
                record = {
                    "voter": voter,
                    "team": team,
                    "votes": votes,
                    "timestamp": datetime.now(timezone.utc)
                }
                collection.insert_one(record)
                st.success("✅ Your votes have been submitted successfully!")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.voter_name = ""
        st.session_state.team = ""
        st.rerun()

