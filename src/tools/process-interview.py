import re
import json

def clean_answer(answer):
    # Remove any heading information from the answer
    cleaned_answer = re.sub(r'\n.*?________________$', '', answer, flags=re.DOTALL).strip()
    return cleaned_answer

def create_json_from_qa_interview(input_file):
    questions_and_answers = []

    with open(input_file, 'r') as file:
        data = file.read()

        # Regular expressions for matching questions and answers
        question_pattern = re.compile(r'Q: (.+?)\n')
        answer_pattern = re.compile(r'Notes?: (.+?)(?=\nQ:|\Z)', re.DOTALL)

        # Find all questions
        questions = question_pattern.findall(data)
        
        # Find all answers
        answers = answer_pattern.findall(data)
        
        # Clean up answers - remove excessive whitespace/newlines and headers
        answers = [clean_answer(answer.strip()) for answer in answers]

        # Combine questions and answers
        for question, answer in zip(questions, answers):
            questions_and_answers.append({
                "question": question,
                "answer": answer
            })

    return questions_and_answers


input_file = 'AMS Questionnaire and K8s Maturity Assessment for Graybar.txt'  # Replace with your input file path
