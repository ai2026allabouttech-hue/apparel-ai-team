# =====================================================================
# APPAREL AI TEAM: WEBSITE VERSION (Streamlit + Gemini)
# One page with: Launch Plan tab, 5 agent tabs (one button each), History tab.
# Brand details are edited on the website itself (left side bar), no code editing needed.
# =====================================================================

import os                          # lets the code talk to the computer (files, settings)
import json                        # lets the code save/read notes in a simple text format
import datetime                    # lets the code know today's date and time
import streamlit as st             # the tool that turns this code into a website
from google import genai           # the tool that lets this code talk to Gemini (Google's AI)
from google.genai import types     # extra settings for Gemini (like turning on Google Search)

st.set_page_config(page_title="Apparel AI Team", page_icon="👗", layout="wide")  # browser tab title + wide page

MODEL = "gemini-3.6-flash"         # which Gemini brain to use. If "model not found" appears, change this name.
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))  # Indian time, so dates look right

# ---------------------------------------------------------------------
# STEP 1: READ SECRETS (your key + website password are NOT written in the code)
# ---------------------------------------------------------------------
def get_secret(name):                                  # a small job: find a secret by its name
    try:                                               # try the hosting site's secret box first
        return st.secrets[name]                        # give back the secret if found
    except Exception:                                  # if the box or secret is missing...
        return os.environ.get(name, "")                # ...try the computer's settings, else empty

API_KEY = get_secret("GEMINI_API_KEY")                 # your Gemini key
APP_PASSWORD = get_secret("APP_PASSWORD")              # the password to open this website

# ---------------------------------------------------------------------
# STEP 2: PASSWORD GATE (so strangers cannot use your key and spend your money)
# ---------------------------------------------------------------------
if APP_PASSWORD and not st.session_state.get("logged_in"):   # if a password is set and you are not logged in...
    st.title("👗 Apparel AI Team")                     # show the title
    typed = st.text_input("Enter password", type="password")  # show a hidden password box
    if typed:                                          # once something is typed...
        if typed == APP_PASSWORD:                      # ...if it matches the real password...
            st.session_state["logged_in"] = True       # ...remember that you are logged in
            st.rerun()                                 # ...and reload the page
        else:                                          # ...otherwise...
            st.error("Wrong password.")                # ...say it is wrong
    st.stop()                                          # stop here, nothing below is shown until login

if not API_KEY:                                        # if no Gemini key was found...
    st.error("GEMINI_API_KEY is missing. Add it in the app's Secrets.")  # tell you clearly
    st.stop()                                          # stop here

client = genai.Client(api_key=API_KEY)                 # connect to Gemini using your key

# ---------------------------------------------------------------------
# STEP 3: SAVING AND LOADING (brand details + the shared notebook of reports)
# ---------------------------------------------------------------------
MEMORY_FILE = "hub_memory.json"                        # the notebook file where all reports are saved
BRAND_FILE = "brand.json"                              # the file where brand details are saved

DEFAULT_BRAND = {                                      # starting brand details (you edit these on the website)
    "name": "Nicobar",                                  # brand name
    "product": "women's kurta sets and co-ord sets",   # what you sell
    "price_range": "Rs 899 - Rs 1999",                 # your selling price
    "market": "India, ages 18-35",                     # who buys
    "rivals": ["Rival 1", "Rival 2", "Rival 3", "Rival 4", "Rival 5"],  # replace on the website
    "next_festival": "Christmas and New Year",         # next big sale season
}

def load_json(path, default):                          # a small job: open a saved file
    if os.path.exists(path):                           # if the file exists...
        with open(path, "r", encoding="utf-8") as f:   # ...open it for reading
            return json.load(f)                        # ...and give back what is inside
    return default                                     # if not, give back the starting value

def save_json(path, data):                             # a small job: save data to a file
    with open(path, "w", encoding="utf-8") as f:       # open the file for writing
        json.dump(data, f, indent=2, ensure_ascii=False)  # write everything neatly

brand = load_json(BRAND_FILE, DEFAULT_BRAND)           # load saved brand details (or the starting ones)
memory = load_json(MEMORY_FILE, {})                    # load the shared notebook of old reports

# ---------------------------------------------------------------------
# STEP 4: THE LEFT SIDE BAR (edit your brand details here)
# ---------------------------------------------------------------------
with st.sidebar:                                       # everything inside goes on the left side bar
    st.header("🏷️ Brand details")                      # a heading
    brand["name"] = st.text_input("Brand name", brand["name"])           # box for brand name
    brand["product"] = st.text_input("What you sell", brand["product"])  # box for product
    brand["price_range"] = st.text_input("Your price range", brand["price_range"])  # box for price
    brand["market"] = st.text_input("Your customers", brand["market"])   # box for customers
    rivals_text = st.text_area(                        # a big box: one rival brand per line
        "5 rival brands (one per line)", "\n".join(brand["rivals"]), height=140
    )
    brand["rivals"] = [r.strip() for r in rivals_text.split("\n") if r.strip()]  # turn lines into a list
    brand["next_festival"] = st.text_input("Next big sale season", brand["next_festival"])  # box for festival
    if st.button("💾 Save brand details"):             # when you click Save...
        save_json(BRAND_FILE, brand)                   # ...write the details to the file
        st.success("Saved!")                           # ...and confirm

