"""Demo module to showcase the AI Commit Summarizer functionality."""

def slow_sort_algorithm(items):
    """
    A deliberately inefficient sorting algorithm for demonstration.
    
    Args:
        items: List of items to sort
        
    Returns:
        Sorted list
    """
    # Bubble sort implementation
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


def process_user_data(user_list):
    """
    Process user data with inefficient sorting.
    
    Args:
        user_list: List of user objects
        
    Returns:
        Processed user data
    """
    # Sort users by name using the slow algorithm
    sorted_users = slow_sort_algorithm(user_list)
    
    # Additional processing
    result = []
    for user in sorted_users:
        result.append({
            "username": user.get("name", ""),
            "email": user.get("email", ""),
            "processed": True
        })
        
    return result
