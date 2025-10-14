import base64

def decode_attachment(attachment):
    """Decodes a base64 encoded data URI attachment."""
    try:
        # Splits the data URI into header and the base64-encoded part
        header, encoded = attachment['url'].split(",", 1)
        # Decodes the base64 string
        data = base64.b64decode(encoded)
        # Returns the name and decoded content
        return {
            "name": attachment['name'],
            "content": data.decode('utf-8')
        }
    except Exception as e:
        print(f"Error decoding attachment {attachment.get('name')}: {e}")
        return None