# ---------------------------------------------------------------------
# STEP 5: THE 5 AGENTS (each has ONE job)
# "about" = one line shown on the website. "role" = who the agent is. "task" = what to do.
# ---------------------------------------------------------------------
AGENTS = {
    "Trend Scout": {                                   # Agent 1
        "about": "Finds which styles are growing fast on Instagram and Reels right now.",
        "role": "You are Trend Scout for an online clothing brand. You find which clothing "
                "styles, colours and fabrics are growing fast on Instagram and Reels right now. "
                "Only report what you can find on the web. Say 'not sure' if unclear.",
        "task": "Brand: {name}, sells {product} in {market}. List the top 5 fast-growing styles "
                "this week on Instagram/Reels. For each: style name, why it is rising, "
                "and one product idea we can launch. Keep it short.",
    },
    "Rival Watch": {                                   # Agent 2
        "about": "Tracks 5 rivals: prices, new launches and sales.",
        "role": "You are Rival Watch. You track competitor brands: their prices, new launches "
                "and sales. Use only facts found on the web. Never invent a price.",
        "task": "Our brand: {name}, price {price_range}. Rivals: {rivals}. For each rival give: "
                "price range, newest launch, any sale running now. End with 3 lines on where "
                "we are cheaper or costlier, and any price drop we must react to.",
    },
    "Review Reader": {                                 # Agent 3
        "about": "Reads rival customer reviews and finds what customers hate.",
        "role": "You are Review Reader. You read customer reviews of rival brands and find "
                "what customers complain about, so our brand can fix it first.",
        "task": "Rivals: {rivals}. Find recent customer reviews (Amazon, Myntra, Google, "
                "Trustpilot etc). Give the top 5 repeated complaints (size, fabric, delivery, "
                "returns...) and one way {name} can win on each.",
    },
    "Ad Hunter": {                                     # Agent 4
        "about": "Finds the formula of rival ads that have run for months.",
        "role": "You are Ad Hunter. You study ads that rivals have been running for months "
                "(long-running ads usually mean they make money) and find the formula.",
        "task": "Look at Meta Ad Library style info for rivals: {rivals}. Find ads running "
                "for a long time. Describe the formula: hook, visual, offer, call-to-action. "
                "Then write 3 ad ideas for {name}'s {product} using that formula.",
    },
    "Creator Scout": {                                 # Agent 5
        "about": "Finds Instagram creators with real followers for collabs.",
        "role": "You are Creator Scout. You find Instagram creators with REAL followers "
                "(good engagement, real comments, no obvious fake followers).",
        "task": "Find 10 Instagram creators in fashion for {market} who would suit {name} "
                "({product}). For each: handle, follower range, why their audience looks real, "
                "and a suggested collab type. Flag any who look suspicious.",
    },
}

# ---------------------------------------------------------------------
# STEP 6: THE JOBS THAT MAKE AN AGENT WORK (same brain as the code you ran before)
# ---------------------------------------------------------------------
def now_text():                                        # a small job: current date and time in India
    return datetime.datetime.now(IST).strftime("%d %b %Y, %H:%M")  # like "23 Nov 2026, 13:20"

def latest(key):                                       # a small job: get the newest saved report
    items = memory.get(key, [])                        # all saved reports for this agent
    return items[-1] if items else None                # the last one, or nothing

def save_report(key, report):                          # a small job: save a new report in the notebook
    memory.setdefault(key, []).append({"date": now_text(), "report": report})  # add it with the time
    save_json(MEMORY_FILE, memory)                     # write the notebook to the file

def run_agent(agent_name):                             # a job: run one agent and return its report
    agent = AGENTS[agent_name]                         # pick this agent's role and task
    task = agent["task"].format(                       # fill your brand facts into the task text
        name=brand["name"], product=brand["product"], market=brand["market"],
        price_range=brand["price_range"], rivals=", ".join(brand["rivals"]),
    )
    last = latest(agent_name)                          # this agent's previous report
    if last:                                           # if it worked before...
        task += "\n\nYour last report was:\n" + last["report"]  # ...show it
        task += "\nMention what CHANGED since then."   # ...and ask for the changes
    response = client.models.generate_content(         # ask Gemini to do the work
        model=MODEL,                                   # the chosen brain
        contents=task,                                 # the task
        config=types.GenerateContentConfig(            # extra settings
            system_instruction=agent["role"],          # who the agent is
            tools=[types.Tool(google_search=types.GoogleSearch())],  # allow Google Search for live info
            max_output_tokens=3000,                    # limit answer length (controls cost)
        ),
    )
    return response.text or "(No answer received)"     # return the report text

