from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class BankingResponder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(api_key=api_key, temperature=0.3, model="gpt-3.5-turbo")
        self.qa_chain = None
    
    def create_chain(self, retriever):
        prompt = PromptTemplate(
            template="""Use the context to answer the question.

Context: {context}
Question: {question}

Answer briefly and helpfully:""",
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        return self.qa_chain
    
# Make sure to add this import at the VERY TOP of your app.py file
from openai import OpenAI

def get_ai_response(query):
    """AI response using the new OpenAI client (v1.0.0+)"""
    try:
        # Initialize the client inside the function
        client = OpenAI(api_key=st.session_state.api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful banking assistant. Be concise and professional. If asked non-banking questions, you can answer briefly but remind them you're a banking assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=200
        )
        # Access the response correctly
        return response.choices[0].message.content, "🟢 [AI MODE]"
    except Exception as e:
        # Fallback to simple response if AI fails
        resp, _ = get_simple_response(query)
        return resp + f"\n\n(Note: AI failed: {str(e)})", "🔴 [AI ERROR - Using Fallback]"