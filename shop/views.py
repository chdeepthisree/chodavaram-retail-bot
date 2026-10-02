import json
import os
import requests
import threading
from dotenv import load_dotenv
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, CustomerLead, ChatLog

load_dotenv()


def ask_groq_agent(customer_msg, inventory, history):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "క్షమించండి, సర్వర్ ఆకృతీకరణ లోపం ఉంది."

    system_prompt = f"""You are a polite, helpful AI assistant for a retail shop in Chodavaram, Andhra Pradesh.
Always reply respectfully. Speak in natural conversational Telugu using the Telugu script.
If the customer texts in English script (e.g., 'pappu price entha'), respond in clear Telugu script.
Use friendly local markers like 'andi' (అండి) and 'namaste' (నమస్తే).

LIVE STORE INVENTORY AVAILABLE RIGHT NOW:
{inventory}

RECENT CHAT HISTORY FOR CONTEXT:
{history}

Rule 1: If an item is in stock, confirm the price and ask how many units they want.
Rule 2: If a customer asks for a gift suggestion, recommend 2 matching items from the inventory.
Rule 3: If they ask for bulk discounts, complex hardware rates, or marriage hall bookings, reply that the owner will speak to them directly, and output the word [HUMAN_REQUIRED] at the very end of your text.
Rule 4: Never invent products not listed in the inventory."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": customer_msg}
        ],
        "temperature": 0.2
    }

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        data = res.json()
        if "error" in data:
            return "క్షమించండి, సర్వర్ ఆకృతీకరణ లోపం ఉంది."
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "క్షమించండి, సర్వర్ అందుబాటులో లేదు. దయచేసి కొసేపటి తర్వాత ప్రయత్నించండి."


def reply_via_whatsapp(recipient_phone, reply_text):
    phone_id = os.getenv("WHATSAPP_PHONE_ID") or os.getenv("PHONE_NUMBER_ID")
    token = os.getenv("WHATSAPP_CLOUD_API_TOKEN") or os.getenv("WHATSAPP_TOKEN")

    if not phone_id or not token:
        print("ERROR: WhatsApp API credentials missing.")
        return

    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": reply_text}
    }

    requests.post(url, json=payload, headers=headers)


def process_whatsapp_payload_in_background(body):
    try:
        value = body["entry"][0]["changes"][0]["value"]

        # 1. Ignore non-message events (e.g., status updates for read/delivered)
        if "messages" not in value:
            return

        message_data = value["messages"][0]
        from_phone = message_data.get("from")
        whatsapp_message_id = message_data.get("id")

        print("WHATSAPP MESSAGE ID:", whatsapp_message_id)
        print(
            "WHATSAPP MESSAGE TEXT:",
            message_data.get("text", {}).get("body", "")
        )

        if not whatsapp_message_id:
            return

        text_dict = message_data.get("text") or {}
        user_text = text_dict.get("body", "").strip()

        if not user_text:
            return

        # 2. ATOMIC LOCK / DEDUPLICATION CHECK
        # We save the ChatLog IMMEDIATELY before generating AI response.
        # If another thread tries to save the same whatsapp_message_id, it will be caught here.
        with transaction.atomic():
            if ChatLog.objects.filter(whatsapp_message_id=whatsapp_message_id).exists():
                print(f"DUPLICATE BLOCKED: Message ID {whatsapp_message_id} already exists.")
                return

            customer, _ = CustomerLead.objects.get_or_create(phone_number=from_phone)

            # Create USER log entry FIRST to claim this whatsapp_message_id locks out duplicates
            ChatLog.objects.create(
                customer=customer,
                sender="USER",
                message=user_text,
                whatsapp_message_id=whatsapp_message_id
            )

        if customer.needs_human_help:
            return

        # 3. PREPARE CONTEXT & GENERATE RESPONSE
        items = Product.objects.filter(is_available=True)
        inv_str = "\n".join([f"- {i.name} ({i.get_category_display()}): Rs.{i.price} [Stock: {i.stock_quantity}]" for i in items])

        past_logs = ChatLog.objects.filter(customer=customer).order_by("-timestamp")[:4]
        history_str = "\n".join([f"{l.sender}: {l.message}" for l in reversed(past_logs)])

        ai_raw_response = ask_groq_agent(user_text, inv_str, history_str)

        if "[HUMAN_REQUIRED]" in ai_raw_response:
            customer.needs_human_help = True
            customer.save()
            ai_clean_response = ai_raw_response.replace("[HUMAN_REQUIRED]", "").strip()
        else:
            ai_clean_response = ai_raw_response

        # Save AI Response Log
        ChatLog.objects.create(
            customer=customer,
            sender="AI",
            message=ai_clean_response
        )

        # Send reply
        reply_via_whatsapp(from_phone, ai_clean_response)

    except Exception as e:
        print(f"Error in background execution: {e}")


@csrf_exempt
def whatsapp_bot_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        expected_token = os.getenv("VERIFY_TOKEN") or "chodavaram_secret"

        if mode == "subscribe" and token == expected_token:
            return HttpResponse(challenge, status=200)

        return HttpResponse("Verification failed", status=403)

    if request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))

            # Dispatch background worker immediately
            thread = threading.Thread(
                target=process_whatsapp_payload_in_background,
                args=(body,)
            )
            thread.start()

            # Fast 200 OK return to stop Meta retries
            return HttpResponse("EVENT_RECEIVED", status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "invalid_json"}, status=400)

    return JsonResponse({"status": "method_not_allowed"}, status=405)