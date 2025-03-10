'''
Author: Giancarlo Crocetti, Ryan Handley, Benjamin Hannim
Application: Conversational Intelligence for Retention Optimization (CIRO)
St John's University - 2025 - All Rights Reserved
License: This code is licensed under the Apache License, Version 2.0 (the "License").
'''

import pdfplumber
import spacy
import nltk
import json
import re
from markdownify import markdownify
from keybert import KeyBERT
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

class PDFExtractor:
    def __init__(self):
        # Initialize the NLP models and other components.
        # <TURN THIS INTO A CONFIGURATION PARAMETER>
        self.spacy_model = "en_core_web_sm"
        self.nlp = None

        try:
            self.nlp = spacy.load(self.spacy_model)
        except OSError:
            self.__install_dependencies()
            self.nlp = spacy.load(self.spacy_model)

        self.kw_model = KeyBERT()
        self.summarizer = LsaSummarizer()

    def __install_dependencies(self):
        spacy.cli.download(self.spacy_model)
        nltk.download('punkt')

    def clean_text(self, text):
        """
        Cleans extracted text by fixing spacing issues, removing gibberish, and improving overall readability.
        :param text: text to clean
        :return: cleaned text
        """
        # Remove unwanted non-ASCII characters and artifacts (e.g., cid:27)
        text = re.sub(r'cid:\d+', '', text)  # Remove malformed PDF text artifacts
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace

        # Fix missing spaces between words and punctuation
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Split CamelCase words
        text = re.sub(r'(?<=\D)(?=\d)', ' ', text)  # Split text and numbers
        text = re.sub(r'(?<=\d)(?=\D)', ' ', text)  # Split numbers and text
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)  # Ensure space between letters and numbers
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)  # Ensure space between numbers and letters
        text = re.sub(r'([.,])([a-zA-Z0-9])', r'\1 \2', text)  # Ensure space after punctuation

        # Normalize dashes and special characters
        text = text.replace("\u2013", "-").replace("\u2014", " - ")  # Normalize long dashes
        text = text.replace("\u2019", "'")  # Convert fancy apostrophes to standard ones
        text = text.replace("\u2026", "...")  # Normalize ellipses

        return text.strip()

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from pdf
            :param pdf_path: full path of pdf file
            :return: a list of text object from each page of the PDF
        """
        text_data = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    cleaned_text = self.clean_text(text)
                    text_data.append({"page": i + 1, "text": cleaned_text})
        return text_data

    def convert_text_to_markdown(self, text):
        """Converts extracted text into Markdown format."""
        markdown_text = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Convert headers (Assumption: Headers are in ALL CAPS)
            if re.match(r"^[A-Z\s]+$", line) and len(line) > 3:
                markdown_text.append(f"# {line.capitalize()}\n")

            # Convert bullet points
            elif line.startswith(("-", "*", "•")):
                markdown_text.append(f"- {line.lstrip('-*•').strip()}")

            # Convert numbered lists
            elif re.match(r"^\d+\.", line):
                markdown_text.append(f"{line}")

            # Convert bold text (heuristic: words in ALL CAPS that aren't headers)
            elif re.match(r"^[A-Z\s]+$", line) and len(line.split()) < 5:
                markdown_text.append(f"**{line}**")

            else:
                markdown_text.append(line)

        return "\n".join(markdown_text)

    def extract_keywords(self, text, num_keywords=10, n_gram_range=(1, 2), min_words=5):
        """
        Extracts relevant keywords from text using NLP and KeyBERT.
        These keywords will be used to improve search quality.
            :param text: raw text to convert
            :param num_keywords: number of keywords to extract
            :param n_gram_range: n-gram range to extract (usually (1,2))
            :param min_words: minimum number of words in the document for proceeding
            :return: list of extracted keywords
        """
        # Ensure we have enough text ...
        if len(text.split()) < min_words:
            return {"keywords": [], "categories": []}

        # Use KeyBERT to extract keywords
        keywords = self.kw_model.extract_keywords(
            text, keyphrase_ngram_range=n_gram_range, stop_words="english", top_n=num_keywords
        )
        keywords = [kw[0] for kw in keywords]  # Extract keyword strings

        # Use spaCy for named entity recognition (NER) to extract categories
        doc = self.nlp(text)
        categories = list(
            set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "NORP", "PRODUCT", "EVENT"]])
        )

        return {"keywords": keywords, "categories": categories}

    def summarize_text(self, text, num_sentences=2):
        """
        Summarizes text using LSA-based summarization.
        :param text: raw text to convert
        :param num_sentences: length of the summarized text in sentences
        :return: summarized text
        """
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary_sentences = self.summarizer(parser.document, num_sentences)
        return " ".join([str(sentence) for sentence in summary_sentences])

    def process_pdf(self, pdf_path):
        """
        Main processing methods
        :param pdf_path: full path of pdf file
        :return: Complex JSON of processed PDF
        """
        text_data = self.extract_text_from_pdf(pdf_path)

        sections = []
        full_text = ""

        for item in text_data:
            page_number = item["page"]
            text = item["text"]

            # Convert text to Markdown
            markdown_text = self.convert_text_to_markdown(text)

            # Extract keywords and categories for the section
            metadata = self.extract_keywords(text)

            # Generate section summary
            summary = self.summarize_text(text, num_sentences=3)

            section = {
                "page": page_number,
                "content": markdown_text,
                "summary": summary,
                "metadata": {
                    "source": "PDF",
                    "page": page_number,
                    "keywords": metadata["keywords"],
                    "categories": metadata["categories"]
                }
            }

            sections.append(section)
            full_text += " " + text  # Aggregate full text for document-level analysis

        # Extract higher-level metadata for the entire document
        global_metadata = self.extract_keywords(full_text)

        # Generate full document summary
        document_summary = self.summarize_text(full_text, num_sentences=5)

        # Construct JSON structure
        json_data = {
            "document_metadata": {
                "source": pdf_path,
                "total_pages": len(text_data),
                "summary": document_summary,
                "keywords": global_metadata["keywords"],
                "categories": global_metadata["categories"]
            },
            "sections": sections
        }

        return json_data


# Unit Test
if __name__ == "__main__":
    pdf_extractor = PDFExtractor()
    pdf_path = "C:/tmp/udlg2.2-text-a11y.pdf"  # Replace with the actual PDF path

    pdf_json_data = pdf_extractor.process_pdf(pdf_path)

    # Pretty-print JSON output
    print(json.dumps(pdf_json_data, indent=4))
