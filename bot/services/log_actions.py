import logging

# Get logger for user actions
action_logger = logging.getLogger("user_actions")


allowed_actions = {
    "menu": "Навигация по меню",
    "ai": "Вопрос ИИ",
    "start": "Начало диалога",
    "protocol": "Протокол",
    "document_summary": "Суммаризация документа",
    "voice_message": "Голосовое сообщение",
    "feedback": "Обратная связь",
    "video_protocol": "Протокол из видео",
    "send_news": "Рассылка новостей",
    "subscribe": "Подписка на рассылку",
    "get_report": "Получение отчета",
}


def get_user_display_name(message):
    """
    Get user's display name in format user_id:username
    
    Args:
        message: Telegram message object
        
    Returns:
        String in format "user_id:username" or "user_id:None" if username is not set
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else "None"
        return f"{user_id}:{username}"
    except Exception:
        return "Unknown:None"


def log_action(message, action, answer=None, extra_info=None):
    """
    Log user actions to api.log in structured text format.
    
    Args:
        message: Telegram message object
        action: Action type from allowed_actions
        answer: Optional AI answer text (kept for compatibility, not used)
        extra_info: Optional additional information to log
    """
    try:
        # Get user identifier
        user_name = get_user_display_name(message)
        
        # Format: User: {user_id:username}, Action: {action}
        log_message = f"User: {user_name}, Action: {action}"
        
        # Add extra context if available
        if extra_info:
            log_message += f", Details: {extra_info}"
        
        # Log to user actions logger
        action_logger.info(log_message)
        
    except Exception as e:
        print(f"Error in log_action: {e}")
