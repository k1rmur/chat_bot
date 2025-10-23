import logging

# Get logger for user actions
action_logger = logging.getLogger("user_actions")


allowed_actions = {
    "menu": "Навигация по меню",
    "ai": "Вопрос ИИ",
    "start": "Начало диалога",
}


def get_user_display_name(message):
    """
    Get user's display name in format user_id:username
    
    Args:
        message: VK message object
        
    Returns:
        String in format "user_id:None" (VK doesn't provide username in message object)
    """
    try:
        user_id = message.from_id
        # VK bot doesn't have username in message object, always use None
        return f"{user_id}:None"
    except Exception:
        return "Unknown:None"


def log_action(message, action, answer=None, extra_info=None):
    """
    Log user actions to api.log in structured text format.
    
    Args:
        message: VK message object
        action: Action type from allowed_actions or custom action string
        answer: Optional AI answer text (kept for compatibility, not used)
        extra_info: Optional additional information to log
    """
    try:
        # Get user identifier
        user_name = get_user_display_name(message)
        
        # Format: User: {user_id:username}, Action: {action}
        log_message = f"User: {user_name}, Action: {action}"
        
        # Log to user actions logger
        action_logger.info(log_message)
        
    except Exception as e:
        print(f"Error in log_action: {e}")
