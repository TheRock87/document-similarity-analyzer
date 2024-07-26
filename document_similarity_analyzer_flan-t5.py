{"metadata":{"kernelspec":{"language":"python","display_name":"Python 3","name":"python3"},"language_info":{"name":"python","version":"3.10.13","mimetype":"text/x-python","codemirror_mode":{"name":"ipython","version":3},"pygments_lexer":"ipython3","nbconvert_exporter":"python","file_extension":".py"},"kaggle":{"accelerator":"none","dataSources":[{"sourceId":9027411,"sourceType":"datasetVersion","datasetId":5431642},{"sourceId":9027412,"sourceType":"datasetVersion","datasetId":5431672}],"dockerImageVersionId":30747,"isInternetEnabled":true,"language":"python","sourceType":"script","isGpuEnabled":false}},"nbformat_minor":4,"nbformat":4,"cells":[{"cell_type":"code","source":"# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:26.602390Z\",\"iopub.execute_input\":\"2024-07-24T19:19:26.602981Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.857550Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:26.602948Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.856368Z\"}}\n# Install required libraries\n!pip install nltk PyPDF2 python-docx transformers torch\n\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.860445Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.860925Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.882593Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.860878Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.881473Z\"}}\nimport os\nimport re\nimport nltk\nimport torch\nimport numpy as np\nfrom docx import Document\nimport PyPDF2\nimport ast\nfrom tqdm import tqdm\nimport time\nfrom transformers import T5Tokenizer, T5EncoderModel\nfrom sklearn.metrics.pairwise import cosine_similarity\nfrom docx.shared import Pt, RGBColor\nfrom docx.enum.text import WD_PARAGRAPH_ALIGNMENT\nfrom collections import defaultdict\n# Download required NLTK data\nnltk.download('punkt')\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.883955Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.884362Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.889660Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.884324Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.888575Z\"}}\ndef preprocess_text(text):\n    # Remove special characters and extra whitespace\n    #text = re.sub(r'[^\\w\\s]', '', text)\n    text = re.sub(r'\\s+', ' ', text).strip()\n    return text\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.892756Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.893224Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.903073Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.893183Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.901926Z\"}}\ndef extract_text_from_pdf(pdf_path):\n    with open(pdf_path, 'rb') as file:\n        reader = PyPDF2.PdfReader(file)\n        text = ''\n        for page in reader.pages:\n            text += page.extract_text()\n    return text\n\ndef extract_text_from_docx(docx_path):\n    doc = Document(docx_path)\n    return ' '.join([paragraph.text for paragraph in doc.paragraphs])\n\ndef split_into_chunks(text, chunk_size=100):\n    words = text.split()\n    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.904468Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.904858Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.921067Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.904812Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.919944Z\"}}\ndef load_documents(folder_path):\n    documents = []\n    for filename in os.listdir(folder_path):\n        file_path = os.path.join(folder_path, filename)\n        if filename.endswith('.pdf'):\n            text = extract_text_from_pdf(file_path)\n        elif filename.endswith('.docx'):\n            text = extract_text_from_docx(file_path)\n        else:\n            continue\n        preprocessed_text = preprocess_text(text)\n        chunks = split_into_chunks(preprocessed_text)\n        documents.append((filename, chunks))\n    return documents\n\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.922398Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.922734Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.932336Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.922702Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.931265Z\"}}\ndef load_paragraphs(file_path):\n    with open(file_path, 'r') as file:\n        content = file.read()\n    paragraphs = ast.literal_eval(content)\n    return [preprocess_text(p) for p in paragraphs if p.strip()]\n\ndef get_flan_t5_embedding(text, tokenizer, model):\n    inputs = tokenizer(text, return_tensors=\"pt\", truncation=True, padding=True, max_length=512)\n    inputs = {k: v.to(model.device) for k, v in inputs.items()}\n    with torch.no_grad():\n        outputs = model(**inputs)\n    return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.933848Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.934173Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.959571Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.934125Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.958328Z\"}}\ndef find_similarities(tokenizer, model, paragraphs, documents, top_n=3, similarity_threshold=0.5):\n    results = []\n    total_paragraphs = len(paragraphs)\n    reference_usage = defaultdict(int)\n    start_time = time.time()\n    \n    for i, paragraph in enumerate(tqdm(paragraphs, desc=\"Processing paragraphs\")):\n        paragraph_embedding = get_flan_t5_embedding(paragraph, tokenizer, model)\n        all_similarities = []\n        \n        for doc_name, chunks in documents:\n            chunk_embeddings = [get_flan_t5_embedding(chunk, tokenizer, model) for chunk in chunks]\n            similarities = cosine_similarity([paragraph_embedding], chunk_embeddings)[0]\n            all_similarities.extend([(doc_name, chunk, sim) for chunk, sim in zip(chunks, similarities)])\n        \n        # Sort by similarity\n        all_similarities.sort(key=lambda x: -x[2])\n        \n        top_matches = []\n        used_references = set()\n        \n        # First match: allow up to 2 uses of a reference\n        for doc_name, chunk, sim in all_similarities:\n            if len(top_matches) >= 1:\n                break\n            if reference_usage[doc_name] < 2:\n                top_matches.append((doc_name, chunk, sim))\n                reference_usage[doc_name] += 1\n                used_references.add(doc_name)\n        \n        # Remaining matches: ensure unique references\n        for doc_name, chunk, sim in all_similarities:\n            if len(top_matches) >= top_n:\n                break\n            if doc_name not in used_references:\n                top_matches.append((doc_name, chunk, sim))\n                reference_usage[doc_name] += 1\n                used_references.add(doc_name)\n        \n        # If we still don't have enough matches, add the next best ones\n        while len(top_matches) < top_n:\n            for doc_name, chunk, sim in all_similarities:\n                if (doc_name, chunk, sim) not in top_matches:\n                    top_matches.append((doc_name, chunk, sim))\n                    reference_usage[doc_name] += 1\n                    break\n        \n        results.append((paragraph, top_matches))\n        \n        # Estimate time remaining\n        elapsed_time = time.time() - start_time\n        time_per_paragraph = elapsed_time / (i + 1)\n        estimated_time_left = (total_paragraphs - i - 1) * time_per_paragraph\n        print(f\"\\rEstimated time remaining: {estimated_time_left:.2f} seconds\", end=\"\")\n    \n    print(\"\\n\")  # New line after progress updates\n    \n    # Print reference usage statistics\n    print(\"\\nReference Usage Statistics:\")\n    for doc_name, count in reference_usage.items():\n        print(f\"{doc_name}: used {count} times\")\n    \n    # Check if all references were used\n    unused_references = [doc_name for doc_name, count in reference_usage.items() if count == 0]\n    if unused_references:\n        print(\"\\nWarning: The following references were not used:\")\n        for doc_name in unused_references:\n            print(doc_name)\n    else:\n        print(\"\\nAll references were used at least once.\")\n    \n    return results\n\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:19:40.960920Z\",\"iopub.execute_input\":\"2024-07-24T19:19:40.961339Z\",\"iopub.status.idle\":\"2024-07-24T19:19:40.974346Z\",\"shell.execute_reply.started\":\"2024-07-24T19:19:40.961309Z\",\"shell.execute_reply\":\"2024-07-24T19:19:40.973382Z\"}}\ndef export_to_word(results, output_file):\n    doc = Document()\n    \n    # Add title\n    title = doc.add_heading('Document Similarity Comparison Results', level=0)\n    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER\n    \n    for i, (paragraph, matches) in enumerate(results):\n        # Add paragraph header\n        para_header = doc.add_heading(f'Paragraph {i+1}', level=1)\n        para_header.style.font.color.rgb = RGBColor(0, 0, 139)  # Dark Blue\n        \n        # Add original paragraph\n        doc.add_paragraph(paragraph).style.font.size = Pt(11)\n        \n        # Add matches header\n        doc.add_heading('Top 3 Similar Chunks:', level=2).style.font.color.rgb = RGBColor(0, 100, 0)  # Dark Green\n        \n        for j, (doc_name, chunk, similarity) in enumerate(matches):\n            # Add match details\n            match_para = doc.add_paragraph(style='List Bullet')\n            match_para.add_run(f'Match {j+1}:').bold = True\n            match_para.add_run(f' (Similarity: {similarity:.2%})').italic = True\n            match_para.add_run(f'\\nDocument: {doc_name}').font.color.rgb = RGBColor(139, 0, 0)  # Dark Red\n            match_para.add_run(f'\\nChunk: {chunk}')\n        \n        doc.add_paragraph()  # Add space between paragraphs\n    \n    doc.save(output_file)\n\n\n# %% [code] {\"execution\":{\"iopub.status.busy\":\"2024-07-24T19:23:51.613393Z\",\"iopub.execute_input\":\"2024-07-24T19:23:51.614356Z\",\"iopub.status.idle\":\"2024-07-24T19:46:29.722267Z\",\"shell.execute_reply.started\":\"2024-07-24T19:23:51.614317Z\",\"shell.execute_reply\":\"2024-07-24T19:46:29.721201Z\"}}\n# Main execution\ndef main():\n    # Set paths\n    documents_folder = '/kaggle/input/references'  # Adjust this path for Kaggle\n    paragraphs_file = '/kaggle/input/paragraphs/Paragraphs.txt'  # Adjust this path for Kaggle\n    output_file = 'similarity_results.docx'\n\n    # Load documents and paragraphs\n    documents = load_documents(documents_folder)\n    paragraphs = load_paragraphs(paragraphs_file)\n    \n    print(f\"Loaded {len(paragraphs)} paragraphs\")\n\n\n    # Initialize FLAN-T5 tokenizer and model\n    model_name = \"google/flan-t5-large\"  # You can also use \"google/flan-t5-large\" for better performance\n    tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)\n    model = T5EncoderModel.from_pretrained(model_name)\n\n    \n    # Set padding token\n    tokenizer.pad_token = tokenizer.eos_token\n\n    \n    # Move model to GPU\n    device = torch.device(\"cuda\" if torch.cuda.is_available() else \"cpu\")\n    model.to(device)\n    \n    # Find similarities\n    results = find_similarities(tokenizer, model, paragraphs, documents, top_n=3)\n\n\n    # Export results to Word document\n    export_to_word(results, output_file)\n\n    print(f\"Results exported to {output_file}\")\n\nif __name__ == \"__main__\":\n    main()","metadata":{"_uuid":"da5843dd-cf82-46af-b53c-53564a162fdc","_cell_guid":"32208704-f243-431a-a06d-c87858fc8af4","collapsed":false,"jupyter":{"outputs_hidden":false},"trusted":true},"execution_count":null,"outputs":[]}]}