from database import get_db_connection

def verify_pin(pin):
    """
    Verifies the PIN against the database.
    Returns the user dictionary if valid, None otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE pin = ?", (pin,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None
