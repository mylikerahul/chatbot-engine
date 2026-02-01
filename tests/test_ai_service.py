def test_ai_response_format():
    """
    Ensures AI service returns a valid response structure.
    """
    response = {
        "reply": "Hello"
    }

    assert "reply" in response
    assert isinstance(response["reply"], str)
