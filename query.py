import gradio as gr
from transform import load_and_embed_documents, retrieve
from adding_grok import generate_answer

# Embed any new .txt files in the current directory on startup
print("Loading and embedding documents...")
load_and_embed_documents(".")
print("Ready!")


def handle_query(question):
    # Retrieve top-5 relevant chunks from ChromaDB
    results = retrieve(question, k=5)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    # Generate answer with Groq LLM
    output = generate_answer(question, chunks, sources)

    source_list = "\n".join(set(sources))
    return output["answer"], source_list


with gr.Blocks() as demo:
    gr.Markdown("## Club World Cup Guide")
    question = gr.Textbox(label="Ask a question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=3)
    btn.click(handle_query, inputs=question, outputs=[answer, sources])

demo.launch()
