# from datetime import datetime
# import re
# import random
# import json
# import os

# class ResponseModel:
#     def __init__(self):
#         self.conversation_history = {}
#         self.session_counts = {}
#         self.patterns = {
#             'anxiety': {
#                 'patterns': [r'anxi(ous|ety)', r'worried?', r'stress(ed|ful)', r'nervous', r'panic'],
#                 'responses': [
#                     "I notice you're feeling anxious. Anxiety often stems from the fear of the unknown or from overwhelming stress. One thing that can really help is grounding exercises. Try the 5-4-3-2-1 method: look around and identify five things you can see, four things you can touch, three things you can hear, two things you can smell, and one thing you can taste. This helps bring you back to the present moment and distracts from anxious thoughts.",
#                     "Anxiety can feel overwhelming, but it’s important to remind yourself that it will pass. To help manage it, try deep breathing exercises. Inhale for a count of four, hold for four counts, and exhale for four counts. Focus on your breath and try to let go of any racing thoughts. You can also try progressive muscle relaxation by tensing and releasing different muscle groups from your feet to your head.",
#                     "When did you start feeling this anxiety? Often, anxiety arises when we feel out of control or when we focus on worst-case scenarios. A technique that may help is cognitive reframing—challenge the anxious thoughts by identifying any cognitive distortions, like overgeneralizing or catastrophizing. It can also help to write down your feelings and then assess whether the fears are realistic or exaggerated.",
#                     "It sounds like anxiety is really present for you right now. A grounding technique that could help is the ‘body scan’ method. Sit quietly, close your eyes, and mentally scan your body from head to toe, noticing where you feel tension. Breathe into those areas and consciously release the tension. Focusing on your body instead of your racing thoughts can help ground you in the present moment."
#                 ]
#             },
#             'depression': {
#                 'patterns': [r'depress(ed|ion)', r'sad', r'down', r'hopeless', r'unmotivated'],
#                 'responses': [
#                     "I hear how difficult things are right now. Depression can weigh heavily on you, making even small tasks feel impossible. One important step in coping with depression is to set very small, achievable goals. Try breaking down tasks into the smallest steps, such as simply getting out of bed or making a cup of tea. Each small success can help shift your mindset, giving you a sense of accomplishment. You might also want to explore self-compassion practices, such as saying to yourself, ‘It’s okay to feel like this, and I am doing the best I can.’",
#                     "Depression can feel like a never-ending weight. A powerful tool in managing it is to incorporate daily physical activity, even if it’s just a short walk or some stretching. Exercise releases endorphins, which can naturally elevate your mood. Along with that, try to get some exposure to sunlight, as it can help regulate your sleep-wake cycle and improve your mood. Don't be too hard on yourself; small steps are better than none.",
#                     "It takes courage to share these feelings. Depression often creates a sense of isolation, but you don’t have to go through it alone. Reach out to a therapist or counselor who can help you explore and process these emotions. You might also want to explore journaling to track your thoughts. It can help you identify patterns and triggers that contribute to your feelings of sadness, and provide an outlet for expression.",
#                     "I hear the pain in your words. Finding moments of relief is important. You could try mindfulness or meditation to help detach from negative thoughts. Apps like Headspace or Calm offer guided meditations that focus on self-compassion or relaxing breathing exercises. You can also engage in creative activities like drawing or painting, as these allow you to express emotions you may not have words for. You deserve moments of peace, and taking time for yourself is an essential part of healing."
#                 ]
#             },
#             'anger': {
#                 'patterns': [r'angry?', r'mad', r'frustrat(ed|ing)', r'irritat(ed|ing)', r'upset'],
#                 'responses': [
#                     "I can hear your anger. Anger often arises when we feel disrespected or when our boundaries are crossed. A great way to process anger is through physical outlets. Try some form of exercise, whether it’s going for a run, doing yoga, or even just walking at a fast pace. Exercise helps release tension and promotes the release of feel-good chemicals called endorphins. If possible, try to channel the anger into something creative, like writing, painting, or working on a project you care about.",
#                     "It's okay to feel angry, and it’s important to acknowledge it. One thing that can help manage anger is practicing mindfulness. Focus on your breath, taking deep, slow inhales and exhales. This will help bring your attention away from the trigger and bring you back to a state of calm. Another strategy is to give yourself some space. If you feel the anger rising, try stepping away from the situation and taking a few minutes to collect your thoughts. This can prevent the anger from escalating.",
#                     "Anger often tells us something important about how we feel. If you find yourself consistently angry, it may be helpful to examine what’s underneath that anger. Are there feelings of fear, sadness, or frustration that you haven’t fully processed? Journaling can help you reflect on these emotions and identify the underlying causes. Another great tool is assertive communication. Learn to express your feelings calmly and clearly, without aggression, to communicate what you need without escalating the situation.",
#                     "Your anger is valid, and finding healthy ways to express it is essential. Try to practice relaxation techniques like progressive muscle relaxation, where you tense and release muscles in your body, starting with your toes and working your way up to your head. This can help reduce the physiological effects of anger, such as increased heart rate. Additionally, deep breathing exercises, where you inhale for a count of four, hold for four, and exhale for four, can help you regain control of your emotions."
#                 ]
#             }
#         }

#     def get_response(self, user_input, session_id):
#         if session_id not in self.session_counts:
#             self.session_counts[session_id] = 1
#             self.conversation_history[session_id] = []
#             return "Hi! I'm here to listen and support you. How are you feeling today?"

#         self.session_counts[session_id] += 1
#         emotion = self._detect_emotion(user_input.lower())
#         response = self._generate_response(emotion)

#         self._log_interaction(session_id, user_input, emotion, response)
#         return response

#     def _detect_emotion(self, text):
#         for emotion, data in self.patterns.items():
#             for pattern in data['patterns']:
#                 if re.search(pattern, text):
#                     return emotion
#         return 'general'

#     def _generate_response(self, emotion):
#         responses = self.patterns.get(emotion, {
#             'responses': ["I'm here to listen. Would you like to tell me more?"]
#         })['responses']
#         return random.choice(responses)

#     def _log_interaction(self, session_id, user_input, emotion, response):
#         log_entry = {
#             'timestamp': datetime.now().isoformat(),
#             'session_id': session_id,
#             'user_input': user_input,
#             'emotion': emotion,
#             'response': response
#         }

#         log_file = f"app/logs/chat_log_{datetime.now().strftime('%Y%m%d')}.json"
#         with open(log_file, 'a') as f:
#             json.dump(log_entry, f)
#             f.write('\n')
import json
import requests
from datetime import datetime
class ResponseModel:
    def __init__(self):
        self.conversation_history = {}
        self.session_counts = {}
        self.api_token = "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"  # Replace with your actual API token
        self.api_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

    def get_response(self, user_input, session_id):
        if session_id not in self.session_counts:
            self.session_counts[session_id] = 1
            self.conversation_history[session_id] = []
            return "Hi! I'm here to listen and support you. How are you feeling today?"

        self.session_counts[session_id] += 1

        # Call Hugging Face API to get response from BlenderBot
        response = self._get_blenderbot_response(user_input)

        self._log_interaction(session_id, user_input, response)
        return response

    def _get_blenderbot_response(self, user_input):
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }
        data = json.dumps({"inputs": user_input})

        response = requests.post(self.api_url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            return "Sorry, I couldn't generate a response. Please try again."

    def _log_interaction(self, session_id, user_input, response):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'user_input': user_input,
            'response': response
        }

        log_file = f"app/logs/chat_log_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')
