from flask import Flask, request, jsonify
import json

app = Flask(__name__)

questions =["""
            1. Can you elaborate on your experience with vector databases like Chroma or Cosmos DB? Have you worked with embeddings and querying them effectively?""", 
            """
            2. The job description mentions the use of JavaScript for front-end/back-end tasks. Could you share any experience you have with JavaScript frameworks such as React or Node.js?""",
            """
            3. Could you provide more details about your proficiency in SQL? Have you written queries for data integration and management in your past projects?""",
            """
            4. The role requires collaboration with cross-functional teams. Can you describe a situation where you effectively worked with product owners or developers to translate business requirements into AI-powered features?""",
            """
            5. Have you had any experience with CI/CD pipelines or containerization tools like Docker and Kubernetes? How comfortable are you with these technologies?""",
            """
            6. The job description highlights the importance of performance monitoring. Can you share any experience you have in tracking and fine-tuning AI-driven functionalities for scalability and accuracy?""",
            """
            7. Could you provide more insight into your problem-solving approach, especially in debugging and optimizing existing AI solutions?""", 
            """
            8. The role values a strong grasp of Python fundamentals. Can you discuss your experience with Python, particularly with libraries like NumPy, Pandas, and scikit-learn?""",
            """
            9. Have you had any experience working in a start-up environment? How do you adapt to fast-paced and evolving work settings?""",
            """
            10. The job description mentions cloud platforms like Azure and AWS. While you have experience with GCP, could you discuss any exposure you have had to other cloud services?""",
            """
            11. Can you elaborate on your experience with data handling and transformation? How do you ensure high-quality input to AI models?""",
            """
            12. The role requires maintaining clear documentation and adhering to best practices. Can you share examples of how you have documented your work in past projects?""",
            """
            13. How do you approach continuous learning and skill development in the AI/ML field? Can you provide examples of how you have kept up with industry best practices?""", 
            """
            14. The job description mentions a resourceful approach to debugging. Can you share a challenging problem you faced in your projects and how you resolved it?""",
            """
            15. Collaboration and communication are key for this role. Can you provide examples of how you have effectively communicated and collaborated with a diverse team in your previous roles?"""]

questions = questions[:5]
current_index = 0
answers = []
def format_response(text):
    response = {
            "fulfillmentResponse": {
                "messages": [
                    {
                        "text": {
                            "text": [text]
                        }
                    }
                ]
            }
    }

    return response

@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    global current_index
    
    body = request.get_json()
    pretty_body = json.dumps(body, indent=4)
    

    page_info = body.get("pageInfo", {})
    session_info = body.get("sessionInfo", {})
    user_answer = body.get("intentInfo", {}).get("parameters", {}).get("user_input", {}).get("originalValue", "")
    current_intent = session_info.get("parameters",{}).get("$request.generative.subintent1", "")
    current_page = page_info.get('displayName', "")

    if current_index > 0:
        answers.append(user_answer)

    if current_index < len(questions)-1:
        if current_page == 'Entry Page' and current_intent == "":
            current_index = 0
            text = questions[0]
            response = format_response(text)
        elif current_page == 'Entry Page' and current_intent == "answer":
            current_index += 1
            text = questions[current_index]
            response = format_response(text)
        elif current_page == 'Entry Page' and current_intent == "skip":
            current_index += 1
            text = questions[current_index]
            response = format_response(text)
        elif current_page == 'Answer Page' and current_index == "end":
            text = "Thank you for joing the questionnare."
            response = format_response(text)
    else:
        text = "Thank you for joining the session. You responses are recorded and your CV is getting curated."
        current_index = 0
        response = format_response(text)
        body = request.get_json()
        user_answer = body.get("intentInfo", {}).get("parameters", {}).get("user_input", {}).get("originalValue", "")
        answers.append(user_answer)

    return jsonify(response), 200

@app.route('/', methods=['GET'])
def home():
    temp = answers
    return f"{temp}"

if __name__ == '__main__':
    app.run(debug=True)