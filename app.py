import os
import pyotp
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables from .env file (useful for local development)
# In Docker, environment variables will be passed directly
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def get_available_services():
    """Get all available 2FA services from environment variables"""
    services = {}
    for key, value in os.environ.items():
        if key.startswith("2FA_TOKEN_"):
            service_name = key[10:].lower()  # Remove "2FA_TOKEN_" prefix and lowercase
            # Clean the token to ensure Base32 compatibility
            cleaned_token = clean_token_for_base32(value)
            services[service_name] = cleaned_token
    return services

def clean_token_for_base32(token):
    """
    Clean a token to make it compatible with Base32 format.
    - Removes spaces and special characters
    - Converts to uppercase
    - Pads to valid length if needed
    """
    # Remove spaces and non-alphanumeric characters
    cleaned = ''.join(c for c in token if c.isalnum())
    
    # Convert to uppercase (Base32 is uppercase)
    cleaned = cleaned.upper()
    
    # Filter to only valid Base32 characters (A-Z, 2-7)
    cleaned = ''.join(c for c in cleaned if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    
    # Base32 encoding requires the length to be a multiple of 8
    # Pad with 'A' (arbitrary valid character) if needed
    remainder = len(cleaned) % 8
    if remainder != 0:
        cleaned += 'A' * (8 - remainder)
    
    return cleaned

def get_allowed_channels():
    """Get list of allowed channel IDs from environment variable"""
    allowed_channels_str = os.environ.get("ALLOWED_CHANNEL_IDS", "")
    if not allowed_channels_str:
        return []
    
    return [channel_id.strip() for channel_id in allowed_channels_str.split(",")]

@app.command("/2fa")
def generate_2fa(ack, command, respond):
    """
    Generate a 2FA token for the specified service
    Usage: /2fa [service_name]
    """
    # Get the channel ID
    channel_id = command["channel_id"]
    
    # Check if the channel is allowed
    allowed_channels = get_allowed_channels()
    if allowed_channels and channel_id not in allowed_channels:
        # Acknowledge with error message
        ack("Sorry, this command is not available in this channel.")
        return
        
    # Acknowledge the command request
    ack()
    
    # Get the text after the command (service name)
    text = command.get("text", "").strip().lower()
    
    # Get all available services
    services = get_available_services()
    
    # If no service is specified or the service doesn't exist
    if not text:
        # List available services
        if services:
            service_list = ", ".join(services.keys())
            # Use respond for slash commands which creates ephemeral messages by default
            respond(f"Please specify a service: `/2fa [service_name]`\nAvailable services: {service_list}")
        else:
            # Use respond for slash commands which creates ephemeral messages by default
            respond("No 2FA services configured. Add environment variables starting with '2FA_TOKEN_'.")
        return
    
    # Check if the requested service exists
    if text not in services:
        respond(f"Service '{text}' not found. Available services: {', '.join(services.keys())}")
        return
    
    # Generate the TOTP token for the requested service
    secret = services[text]
    try:
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        # Send the token (only visible to the user who triggered the command)
        respond(f"Your 2FA token for {text} is: `{token}`")
    except Exception as e:
        respond(f"Error generating token: {str(e)}. Please check your token format - it should be Base32 compatible.")


@app.event("app_mention")
def handle_mention(client, event):
    """Handle when the app is mentioned in a channel"""
    channel_id = event.get("channel")
    user_id = event.get("user")
    
    # Check if the channel is allowed
    allowed_channels = get_allowed_channels()
    if allowed_channels and channel_id not in allowed_channels:
        # Don't respond in non-allowed channels
        return
        
    # Send a DM to the user instead of responding in the channel
    client.chat_postMessage(
        channel=user_id,  # This sends a direct message
        text="Hello! Use `/2fa` to generate a 2FA token."
    )

if __name__ == "__main__":
    # Check if required environment variables are set
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable is required")
        exit(1)
    if not os.environ.get("SLACK_APP_TOKEN"):
        print("Error: SLACK_APP_TOKEN environment variable is required")
        exit(1)
        
    # Log channel restrictions
    allowed_channels = get_allowed_channels()
    if allowed_channels:
        print(f"Bot restricted to these channel IDs: {', '.join(allowed_channels)}")
    else:
        print("No channel restrictions specified. Bot will work in all channels.")
    
    # Get available services
    services = get_available_services()
    if not services:
        print("Warning: No 2FA services configured. Add environment variables starting with '2FA_TOKEN_'.")
    else:
        print(f"Available services: {', '.join(services.keys())}")
    
    # Start the app in Socket Mode
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    print("⚡️ Slack 2FA app is running!")
    handler.start()