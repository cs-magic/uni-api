import json
from typing import List, Dict, Union, Any


def openai2anthropic(messages: List[Dict[str, Any]]) -> Dict:
    """
    Convert OpenAI chat completion messages format to Anthropic messages format,
    supporting text, images, and other content types.

    @see: [Convert OpenAI Messages to Anthropic Format - Claude](https://claude.ai/chat/b9709c74-75ce-4a1d-8818-9bab933d6294)

    OpenAI image format examples:
    1. URL: {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
    2. Base64: {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}

    Anthropic image format:
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "..."
        }
    }
    """

    def convert_role(role: str) -> str:
        """Convert OpenAI role to Anthropic role."""
        role_mapping = {"system": "user", "user": "user", "assistant": "assistant", "function": "assistant"}
        return role_mapping.get(role, "user")

    def convert_content_item(item: Union[str, Dict]) -> Dict:
        """Convert a single content item to Anthropic format."""
        if isinstance(item, str):
            return {"type": "text", "text": item}

        # Handle image content
        if item.get("type") == "image_url":
            image_url = item["image_url"]["url"]

            # 看源码，目前只支持 base64 好像
            return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_url}}

        # Handle function calls
        if item.get("function_call"):
            return {
                "type": "text",
                "text": f"Function call: {item['function_call']['name']}\nArguments: {item['function_call']['arguments']}"}

        # Default to text for unknown types
        return {"type": "text", "text": str(item)}

    def convert_message_content(content: Union[str, List[Dict], Dict]) -> List[Dict]:
        """Convert message content to Anthropic format."""
        if isinstance(content, str):
            return [{"type": "text", "text": content}]
        elif isinstance(content, list):
            return [convert_content_item(item) for item in content]
        else:
            return [convert_content_item(content)]

    def process_system_message(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process system messages by combining them with the first user message."""
        result = []
        system_contents = []

        for msg in messages:
            if msg["role"] == "system":
                if isinstance(msg["content"], str):
                    system_contents.append(msg["content"])
                else:
                    # Handle complex system messages with images
                    result.append({"role": "user", "content": convert_message_content(msg["content"])})
            else:
                if system_contents and msg["role"] == "user":
                    # Combine system messages with first user message
                    user_content = msg["content"]
                    if isinstance(user_content, str):
                        combined_content = "\n".join(system_contents + [user_content])
                        result.append({"role": "user", "content": [{"type": "text", "text": combined_content}]})
                    else:
                        # If user message has images, add system message as separate message
                        if system_contents:
                            result.append({
                                "role": "user",
                                "content": [{"type": "text", "text": "\n".join(system_contents)}]})
                        result.append({"role": "user", "content": convert_message_content(user_content)})
                    system_contents = []
                else:
                    result.append({
                        "role": convert_role(msg["role"]),
                        "content": convert_message_content(msg["content"])})

        return result

    def handle_function_calls(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert function calls to text format in assistant messages."""
        result = []

        for msg in messages:
            if msg.get("function_call"):
                # Convert function call to text format
                result.append({
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": f"Function call: {msg['function_call']['name']}\nArguments: {msg['function_call']['arguments']}"}]})
            elif msg.get("role") == "function":
                # Convert function response to text format
                result.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": f"Function result: {msg['content']}"}]})
            else:
                result.append(msg)

        return result

    # Process messages
    processed_messages = process_system_message(messages)
    processed_messages = handle_function_calls(processed_messages)

    # Create Anthropic format
    anthropic_format = processed_messages

    return anthropic_format


# Example usage
if __name__ == "__main__":
    openai_messages = [{"role": "system", "content": "You are a helpful assistant"}, {
        "role": "user",
        "content": [{"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}]},
                       {"role": "assistant", "content": "I see a beautiful landscape."}, {
                           "role": "user",
                           "content": [
                               {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."}},
                               {"type": "text", "text": "And this one?"}]}]

    anthropic_format = openai2anthropic(openai_messages)
    print(json.dumps(anthropic_format, indent=2))
