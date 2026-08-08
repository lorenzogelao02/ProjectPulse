import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.config import DATA_DIR
from src.ingestion import MarkdownParser, PDFParser, GitHubRepositoryConnector
from src.vector_store import VectorStoreManager, HybridRetriever
from src.agent import ProjectCoordinatorAgent

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="ProjectPulse AI - Production RAG Co-Pilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Objects
if "vector_store" not in st.session_state:
    vs = VectorStoreManager()
    sample_dir = DATA_DIR / "sample_project"
    if sample_dir.exists():
        for file_path in sample_dir.glob("*.md"):
            chunks = MarkdownParser.parse_file(file_path)
            vs.add_chunks(chunks)
    st.session_state.vector_store = vs

if "retriever" not in st.session_state:
    st.session_state.retriever = HybridRetriever(st.session_state.vector_store)

if "agent" not in st.session_state:
    st.session_state.agent = ProjectCoordinatorAgent(st.session_state.retriever)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **ProjectPulse AI**! Ask any technical or project architecture question about your documentation."}
    ]

# Sidebar
with st.sidebar:
    st.title("⚡ ProjectPulse AI")
    st.caption("AI-Driven Project Coordination & Production RAG System")
    st.markdown("---")
    
    # Active LLM Indicator
    if os.getenv("GROQ_API_KEY"):
        st.success("🟢 **LLM Active:** Groq Cloud (`llama-3.3-70b`)")
    elif os.getenv("OPENAI_API_KEY"):
        st.success("🟢 **LLM Active:** OpenAI (`gpt-4o-mini`)")
    else:
        st.warning("🟠 **LLM Active:** Local Rule-based Fallback")
        
    st.markdown("---")
    st.metric("Total Indexed Chunks", len(st.session_state.vector_store.chunks))
    
    st.markdown("---")
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you?"}
        ]
        st.rerun()

# Main Application Tabs
tab_chat, tab_ingest, tab_risks = st.tabs(["💬 Q&A Chat Assistant", "🐙 GitHub Ingestion", "⚠️ Project Risk Radar"])

# ---------------------------------------------------------
# TAB 1: Q&A Chat Assistant
# ---------------------------------------------------------
with tab_chat:
    st.header("Project Documentation Q&A")
    st.write("Ask questions about code architecture, technical decisions, or open tasks with exact file & line number citations.")
    
    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander("📚 View Document Citations"):
                    for idx, c in enumerate(msg["citations"], start=1):
                        st.markdown(
                            f"**{idx}. `{c['filename']}` ({c['lines']})** — *{c['section']}*\n"
                            f"  - Score: `{c['confidence_score']}` | Source: `{c['source_type']}`"
                        )
                        
    # Chat Input Box
    if user_query := st.chat_input("Ask a question about the project..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing hybrid vector & sparse BM25 index..."):
                response = st.session_state.agent.answer_query(user_query)
                st.markdown(response["answer"])
                
                if response["citations"]:
                    with st.expander("📚 View Document Citations"):
                        for idx, c in enumerate(response["citations"], start=1):
                            st.markdown(
                                f"**{idx}. `{c['filename']}` ({c['lines']})** — *{c['section']}*\n"
                                f"  - Confidence Score: `{c['confidence_score']}` | Source: `{c['source_type']}`"
                            )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "citations": response["citations"]
                })

# ---------------------------------------------------------
# TAB 2: Document & GitHub Ingestion
# ---------------------------------------------------------
with tab_ingest:
    col1, col2 = st.columns(2)

    with col1:
        st.header("📄 Upload PDF or Markdown")
        st.write("Drag and drop PDF files or Markdown docs to index them into vector storage.")

        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "md"],
            accept_multiple_files=True,
            help="Upload PDF or Markdown files to index into ProjectPulse AI."
        )

        if st.button("📤 Process & Index Uploaded Files"):
            if uploaded_files:
                total_new_chunks = 0
                with st.spinner("Processing uploaded files..."):
                    for uploaded_file in uploaded_files:
                        file_bytes = uploaded_file.read()
                        if uploaded_file.name.endswith(".pdf"):
                            chunks = PDFParser.parse_pdf_bytes(uploaded_file.name, file_bytes)
                        else:
                            text = file_bytes.decode("utf-8", errors="ignore")
                            temp_path = DATA_DIR / uploaded_file.name
                            temp_path.write_text(text, encoding="utf-8")
                            chunks = MarkdownParser.parse_file(temp_path)

                        st.session_state.vector_store.add_chunks(chunks)
                        total_new_chunks += len(chunks)

                st.success(f"Successfully processed and indexed {total_new_chunks} chunks from {len(uploaded_files)} file(s)!")
                st.rerun()
            else:
                st.warning("Please select at least one PDF or Markdown file to upload.")

    with col2:
        st.header("🐙 Ingest GitHub Repository")
        st.write("Import README files and open issues directly into vector database from any public GitHub repo.")

        repo_input = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/techwithtim/ProductionGradeRAGPythonApp",
            help="Paste a public GitHub repo URL to automatically pull documentation."
        )

        if st.button("🚀 Ingest Repository"):
            if repo_input.strip():
                with st.spinner(f"Fetching documentation from {repo_input}..."):
                    try:
                        connector = GitHubRepositoryConnector()
                        chunks = connector.fetch_repo_documents(repo_input)
                        st.session_state.vector_store.add_chunks(chunks)
                        st.success(f"Successfully indexed {len(chunks)} document chunks from GitHub!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to ingest GitHub repository: {str(e)}")
            else:
                st.warning("Please enter a valid GitHub repository URL.")


# ---------------------------------------------------------
# TAB 3: Project Risk Radar
# ---------------------------------------------------------
with tab_risks:
    st.header("Automated Project Risk Radar")
    st.write("Scans indexed documentation for dependency blockers, architectural risks, and database concurrency locks.")
    
    if st.button("🔍 Run Risk Audit"):
        with st.spinner("Scanning indexed project documentation..."):
            risks = st.session_state.agent.scan_project_risks()
            if risks:
                st.subheader(f"Found {len(risks)} Potential Risk Signals")
                for r in risks:
                    st.error(f"**[{r['risk_type']}]** Source: `{r['source']}` ({r['lines']})")
                    st.caption(f"Snippet: \"{r['summary'].strip()}...\"")
            else:
                st.info("No immediate risk blockers detected in current indexed documentation.")
