import json
from bs4 import BeautifulSoup

def parse_html_interview_to_json(html_path, question_keyword='Q:', answer_keyword='Notes:'):
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    result = {}
    current_heading = None

    elements = soup.body.find_all(['h3', 'p'])
    it = iter(elements)
    for element in it:
        if element.name == 'h3':
            # For headings, initialize a new list of Q&As
            current_heading = element.get_text(strip=True)
            result[current_heading] = []
        elif current_heading and element.name == 'p' and question_keyword in element.get_text():
            # Capture the question text
            question = element.get_text().replace(question_keyword, '', 1).strip()

            # Move to the next elements to find the answer
            answer_found = False
            while True:
                next_element = next(it, None)
                if next_element is None or next_element.name == 'h3':
                    # Break if we reach the end or a new heading
                    break
                if next_element.name == 'p' and answer_keyword in next_element.get_text():
                    # We found the answer element
                    answer = next_element.get_text().replace(answer_keyword, '', 1).strip()
                    answer_found = True
                    break

            if not answer_found:
                answer = "No answer provided."

            # Append the question and answer under the current heading
            result[current_heading].append({'question': question, 'answer': answer})

    # Convert the result dictionary to JSON
    return result

# Specify the path to your HTML file
# html_path = "AMSQuestionnaireandK8sMaturityAssessmentforGr.html"
# json_result = parse_html_to_json(html_path, question_keyword='Q:', answer_keyword='Notes:')

# # Print the JSON result
# print(json_result)

# with open('result.json', 'w', encoding='utf-8') as json_file:
#     json_file.write(json_result)
