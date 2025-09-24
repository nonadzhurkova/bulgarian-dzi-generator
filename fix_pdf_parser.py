#!/usr/bin/env python3
"""
Поправка на PDF парсера за по-добро извличане на въпроси
"""
import re
import json
from pathlib import Path

def clean_question_text(text):
    """Почиства въпроса от излишни части"""
    # Премахваме административни части
    text = re.sub(r'до \d+\. включително отбелязвайте в листа за отговори\.?\s*', '', text)
    text = re.sub(r'МИНИСТЕРСТВО НА ОБРАЗОВАНИЕТО И НАУКАТА.*?ЧАСТ \d+.*?Време за работа.*?', '', text, flags=re.DOTALL)
    text = re.sub(r'Отговорите на задачите от \d+\. до \d+\. включително отбелязвайте в листа за отговори\.\s*', '', text)
    
    # Почистваме излишни нови редове и интервали
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    
    return text

def extract_multiple_choice_questions(text):
    """Извлича въпроси с множествен избор по-добро"""
    questions = []
    
    # Подобрен патърн за множествен избор с български букви
    pattern = r'(\d+)\.\s*([^А-Г]+?)\s*А\)\s*([^\n]+?)\s*Б\)\s*([^\n]+?)\s*В\)\s*([^\n]+?)\s*Г\)\s*([^\n]+?)(?=\n\s*\d+\.|$)'
    
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        question_num, question_text, option_a, option_b, option_c, option_d = match
        question_number = int(question_num.strip())
        
        # Пропускаме проблематичните въпроси
        if question_number in [14, 15, 16, 17, 18, 19, 20, 21, 40, 41]:
            continue
        
        # Пропускаме въпроси, които изискват контекстни текстове
        if question_number in range(14, 22):
            continue
        
        # Пропускаме въпроси с отворен отговор
        if question_number in [40, 41]:
            continue
        
        # Почистваме въпроса
        clean_question = clean_question_text(question_text)
        
        # Почистваме опциите
        options = [
            option_a.strip(),
            option_b.strip(), 
            option_c.strip(),
            option_d.strip()
        ]
        
        questions.append({
            'type': 'multiple_choice',
            'number': question_num.strip(),
            'question': clean_question,
            'options': options,
            'correct_answer': None,
            'points': 1
        })
    
    return questions

def extract_answers_from_text(text):
    """Извлича отговори от текст по-добро"""
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

def fix_json_file(input_path, output_path):
    """Поправя JSON файл с по-добро парсиране"""
    print(f"Поправяне на файл: {input_path}")
    
    # Зареждаме оригиналните данни
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Извличаме суровия текст - използваме пълния текст, не само първите 1000 символа
    raw_text = data.get('raw_text', '')
    if not raw_text:
        print("Няма суров текст за обработка")
        return
    
    # Ако текстът е скъсен, опитваме да го извлечем отново от PDF
    if len(raw_text) < 2000:  # Твърде кратък
        print("Суровият текст е твърде кратък, опитваме се да го извлечем отново...")
        from src.pdf_processor import MaturaPDFProcessor
        processor = MaturaPDFProcessor()
        pdf_path = f"tests/{data['metadata']['file_name']}"
        if Path(pdf_path).exists():
            full_text = processor.extract_text_from_pdf(pdf_path)
            if full_text:
                raw_text = full_text
                print(f"Извлечен пълен текст с дължина: {len(raw_text)}")
            else:
                print("Не може да се извлече пълен текст от PDF")
                return
        else:
            print(f"PDF файлът не съществува: {pdf_path}")
            return
    
    # Извличаме въпроси с множествен избор
    mc_questions = extract_multiple_choice_questions(raw_text)
    
    # Извличаме отговори
    answers = extract_answers_from_text(raw_text)
    
    # Свързваме въпроси с отговори
    for question in mc_questions:
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
    
    # Запазваме поправените данни
    data['questions'] = mc_questions
    data['metadata']['total_questions'] = len(mc_questions)
    data['metadata']['multiple_choice_count'] = len(mc_questions)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Поправените данни са запазени в: {output_path}")
    print(f"Намерени {len(mc_questions)} въпроса с множествен избор")

if __name__ == "__main__":
    # Поправяме двата файла
    fix_json_file('data/matura_21_05_2025.json', 'data/matura_21_05_2025_fixed.json')
    fix_json_file('data/matura_2025_avgust.json', 'data/matura_2025_avgust_fixed.json')
