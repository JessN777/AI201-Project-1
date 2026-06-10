import gradio as gr

def handle_query(question):
    # retrieve chunks
    results = retrieve(question, k=5)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    
    # generate answer
    output = generate_answer(question, chunks, sources)
    
    source_list = "\n".join(set(sources))
    return output["answer"], source_list

with gr.Blocks() as demo:
    gr.Markdown("## Unofficial College Guide")
    question = gr.Textbox(label="Ask a question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=3)
    btn.click(handle_query, inputs=question, outputs=[answer, sources])

demo.launch()