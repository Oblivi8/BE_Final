from flask import Flask, render_template, request

app = Flask(__name__)

# Define your chatbot responses
chatbot_responses = {
    "Hi":"Hello,How may I help you?",
    "Hello":"Hello,How may I help you?.",
    "What is your name?": "My name is Chatbot!",
    "How are you?": "I'm doing well, thank you!",
    "What can you do?": "I can answer your questions. Feel free to ask!",
    "What are the courses offered?": " From UG to PG variety of cources are offered like -B.E, M.B.A ,M.E, PhD",
    "What is the fee structure?":"Please visit college webite for more info"
    # Add more responses as needed
}

@app.route('/')
def index():
    return render_template('login_register_page.html')

# Handle chatbot requests
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.form['message']
    response = chatbot_responses.get(user_message, "I'm sorry, I don't understand.")
    return response


if(__name__ == "__main__"):
    app.run(debug=True)