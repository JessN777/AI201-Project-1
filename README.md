# AI201-Project-1
A retrieval-augmented generation (RAG) system that makes unofficial student knowledge searchable and answerable. Ask plain-language questions about professors, housing, dining, or campus life and get grounded, cited answers drawn from real student-generated content like Reddit threads.
Because I had issues with getting the API for reddit for right now, I'm just copying some of the best posts I like into a .txt file.
Since my documents are Reddit posts and comments, I chunk by individual comment rather than fixed character count. Each comment represents a complete thought, so splitting mid-comment would lose meaning. I set a minimum length of 50 characters to filter out low-value responses like 'lol' or 'agreed'.
