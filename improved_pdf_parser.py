#!/usr/bin/env python3
"""
Подобрен PDF парсер за извличане на повече въпроси
"""
import re
import json
from pathlib import Path
from src.pdf_processor import MaturaPDFProcessor

def extract_all_questions(text):
    """Извлича всички въпроси от текста"""
    questions = []
    
    # Разделяме текста на редове
    lines = text.split('\n')
    
    current_question = None
    current_options = []
    question_number = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Търсим начало на въпрос
        question_match = re.match(r'^(\d+)\.\s*(.+)$', line)
        if question_match:
            # Ако имаме предходен въпрос, го запазваме
            if current_question and question_number:
                if len(current_options) >= 4:  # Само ако има достатъчно опции
                    questions.append({
                        'type': 'multiple_choice',
                        'number': str(question_number),
                        'question': current_question,
                        'options': current_options,
                        'correct_answer': None,
                        'points': 1
                    })
            
            # Започваме нов въпрос
            question_number = int(question_match.group(1))
            current_question = question_match.group(2).strip()
            current_options = []
            
            # Пропускаме проблематичните въпроси
            if question_number in [14, 15, 16, 17, 18, 19, 20, 21, 40, 41]:
                current_question = None
                question_number = None
                continue
        
        # Търсим опции (А), Б), В), Г))
        elif current_question and question_number:
            option_match = re.match(r'^([А-Г])\)\s*(.+)$', line)
            if option_match:
                current_options.append(option_match.group(2).strip())
    
    # Запазваме последния въпрос
    if current_question and question_number and len(current_options) >= 4:
        questions.append({
            'type': 'multiple_choice',
            'number': str(question_number),
            'question': current_question,
            'options': current_options,
            'correct_answer': None,
            'points': 1
        })
    
    return questions

def extract_answers_from_text(text):
    """Извлича отговори от текст"""
    answers = {}
    
    # Търсим отговори в различни формати
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

def process_pdf_file(pdf_path):
    """Обработва PDF файл"""
    print(f"Обработване на файл: {pdf_path}")
    
    processor = MaturaPDFProcessor()
    text = processor.extract_text_from_pdf(pdf_path)
    
    if not text:
        print(f"Не може да се извлече текст от {pdf_path}")
        return None
    
    # Извличаме въпроси
    questions = extract_all_questions(text)
    
    # Извличаме отговори
    answers = extract_answers_from_text(text)
    
    # Свързваме въпроси с отговори
    for question in questions:
        if question['number'] in answers:
            answer = answers[question['number']]
            # Мапираме буквите към опциите
            if answer in ['А', 'A']:
                question['correct_answer'] = question['options'][0]
            elif answer in ['Б', 'B']:
                question['correct_answer'] = question['options'][1]
            elif answer in ['В', 'C']:
                question['correct_answer'] = question['options'][2]
            elif answer in ['Г', 'D']:
                question['correct_answer'] = question['options'][3]
    
    # Създаваме резултат
    result = {
        'metadata': {
            'file_name': Path(pdf_path).name,
            'file_path': pdf_path,
            'total_questions': len(questions),
            'multiple_choice_count': len(questions),
            'short_answer_count': 0,
            'extracted_text_length': len(text),
            'context_texts_available': False
        },
        'questions': questions,
        'context_texts': {},
        'raw_text': text[:1000] + "..." if len(text) > 1000 else text
    }
    
    return result

def main():
    """Главна функция"""
    # Обработваме двата PDF файла
    pdf_files = [
        'tests/matura-bel-21-05-2025.pdf',
        'tests/matura-po-bel-2025-avgust.pdf'
    ]
    
    for pdf_file in pdf_files:
        if Path(pdf_file).exists():
            result = process_pdf_file(pdf_file)
            if result:
                # Запазваме резултата
                output_file = f"data/{Path(pdf_file).stem}_improved.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"Обработени {len(result['questions'])} въпроси от {pdf_file}")
                print(f"Запазени в: {output_file}")
        else:
            print(f"Файлът не съществува: {pdf_file}")

if __name__ == "__main__":
    main()
