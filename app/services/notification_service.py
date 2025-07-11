# app/services/notification_service.py

import httpx

NOTIFICATION_URL = "http://notification-service/notify"  # adapte si besoin

def send_notification(notification_type: str, data: dict):
    payload = {
        "type": notification_type,
        "data": data
    }

    try:
        response = httpx.post(NOTIFICATION_URL, json=payload, timeout=5)
        response.raise_for_status()
    except httpx.RequestError as exc:
        print(f"[NotificationService] Erreur: {exc}")
    except httpx.HTTPStatusError as exc:
        print(f"[NotificationService] Erreur HTTP: {exc.response.status_code} - {exc.response.text}")