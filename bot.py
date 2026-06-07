import anthropic
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

conversations: dict[str, list] = {}

def build_system_prompt(client: dict) -> str:
    return f"""أنت {client['bot_name']} — مساعد ذكي لإدارة الحجوزات.

📋 معلومات النشاط:
• الاسم: {client['name']}
• نوع الخدمة: {client['business_type']}
• أوقات الدوام: {client['hours']}

💰 الأسعار:
{client['prices']}

🎭 أسلوب الرد: {client['tone']}

القواعد:
1. رُد دائماً بالعربية
2. كن مختصراً ومفيداً
3. عند طلب حجز اجمع: الاسم، الجوال، التاريخ، الوقت، الخدمة
4. عند اكتمال المعلومات أضف في نهاية ردك:
[BOOKING_DATA:{{"name":"...","phone":"...","date":"YYYY-MM-DD","time":"HH:MM","service":"..."}}]"""

def get_reply(phone_id: str, user_id: str, user_text: str, client: dict):
    conv_key = f"{phone_id}_{user_id}"
    if conv_key not in conversations:
        conversations[conv_key] = []
    conversations[conv_key].append({"role": "user", "content": user_text})
    history = conversations[conv_key][-10:]
    response = claude.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=build_system_prompt(client),
        messages=history
    )
    reply = response.content[0].text
    booking_data = None
    match = re.search(r'\[BOOKING_DATA:(\{.*?\})\]', reply, re.DOTALL)
    if match:
        try:
            booking_data = json.loads(match.group(1))
            reply = reply.replace(match.group(0), "").strip()
        except Exception:
            pass
    conversations[conv_key].append({"role": "assistant", "content": reply})
    return reply, booking_data