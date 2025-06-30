from screen_utils import ScreenUtils

class ButtonLocator:
    def __init__(self, image_directory):
        self.image_directory = image_directory

        # Default relative positions for window-based buttons
        self.default_relative_positions = [
            (0.130, 0.643),  # Number button
            (0.674, 0.530),  # Left button
            (0.808, 0.321),  # Up button
            (0.914, 0.591),  # Right button
            (0.808, 0.852)   # Down button
        ]
        self.default_button_names = ["number", "left", "up", "right", "down"]
        
		# Default relative positions for window-based buttons
        self.default_extension_position = [
            (0.3673, 0.8144),  # Extension number
            (0.8633, 0.2887),  # Engage
            (0.8365, 0.7835)  # Extension Set
        ]
        self.default_extension_button_names = ["Extension number", "Engage", "Extension set"]
        self.displacement_relative_position=[
			(0.6280, 0.8000),  # displacement number
			(0.9156, 0.7905) # displaement set
		]
        self.default_displacement_button_names=["displacement number", "displacement set"]      

        

        # Relative positions for dynamically evaluated buttons
        self.dynamic_relative_positions = {
            "right_click": (0.42900302114803623, 2.342857142857143),
            "backlash": (0.44954682779456195, 2.2857142857142856),
            "move_relative": (0.44954682779456195, 2.414285714285714),
            "sample1": (0.8350453172205438, 0.9571428571428572),
            "sample_name": (0.8223564954682779, 0.680952380952381),
            "XY1": (0.08821752265861027, 0.3523809523809524),  # Top-left corner (relative)
            "XY2": (0.7667673716012084, 4.357142857142857),   # Bottom-right corner (relative)
            "Bbox_XYZ_1": (-0.062235649546827795, 1.6666666666666667),
            "Bbox_XYZ_2": (0.05740181268882175, 4.161904761904762)
        }

        self.dynamic_button_order = [
            "right_click", "backlash", "move_relative", 
            "sample1", "sample_name", "XY1", "XY2", "Bbox_XYZ_1", "Bbox_XYZ_2"
        ]

    def get_button_coordinates(self, button_name):
        """
        Get the coordinates of a button by its image name.
        """
        image_path = f"{self.image_directory}/{button_name}.png"
        return ScreenUtils.find_image_center_on_screen(image_path)

    def get_absolute_from_window_coordinates(self, window_image_name, 
                                             relative_positions=None, 
                                             button_names=None):
        """
        Get button coordinates using relative positions of buttons in a window.
        Allows the use of custom relative positions and button names.

        Parameters:
            window_image_name (str): Name of the window image (without '.png').
            relative_positions (list of tuple): Optional. Relative positions as percentages (x, y).
            button_names (list of str): Optional. Names of the buttons.

        Returns:
            dict: Button names mapped to their calculated absolute (x, y) coordinates.
        """
        # Use defaults if no custom values are provided
        if relative_positions == 'extension':
             relative_positions = self.default_extension_position
             button_names = self.default_extension_button_names
        elif relative_positions == 'displacement':
             relative_positions = self.displacement_relative_position
             button_names = self.default_displacement_button_names
        elif relative_positions is None:
             relative_positions = self.default_relative_positions
             button_names = self.default_button_names

        # Ensure the inputs match in length
        if len(relative_positions) != len(button_names):
            raise ValueError("The number of relative positions must match the number of button names.")

        # Find the bounding box of the window
        window_image_path = f"{self.image_directory}/{window_image_name}.png"
        edges = ScreenUtils.find_image_edges_on_screen(window_image_path)

        if edges is None:
            raise ValueError(f"Bounding box not found for {window_image_name}")

        top_left_x, top_left_y, bottom_right_x, bottom_right_y = edges
        box_width = bottom_right_x - top_left_x
        box_height = bottom_right_y - top_left_y

        # Calculate absolute positions
        coordinates = {}
        for i, (relative_x, relative_y) in enumerate(relative_positions):
            absolute_x = relative_x * box_width + top_left_x
            absolute_y = relative_y * box_height + top_left_y
            coordinates[button_names[i]] = (absolute_x, absolute_y)

        return coordinates

    def get_absolute_from_dynamic_coordinates(self, button_name, image_path1, image_path2):
        """
        Get the absolute position of a dynamically evaluated button by calculating it
        from its relative position and two reference images.
        """
        if button_name not in self.dynamic_relative_positions:
            raise ValueError(f"Button '{button_name}' is not defined in dynamic relative positions.")

        relative_position = self.dynamic_relative_positions[button_name]
        absolute_position = ScreenUtils.calculate_absolute_from_relative_two_images(
            image_path1=image_path1,
            image_path2=image_path2,
            relative_positions=[relative_position],
            monitor_index=2,
            threshold=0.8
        )

        # Extract keys dynamically for the single button
        abs_x = absolute_position.get(f"button_0_X")
        abs_y = absolute_position.get(f"button_0_Y")

        if abs_x is None or abs_y is None:
            raise ValueError(f"Coordinates for '{button_name}' could not be calculated.")

        return abs_x, abs_y

    def evaluate_dynamic_buttons(self, image_dir):
        """
        Evaluate all dynamically defined buttons by calculating their absolute positions
        from relative positions and the two reference images.
        """
        button_positions = {}
        image_path1 = f"{image_dir}/puck 2.png"
        image_path2 = f"{image_dir}/start.png"
        for button_name in self.dynamic_button_order:
            button_positions[button_name] = self.get_absolute_from_dynamic_coordinates(
                button_name, image_path1, image_path2
            )
        return button_positions

    def get_bounding_box(self, image_dir, corner_1="XY1", corner_2="XY2"):
        """
        Calculate the bounding box using corner_1 (top-left) and corner_2 (bottom-right)
        based on their relative positions and two reference images.

        Parameters:
            image_dir (str): Directory containing reference images.
            corner_1 (str): Key for the top-left corner in dynamic_relative_positions.
            corner_2 (str): Key for the bottom-right corner in dynamic_relative_positions.

        Returns:
            tuple: (x1, y1, x2, y2) representing the bounding box.
        """
        # Get absolute positions for the specified corners
        xy1_abs = self.get_absolute_from_dynamic_coordinates(corner_1, 
                                                             f"{image_dir}/puck 2.png", 
                                                             f"{image_dir}/start.png")
        xy2_abs = self.get_absolute_from_dynamic_coordinates(corner_2, 
                                                             f"{image_dir}/puck 2.png", 
                                                             f"{image_dir}/start.png")

        x1, y1 = xy1_abs  # Top-left corner
        x2, y2 = xy2_abs  # Bottom-right corner

        return x1, y1, x2, y2
    