def make_launch_plan():                                # a job: combine the latest 5 reports into one plan
    parts = []                                         # an empty list to collect reports
    for name in AGENTS:                                # go through all 5 agents
        item = latest(name)                            # get each agent's newest report
        if item:                                       # if it exists...
            parts.append(f"=== {name} ({item['date']}) ===\n{item['report']}")  # ...add it
    combined = "\n\n".join(parts)                      # join them into one big text
    response = client.models.generate_content(         # ask Gemini to act as the planner
        model=MODEL,
        contents=(
            f"Brand: {brand['name']}. Next festival: {brand['next_festival']}.\n\n{combined}\n\n"
            "Write a launch plan with: 1) What to launch (styles + price), "
            "2) Price position vs rivals, 3) Problems to fix before launch (from reviews), "
            "4) 3 ad ideas, 5) Which creators to contact first, "
            "6) A checklist for the first 3 weeks, "
            f"7) What to prepare 3 weeks before {brand['next_festival']}."
        ),
        config=types.GenerateContentConfig(
            system_instruction="You are the Business Hub planner for an online clothing brand. "
                               "Combine the agent reports into one clear launch plan a busy founder can act on.",
            max_output_tokens=4000,                    # allow a longer answer for the plan
        ),
    )
    return response.text or "(No plan received)"       # return the plan text

def show_report(key):                                  # a job: display the newest saved report on screen
    item = latest(key)                                 # get the newest report
    if item:                                           # if there is one...
        st.caption(f"Last updated: {item['date']}")    # ...show when it was made
        st.markdown(item["report"])                    # ...show the report itself
        st.download_button("⬇️ Download this report", item["report"],  # ...a download button
                           file_name=f"{key.replace(' ', '_')}.md", key=f"dl_{key}")
    else:                                              # if nothing saved yet...
        st.info("No report yet. Click the button above to create one.")  # ...say so

# ---------------------------------------------------------------------
# STEP 7: THE WEBSITE PAGE ITSELF
# ---------------------------------------------------------------------
st.title(f"👗 {brand['name']} AI Team")                # big title with your brand name
st.caption("5 AI agents + 1 business hub. Click a tab, press the button, read the result.")  # small line

tab_names = ["🏠 Launch Plan"] + list(AGENTS.keys()) + ["📜 History"]  # names of all tabs
tabs = st.tabs(tab_names)                              # create the tabs

with tabs[0]:                                          # TAB 1: the Launch Plan
    st.subheader("Launch Plan")                        # heading
    st.write("Runs all 5 agents, then combines everything into one plan. Takes a few minutes.")  # help line
    if st.button("🚀 Run all 5 agents + build plan"):  # when you click the big button...
        bar = st.progress(0, text="Starting...")       # ...show a progress bar
        try:                                           # ...try the work (catch problems politely)
            for i, name in enumerate(AGENTS):          # ...go through each agent
                bar.progress(i / 6, text=f"Running {name}...")  # ......update the bar
                save_report(name, run_agent(name))     # ......run the agent and save its report
            bar.progress(5 / 6, text="Building the launch plan...")  # ...update the bar
            save_report("Launch Plan", make_launch_plan())  # ...build and save the plan
            bar.progress(1.0, text="Done!")            # ...finish the bar
            st.rerun()                                 # ...reload to show the fresh plan
        except Exception as e:                         # ...if anything goes wrong...
            st.error(f"Something went wrong: {e}")     # ...show the problem in plain text
    show_report("Launch Plan")                         # show the newest plan (if any)

for tab, name in zip(tabs[1:6], AGENTS):               # TABS 2 to 6: one tab for each agent
    with tab:                                          # inside this agent's tab...
        st.subheader(name)                             # ...its name
        st.write(AGENTS[name]["about"])                # ...its one-line job
        if st.button(f"▶ Run {name}", key=f"run_{name}"):  # ...its own run button
            try:                                       # ...try the work
                with st.spinner(f"{name} is working..."):  # ......show a spinner
                    save_report(name, run_agent(name)) # ......run and save the report
                st.rerun()                             # ......reload to show it
            except Exception as e:                     # ...if something goes wrong...
                st.error(f"Something went wrong: {e}") # ...show the problem
        show_report(name)                              # ...show the newest report

with tabs[6]:                                          # LAST TAB: History of all old reports
    st.subheader("History")                            # heading
    pick = st.selectbox("Choose an agent", ["Launch Plan"] + list(AGENTS.keys()))  # a dropdown list
    old = memory.get(pick, [])                         # all saved reports of that agent
    if not old:                                        # if none saved...
        st.info("Nothing saved yet.")                  # ...say so
    for item in reversed(old):                         # newest first
        with st.expander(item["date"]):                # a click-to-open box with the date
            st.markdown(item["report"])                # the old report inside
