import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
def embed_text(text):
    """Embed text using OpenAI embeddings."""
    loader = TextLoader("data/knowledge_base.txt")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=20)
    chunks = text_splitter.split_documents(loader.load())

    embeddings = OpenAIEmbeddings()
    Chroma.from_documents(chunks, embeddings, persist_directory="data/chroma_db")


class State(BaseModel):
    """State for the agent."""
    query: str
    docs: list = []
    summary: str = ""
    response: str = ""

embeddings = OpenAIEmbeddings()
retriver = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings).as_retriever(search_kwargs={"k": 3})

client = OpenAI() # type: ignore

def retrieve_docs(state: State) -> State:
    """Retrieve documents based on user input."""
    query = state.query
    if not query:
        return state
    
    docs = retriver.invoke(query)
    return State(query=query, docs=docs)

def summarize_docs(state: State) -> State:
    """Summarize retrieved documents."""
    if not state.docs:
        return State(query=state.query, docs=state.docs, summary="No relevant documents found.")
    
    content = "\n".join(doc.page_content for doc in state.docs)

    summary = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following content: {content}"}
        ]
    ).choices[0].message.content
    
    if not summary:
        return State(query=state.query, docs=state.docs, summary="No summary generated.")
    
    return State(query=state.query, docs=state.docs, summary=summary.strip())

def generate_response(state: State) -> State:
    """Generate a response based on the summary."""
    if not state.summary:
        return State(
            query=state.query,
            docs=state.docs,
            summary=state.summary,
            response="No summary available to generate a response."
        )

    prompt = f"Based on the following summary, provide a detailed response to the query: {state.query}\n\nSummary: {state.summary}"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    ).choices[0].message.content
    
    if not response:
        return State(query=state.query, docs=state.docs, summary=state.summary, response="No response generated.")
    
    return State(query=state.query, docs=state.docs, summary=state.summary, response=response.strip())

graph = StateGraph(State)

graph.add_node("retrieve_docs", retrieve_docs)
graph.add_node("summarize_docs", summarize_docs)
graph.add_node("generate_response", generate_response)

graph.add_edge(START, "retrieve_docs")
graph.add_edge("retrieve_docs", "summarize_docs")
graph.add_edge("summarize_docs", "generate_response")
graph.add_edge("generate_response", END)

agent = graph.compile()

query = "how to reset password"
result = agent.invoke({"query": query})
print("Response:", result["response"])