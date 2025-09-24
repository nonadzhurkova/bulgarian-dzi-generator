"""
PDF Processor for extracting questions from DZI matura exams
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any
import PyPDF2
import fitz  # PyMuPDF
import pdfplumber

class MaturaPDFProcessor:
    """Processor for DZI matura PDF files"""
    
    def __init__(self):
        self.patterns = {
            'multiple_choice': r'(\d+)\.\s*(.+?)\s*A\)\s*(.+?)\s*B\)\s*(.+?)\s*C\)\s*(.+?)\s*D\)\s*(.+?)(?=\d+\.|$)',
            'multiple_choice_bg': r'(\d+)\.\s*(.+?)\s*А\)\s*(.+?)\s*Б\)\s*(.+?)\s*В\)\s*(.+?)\s*Г\)\s*(.+?)(?=\d+\.|$)',
            'short_answer': r'(\d+)\.\s*(.+?)(?=\d+\.|$)',
            'essay': r'(\d+)\.\s*(.+?)(?=\d+\.|$)',
            'lexical_error': r'(\d+)\.\s*В листа за отговори запишете САМО паронима, с който да поправите лексикалната грешка в изречението\.\s*(.+?)(?=\d+\.|$)',
            'word_choice': r'(\d+)\.\s*За всяко празно място изберете УМЕСТНАТА ДУМА и я запишете срещу съответната буква в листа за отговори\.\s*(.+?)(?=\d+\.|$)',
            'grammar_correction': r'(\d+)\.\s*В листа за отговори запишете правилната за изречението форма на думата, поставена в скоби\.\s*(.+?)(?=\d+\.|$)',
            'simple_question': r'(\d+)\.\s*([^\.]+\.\s*[^\.]+\.)(?=\d+\.|$)',
            'word_correction': r'(\d+)\.\s*В кой ред думата\s*(.+?)\s*е изписана правилно\?'
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        # Try pdfplumber first (best for structured text)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        # Fallback to PyMuPDF
        if not text:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            except Exception as e:
                print(f"PyMuPDF failed: {e}")
        
        # Fallback to PyPDF2
        if not text:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 failed: {e}")
        
        return text
    
    def clean_question_text(self, text: str) -> str:
        """Clean question text from administrative parts"""
        # Remove administrative parts
        text = re.sub(r'до \d+\. включително отбелязвайте в листа за отговори\.?\s*', '', text)
        text = re.sub(r'МИНИСТЕРСТВО НА ОБРАЗОВАНИЕТО И НАУКАТА.*?ЧАСТ \d+.*?Време за работа.*?', '', text, flags=re.DOTALL)
        text = re.sub(r'Отговорите на задачите от \d+\. до \d+\. включително отбелязвайте в листа за отговори\.\s*', '', text)
        
        # Clean extra newlines and spaces
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()
        
        return text
    
    def extract_context_texts(self, text: str) -> Dict[str, str]:
        """Extract context texts (ТЕКСТ 1, ТЕКСТ 2) from the PDF"""
        texts = {}
        
        # Find ТЕКСТ 1
        text1_match = re.search(r'ТЕКСТ 1\s*(.+?)(?=ТЕКСТ 2|$)', text, re.DOTALL)
        if text1_match:
            texts['text_1'] = text1_match.group(1).strip()
        
        # Find ТЕКСТ 2
        text2_match = re.search(r'ТЕКСТ 2\s*(.+?)(?=ТЕКСТ 1|$)', text, re.DOTALL)
        if text2_match:
            texts['text_2'] = text2_match.group(1).strip()
        
        return texts
    
    def parse_matura_questions(self, text: str) -> List[Dict[str, Any]]:
        """Parse questions from matura text"""
        questions = []
        
        # Extract context texts first
        texts = self.extract_context_texts(text)
        
        # Improved pattern for multiple choice questions
        improved_pattern = r'(\d+)\.\s*([^А-Г]+?)\s*А\)\s*([^\n]+?)\s*Б\)\s*([^\n]+?)\s*В\)\s*([^\n]+?)\s*Г\)\s*([^\n]+?)(?=\n\s*\d+\.|$)'
        
        # Find multiple choice questions with Bulgarian letters
        mc_matches = re.findall(improved_pattern, text, re.DOTALL)
        for match in mc_matches:
            question_num, question_text, option_a, option_b, option_c, option_d = match
            question_number = int(question_num.strip())
            
            # Skip problematic questions (context-based and open-ended)
            if question_number in [14, 15, 16, 17, 18, 19, 20, 21, 40, 41]:
                continue
            
            # Skip questions that require context texts (ТЕКСТ 1, ТЕКСТ 2)
            if question_number in range(14, 22):
                continue
            
            # Skip open-ended questions (essays and complex tasks)
            if question_number in [40, 41]:
                continue
            
            # Clean question text
            clean_question = self.clean_question_text(question_text)
            
            # Clean options
            options = [
                option_a.strip(),
                option_b.strip(),
                option_c.strip(),
                option_d.strip()
            ]
            
            question_data = {
                'type': 'multiple_choice',
                'number': question_num.strip(),
                'question': clean_question,
                'options': options,
                'correct_answer': None,
                'points': 1
            }
            
            # Add context texts for questions 14-21 (even though we skip them)
            if question_number in range(14, 22):
                question_data['context_texts'] = texts
            
            questions.append(question_data)
        
        return questions
    
    def extract_answers(self, text: str) -> Dict[str, str]:
        """Extract answers from text"""
        answers = {}
        
        # Answer patterns
        answer_patterns = [
            r'(\d+)\s*[\.:]\s*([А-Г])\s*',
            r'(\d+)\s*[\.:]\s*([A-D])\s*',
            r'(\d+)\s+([А-Г])\s+',
            r'(\d+)\s+([A-D])\s+',
            r'Въпрос\s*(\d+)\s*[\.:]\s*([А-Г])',
            r'Въпрос\s*(\d+)\s*[\.:]\s*([A-D])'
        ]
        
        for pattern in answer_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                question_num, answer = match
                answers[question_num.strip()] = answer.strip()
        
        return answers
    
    def process_matura_file(self, pdf_path: str) -> Dict[str, Any]:
        """Process a matura file"""
        print(f"Processing file: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return {"error": "Could not extract text from PDF file"}
        
        # Extract context texts
        texts = self.extract_context_texts(text)
        
        # Parse questions
        questions = self.parse_matura_questions(text)
        
        # Extract answers
        answers = self.extract_answers(text)
        
        # Link questions with answers
        for question in questions:
            if question['number'] in answers:
                answer = answers[question['number']]
                # Map letters to options
                if answer in ['А', 'A']:
                    question['correct_answer'] = question['options'][0]
                elif answer in ['Б', 'B']:
                    question['correct_answer'] = question['options'][1]
                elif answer in ['В', 'C']:
                    question['correct_answer'] = question['options'][2]
                elif answer in ['Г', 'D']:
                    question['correct_answer'] = question['options'][3]
        
        # Extract metadata
        metadata = {
            'file_name': Path(pdf_path).name,
            'file_path': pdf_path,
            'total_questions': len(questions),
            'multiple_choice_count': len([q for q in questions if q['type'] == 'multiple_choice']),
            'short_answer_count': len([q for q in questions if q['type'] == 'short_answer']),
            'extracted_text_length': len(text),
            'context_texts_available': len(texts) > 0
        }
        
        result = {
            'metadata': metadata,
            'questions': questions,
            'context_texts': texts,
            'raw_text': text[:1000] + "..." if len(text) > 1000 else text
        }
        
        return result
    
    def save_processed_data(self, data: Dict[str, Any], output_path: str):
        """Save processed data"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to: {output_path}")
    
    def load_processed_data(self, input_path: str) -> Dict[str, Any]:
        """Load processed data"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
