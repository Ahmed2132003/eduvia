import json
from django.http import JsonResponse
from django.shortcuts import render
import google.generativeai as genai
from Eduvia.settings import GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")  # اختر النموذج المناسب (مثل gemini-1.5-flash)

# View to handle user requests and render the chatbot page
def chatbot_page(request):
    if request.method == "POST":
        try:
            # Read request data as JSON
            body = json.loads(request.body)
            user_input = body.get("message")  # Extract the user's input message

            if user_input:  # Check if a message is provided
                # Send user input to Gemini API
                response = model.generate_content(user_input)
                response_text = response.text  # Extract the response text
                return JsonResponse({"response": response_text})
            else:
                return JsonResponse({"error": "No valid message provided"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)

    # Render the chatbot HTML page if the request is GET
    return render(request, 'chatbot/chatbot.html')