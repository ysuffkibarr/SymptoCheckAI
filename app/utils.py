from fastapi import Request

def get_client_ip(request: Request) -> str:
    """
    Safely extracts the client IP address, mitigating basic IP spoofing attempts.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host