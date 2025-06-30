import cv2
import numpy as np
import mss
from PIL import Image

class ScreenUtils:
    @staticmethod
    def find_image_center_on_screen(image_path, monitor_index=2, threshold=0.8):
        """
        Finds the center coordinates of a target image on a specified screen monitor.
        """
        target_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if target_img is None:
            raise ValueError(f"Could not load image at {image_path}")

        target_height, target_width = target_img.shape[:2]

        with mss.mss() as sct:
            # Single screenshot capture
            screenshot = sct.grab(sct.monitors[monitor_index])
            screen_img = np.array(screenshot)

            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2GRAY)
            target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(screen_gray, target_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                top_left = max_loc
                center_x = 1920 + top_left[0] + target_width // 2
                center_y = top_left[1] + target_height // 2
                return center_x, center_y
            return None

    @staticmethod
    def find_image_edges_on_screen(image_path, monitor_index=2, threshold=0.8):
        """
        Finds the edges of a target image on a specified screen monitor.
        """
        target_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if target_img is None:
            raise ValueError(f"Could not load image at {image_path}")

        target_height, target_width = target_img.shape[:2]

        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[monitor_index])
            screen_img = np.array(screenshot)

            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2GRAY)
            target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(screen_gray, target_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                top_left_x = 1920 + max_loc[0]
                top_left_y = max_loc[1]
                bottom_right_x = top_left_x + target_width
                bottom_right_y = top_left_y + target_height
                return top_left_x, top_left_y, bottom_right_x, bottom_right_y
            return None

    @staticmethod
    def calculate_relative_positions_from_edges(image_path, absolute_positions, monitor_index=2, threshold=0.8):
        """
        Calculates relative positions of points of interest using the bounding box of an image.
        """
        bounding_box = ScreenUtils.find_image_edges_on_screen(image_path, monitor_index, threshold)
        if bounding_box is None:
            raise ValueError(f"Bounding box not found for {image_path}")

        top_left_x, top_left_y, bottom_right_x, bottom_right_y = bounding_box
        box_width = bottom_right_x - top_left_x
        box_height = bottom_right_y - top_left_y

        relative_positions = []
        for abs_x, abs_y in absolute_positions:
            relative_x = (abs_x - top_left_x) / box_width
            relative_y = (abs_y - top_left_y) / box_height
            relative_positions.append((relative_x, relative_y))

        return relative_positions

    @staticmethod
    def calculate_relative_from_two_images(image_path1, image_path2, true_positions, monitor_index=2, threshold=0.8):
        """
        Calculates relative positions of points of interest using two reference images.
        """
        coords1 = ScreenUtils.find_image_center_on_screen(image_path1, monitor_index, threshold)
        coords2 = ScreenUtils.find_image_center_on_screen(image_path2, monitor_index, threshold)

        if coords1 is None or coords2 is None:
            raise ValueError("Could not find both reference images on the screen.")

        x1, y1 = coords1
        x2, y2 = coords2

        box_width = abs(x2 - x1)
        box_height = abs(y2 - y1)

        relative_positions = []
        for true_x, true_y in true_positions:
            relative_x = (true_x - min(x1, x2)) / box_width
            relative_y = (true_y - min(y1, y2)) / box_height
            relative_positions.append((relative_x, relative_y))

        return relative_positions

    @staticmethod
    def calculate_absolute_from_relative_two_images(image_path1, image_path2, relative_positions, monitor_index=2, threshold=0.8):
        """
        Calculates absolute positions from relative positions using two reference images.
        """
        coords1 = ScreenUtils.find_image_center_on_screen(image_path1, monitor_index, threshold)
        coords2 = ScreenUtils.find_image_center_on_screen(image_path2, monitor_index, threshold)

        if coords1 is None or coords2 is None:
            raise ValueError("Could not find both reference images on the screen.")

        x1, y1 = coords1
        x2, y2 = coords2

        box_width = abs(x2 - x1)
        box_height = abs(y2 - y1)
        top_left_x = min(x1, x2)
        top_left_y = min(y1, y2)

        absolute_positions = {}
        for i, (relative_x, relative_y) in enumerate(relative_positions):
            abs_x = relative_x * box_width + top_left_x
            abs_y = relative_y * box_height + top_left_y

            # Assign proper key names dynamically
            absolute_positions[f"button_{i}_X"] = abs_x
            absolute_positions[f"button_{i}_Y"] = abs_y

        return absolute_positions
    
    @staticmethod
    def capture_screen_area(x1, y1, x2, y2):
        """
        Captures a specific rectangular area of the screen and returns it as a PIL Image object.
        
        Parameters:
            x1, y1, x2, y2 (int): Coordinates of the diagonal corners of the rectangle to capture.
                                  (top-left and bottom-right).
        
        Returns:
            Image: A PIL Image object of the captured screenshot area.
        """
        # Ensure all coordinates are integers
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        with mss.mss() as sct:
            # Define the bounding box for the area to capture
            bbox = {'left': x1, 'top': y1, 'width': x2 - x1, 'height': y2 - y1}
            
            # Capture the screen area
            screenshot = sct.grab(bbox)

            # Convert the screenshot to a PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img

    @staticmethod
    def capture_screen_as_variable(monitor_index=2):
        with mss.mss() as sct:
            monitor = sct.monitors[monitor_index]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img
    
	
