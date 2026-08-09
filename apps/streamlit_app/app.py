import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Pipeline", layout="wide")
st.title("RAG Pipeline")

with st.sidebar:
    st.header("Upload document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "pptx", "txt"])
    if uploaded_file is not None and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        try:
            resp = requests.post(f"{API_BASE_URL}/documents", files=files, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            st.success(f"Uploaded — document_id={data['document_id']}, status={data['status']}")
        except requests.RequestException as exc:
            st.error(f"Upload failed: {exc}")

    st.divider()
    st.header("Check status")
    document_id = st.text_input("Document ID")
    if document_id and st.button("Check"):
        try:
            resp = requests.get(f"{API_BASE_URL}/documents/{document_id}", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.json(data)
        except requests.RequestException as exc:
            st.error(f"Lookup failed: {exc}")

st.header("Ask a question")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for entry in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(entry["query"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        if entry["citations"]:
            with st.expander(f"{len(entry['citations'])} source(s)"):
                for c in entry["citations"]:
                    st.caption(
                        f"document {c['document_id']} · chunk {c['chunk_index']}"
                        + (f" · {c['section']}" if c.get("section") else "")
                        + (f" · page {c['page']}" if c.get("page") else "")
                    )

query = st.chat_input("Ask something about your documents")
if query:
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        try:
            resp = requests.post(f"{API_BASE_URL}/rag/query", json={"query": query}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            st.write(data["answer"])
            if data["citations"]:
                with st.expander(f"{len(data['citations'])} source(s)"):
                    for c in data["citations"]:
                        st.caption(
                            f"document {c['document_id']} · chunk {c['chunk_index']}"
                            + (f" · {c['section']}" if c.get("section") else "")
                            + (f" · page {c['page']}" if c.get("page") else "")
                        )
            st.session_state.chat_history.append(
                {"query": query, "answer": data["answer"], "citations": data["citations"]}
            )
        except requests.RequestException as exc:
            st.error(f"Query failed: {exc}")
