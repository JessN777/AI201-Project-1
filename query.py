import gradio as gr
import threading
import time
from transform import load_and_embed_documents, retrieve
from adding_grok import generate_answer
from scrape_news import scrape

def background_scraper(interval_minutes=10):
    """Scrape new articles and re-embed every interval_minutes while app runs."""
    while True:
        time.sleep(interval_minutes * 60)
        print(f"\n[Background] Scraping for new articles...")
        new = scrape(output_dir=".", max_articles=100)
        if new > 0:
            print(f"[Background] Embedding {new} new articles...")
            load_and_embed_documents(".")
            print("[Background] Done.")

# Embed any .txt files on startup
print("Loading and embedding documents...")
load_and_embed_documents(".")
print("Ready!")

# Start background scraper thread (runs every 10 minutes)
scraper_thread = threading.Thread(target=background_scraper, args=(10,), daemon=True)
scraper_thread.start()
print("Background scraper started — will check for new articles every 10 minutes.")


def handle_query(question):
    results = retrieve(question, k=5)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
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
