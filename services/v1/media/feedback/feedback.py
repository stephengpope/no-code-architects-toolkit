import os

def get_feedback_path():
    """
    Returns the absolute path to the feedback static files directory
    """
    # Define the path to the static feedback site files
    # Keeping files isolated in the feedback module directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, 'static')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    return static_dir
