from button_locator import ButtonLocator

if __name__ == "__main__":
    image_dir = "assets"
    locator = ButtonLocator(image_dir)

    # Example 1: Find the center of a button image
    add_button_coords = locator.get_button_coordinates("add")
    print(f"Add Button Coordinates: {add_button_coords}")

    # Example 2: Find relative button coordinates within a window
    relative_positions = [
        (0.130, 0.643),  # Number button
        (0.674, 0.530),  # Left button
        (0.808, 0.321),  # Up button
        (0.914, 0.591),  # Right button
        (0.808, 0.852)   # Down button
    ]
    button_names = ["number", "left", "up", "right", "down"]
    relative_coords = locator.get_absolute_from_relative_button_coordinates("relative move", relative_positions, button_names)
    print(f"Relative Button Coordinates: {relative_coords}")
