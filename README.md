# Document Similarity Analyzer

## Project Overview

This project implements a Document Similarity Analyzer using the FLAN-T5 model to compare paragraphs from a source document against a collection of reference documents. It identifies the most similar chunks of text from the references and exports the results to a formatted Word document.

## Features

- Extracts text from PDF and DOCX files
- Preprocesses and chunks text for analysis
- Utilizes FLAN-T5 model for generating text embeddings
- Computes cosine similarity between paragraphs and reference chunks
- Exports results to a well-formatted Word document
- Provides reference usage statistics

## Installation

1. Clone the repository:
git clone https://github.com/TheRock87/document-similarity-analyzer.git
cd document-similarity-analyzer

3. Install the required packages:
pip install -r requirements.txt

## Usage

1. Place your reference documents (PDF or DOCX) in a folder named `references`
2. Create a `Paragraphs.txt` file containing the paragraphs you want to analyze
3. Run the script:
4. The results will be exported to `similarity_results.docx`

## How It Works

1. The script loads reference documents and source paragraphs
2. It uses the FLAN-T5 model to generate embeddings for each chunk of text
3. Cosine similarity is computed between each paragraph and reference chunks
4. The top 3 most similar chunks are identified for each paragraph
5. Results are formatted and exported to a Word document

## Future Improvements

- Add support for more document formats
- Implement a user interface for easier interaction
- Optimize performance for larger document sets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
