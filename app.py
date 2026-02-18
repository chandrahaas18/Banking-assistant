import streamlit as st
import openai
import os

st.set_page_config(page_title="Banking Assistant", page_icon="🏦")
st.title("🏦 Banking Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "input_trigger" not in st.session_state:
    st.session_state.input_trigger = None
if "using_ai" not in st.session_state:
    st.session_state.using_ai = False

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        st.session_state.api_key = api_key
        openai.api_key = api_key
        st.session_state.using_ai = True
        st.success("✅ AI Mode Activated!")
    else:
        st.session_state.using_ai = False
        st.info("ℹ️ Using Fallback Mode (no API key)")
    
    # Test connection button
    if st.session_state.api_key and st.button("🔌 Test AI Connection", use_container_width=True):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'AI is working!' in 3 words"}],
                max_tokens=10
            )
            st.success(f"✅ AI Connected! Response: {response.choices[0].message.content}")
        except Exception as e:
            st.error(f"❌ Connection Failed: {str(e)}")
            st.session_state.using_ai = False
    
    st.divider()
    
    # Show current mode
    mode_color = "green" if st.session_state.using_ai else "orange"
    st.markdown(f"**Current Mode:** :{mode_color}[{'AI MODE' if st.session_state.using_ai else 'FALLBACK MODE'}]")
    
    st.divider()
    
    st.header("❓ Try these")
    samples = ["How to open account?", "Lost my card!", "Loan rates?", "Branch hours?", "Tell me a joke", "What's 2+2?"]
    for q in samples:
        if st.button(q, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.input_trigger = q
            st.rerun()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_trigger = None
        st.rerun()
    
    st.divider()
    st.info("📞 Emergency: 1-800-HELP")

# Banking knowledge (simple fallback)
banking_knowledge = {
    "account": "To open an account, visit any branch with ID proof and $100 minimum deposit. Account activated within 24 hours.",
    "open account": "To open an account, visit any branch with ID proof and $100 minimum deposit. Account activated within 24 hours.",
    "card": "For lost or stolen cards, call 1-800-HELP immediately to block. Replacement arrives in 5-7 business days.",
    "lost": "🚨 LOST CARD: Call 1-800-HELP immediately to block your card. You have zero liability if reported within 3 days.",
    "loan": "Personal loans: up to $50,000 at 10.99% APR. Home loans: up to $1M at 8.5% APR. Auto loans: up to $100,000 at 9.5% APR.",
    "rates": "Savings: 3.5%, Fixed Deposit (1 year): 6.5%, Personal Loan from 10.99%, Home Loan from 8.5%.",
    "branch": "Downtown: 123 Main St, Mon-Fri 9AM-6PM, Sat 9AM-2PM. Westside: 456 Oak Ave, Mon-Fri 9AM-7PM.",
    "hours": "Downtown: Mon-Fri 9AM-6PM, Sat 9AM-2PM. Westside: Mon-Fri 9AM-7PM. Airport: Daily 7AM-10PM.",
    "fraud": "Report fraud at 1-800-HELP immediately. Freeze cards via mobile app. Zero liability within 3 days.",
    "balance": "Check balance via Mobile App, Internet Banking, ATM, or SMS 'BAL' to 56789. Minimum balance: $100.",
    "transfer": "ATM: $500/day, POS: $2000/day, Online: $5000/day, International: $2000/day + 2.5% fee."
}

def get_simple_response(query):
    """Fallback response using keyword matching"""
    query_lower = query.lower()
    for key, response in banking_knowledge.items():
        if key in query_lower:
            return response, "🔵 [FALLBACK MODE]"
    
    # Default response
    return "I can help you with accounts, cards, loans, branches, and more. Please ask a specific question or call 1-800-HELP.", "🔵 [FALLBACK MODE]"

def get_ai_response(query):
    """AI response using OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful banking assistant. Be concise and professional. If asked non-banking questions, you can answer briefly but remind them you're a banking assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content, "🟢 [AI MODE]"
    except Exception as e:
        # Fallback to simple response if AI fails
        resp, _ = get_simple_response(query)
        return resp + f"\n\n(Note: AI failed: {str(e)})", "🔴 [AI ERROR - Using Fallback]"

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "mode" in msg:
            st.caption(msg["mode"])
        st.write(msg["content"])

# Handle input trigger from buttons
if st.session_state.input_trigger:
    prompt = st.session_state.input_trigger
    st.session_state.input_trigger = None
    
    # Process the message
    with st.chat_message("assistant"):
        with st.spinner("Thinking..." if st.session_state.using_ai else "Searching..."):
            # Check for urgent keywords
            urgent = any(word in prompt.lower() for word in ['lost', 'stolen', 'fraud', 'emergency'])
            
            # Get response based on mode
            if st.session_state.using_ai:
                response, mode_indicator = get_ai_response(prompt)
            else:
                response, mode_indicator = get_simple_response(prompt)
            
            # Add urgent prefix if needed
            if urgent:
                response = "🚨 **URGENT**\n\n" + response + "\n\n📞 **Please call 1-800-HELP immediately!**"
            
            # Show mode indicator
            st.caption(mode_indicator)
            st.write(response)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "mode": mode_indicator
            })

# Chat input
if prompt := st.chat_input("Ask about banking..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..." if st.session_state.using_ai else "Searching..."):
            # Check for urgent keywords
            urgent = any(word in prompt.lower() for word in ['lost', 'stolen', 'fraud', 'emergency'])
            
            # Get response based on mode
            if st.session_state.using_ai:
                response, mode_indicator = get_ai_response(prompt)
            else:
                response, mode_indicator = get_simple_response(prompt)
            
            # Add urgent prefix if needed
            if urgent:
                response = "🚨 **URGENT**\n\n" + response + "\n\n📞 **Please call 1-800-HELP immediately!**"
            
            # Show mode indicator
            st.caption(mode_indicator)
            st.write(response)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "mode": mode_indicator
            })