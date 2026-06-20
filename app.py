import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")
# Page settings
st.set_page_config(page_title="InsureWise AI", page_icon="🏥")

# Title
st.title("🏥 InsureWise AI")
st.subheader("Public Health Benefits Navigator")

st.write(
    "Describe your situation in plain language. "
    "InsureWise AI will help you understand which public health programs "
    "you may qualify for and what steps to take next."
)

# Sidebar
st.sidebar.header("📚 Key Terms")

st.sidebar.write("""
**Premium**  
What you pay monthly for insurance.

**Deductible**  
What you pay before insurance starts covering costs.

**Copay**  
A fixed amount you pay for a visit.

**In-network**  
Doctors and hospitals covered at lower cost.
""")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Describe your situation...")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = """
You are InsureWise AI, a friendly public health benefits navigator.

Your job is to help users understand which public health programs they may qualify for.

Always explain things in simple language.

Recommend only from:

- Medicaid
- CHIP
- ACA Marketplace plans with subsidies
- Community Health Centers

Always organize your answer into these sections:

## Programs You May Qualify For

Explain each program and why.

## Documents to Gather

Examples:
- Proof of income
- Household information
- Proof of residency

## Next Steps

Provide clear actions.

## Key Terms Explained

Explain premium, deductible, copay, or in-network if needed.

## Important Reminder

State:

"This is guidance only and not an official eligibility determination. Please verify information through Healthcare.gov or your state Medicaid agency."

Never ask for:
- Social Security numbers
- Addresses
- Account numbers
"""

    full_prompt = system_prompt + "\n\nUser:\n" + prompt

    response = model.generate_content(full_prompt)

    answer = response.text

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )