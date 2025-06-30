import os
import pyautogui
import time
import pandas as pd
import pytesseract
import numpy as np
from button_locator import ButtonLocator
from screen_utils import ScreenUtils
import random
import string
import cv2
import re
from image_processing import ImageProcessing


class Automation:
    def __init__(self, image_directory="assets"):
        self.locator = ButtonLocator(image_directory)
        self.image_directory = image_directory
        self.default_directory = r"C:\Users\vchawla\OneDrive\Automation Tests\Trial 1"
        self.default_file_name = "_Results.csv"
        self.default_file_path = os.path.join(self.default_directory, self.default_file_name)

    def starting_tests(self, sample_name, t=2):
        """
        Automates the process of starting tests.
        """
        dynamic_button_positions = self.locator.evaluate_dynamic_buttons(self.image_directory)

        # Perform actions to start the test
        pyautogui.click(dynamic_button_positions['sample1'][0], dynamic_button_positions['sample1'][1])
        time.sleep(t)

        Add_X, Add_Y = self.locator.get_button_coordinates('add')
        pyautogui.click(Add_X, Add_Y)
        time.sleep(t)

        pyautogui.click(dynamic_button_positions['sample_name'][0], dynamic_button_positions['sample_name'][1])
        time.sleep(t)
        pyautogui.write(sample_name, interval=0.1)

        continue_X, continue_Y = self.locator.get_button_coordinates('continue')
        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)
        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)

        C_X, C_Y = self.locator.get_button_coordinates('C')
        array_X, array_Y = self.locator.get_button_coordinates('array')

        pyautogui.click(C_X, C_Y)
        time.sleep(t)

        pyautogui.click(array_X, array_Y)
        time.sleep(t)

        Ok_X, Ok_Y = self.locator.get_button_coordinates('ok')
        pyautogui.click(Ok_X, Ok_Y)
        time.sleep(t)

        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)
        
    def start_test_normal(self, t=2):
        start_test_X, start_test_Y = self.locator.get_button_coordinates('start')
        pyautogui.click(start_test_X, start_test_Y)
        time.sleep(t)
    

    def move(self, amount, direction, t=2, tt=4, time_trial=None, Backlash=None):
        """
        Automates the movement process by entering a number and clicking direction buttons.
        """
        dynamic_button_positions = self.locator.evaluate_dynamic_buttons(self.image_directory)
        # Right-click to open the context menu
        pyautogui.rightClick(dynamic_button_positions['right_click'][0], dynamic_button_positions['right_click'][1])
        time.sleep(0.5)

        # Right-click on "move_relative"
        pyautogui.rightClick(dynamic_button_positions['move_relative'][0], dynamic_button_positions['move_relative'][1])
        time.sleep(0.5)

        window_button_positions = self.locator.get_absolute_from_window_coordinates("relative move")

        # Step 1: Click on the 'number' field
        pyautogui.click(window_button_positions['number'][0], window_button_positions['number'][1])
        time.sleep(t)

        # Step 2: Clear current input and enter the new amount
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(t)
        pyautogui.write(str(amount), interval=0.1)
        time.sleep(t)

        # Step 3: Click the direction button
        direction_buttons = ["right", "left", "up", "down"]
        
        if direction in direction_buttons:
            pyautogui.click(window_button_positions[direction][0], window_button_positions[direction][1])
        else:
            print("Invalid direction specified. Please use 'right', 'left', 'up', or 'down'.")
            return

        time.sleep(tt)

        # Step 4: Perform backlash correction
        if Backlash is None:
            pyautogui.rightClick(dynamic_button_positions['right_click'][0], dynamic_button_positions['right_click'][1])
            time.sleep(4)
            pyautogui.click(dynamic_button_positions['backlash'][0], dynamic_button_positions['backlash'][1])          
            time.sleep(6)
        
    def move_in_increments(self, total_amount, direction, increment, t=2, tt=4, time_trial=None, Backlash=None):
        """
        Automates the movement process in increments. Moves the specified amount in the given direction using defined increments.
        
        Args:
            total_amount (int): The total distance to move.
            direction (str): The direction to move ('right', 'left', 'up', 'down').
            increment (int): The step size for each movement.
            t (int, optional): Time delay after each step. Default is 2.
            tt (int, optional): Time delay after each full step cycle. Default is 4.
            time_trial (optional): Additional parameter for future use. Default is None.
            Backlash (optional): Specifies if backlash correction should be applied. Default is None.
        """
        remaining_amount = total_amount
        
        while remaining_amount > 0:
            step_amount = min(remaining_amount, increment)
            print(f"Moving {step_amount} in direction {direction}")
            
            # Call the move method with the step amount
            self.move(step_amount, direction, t=t, tt=tt, time_trial=time_trial, Backlash=Backlash)
            
            # Subtract the step amount from the remaining amount
            remaining_amount -= step_amount
            time.sleep(1)  # Small delay between steps for stability

        print(f"Movement of {total_amount} in {direction} direction completed in increments of {increment}.")


    def wait_and_read_file(self, image_path, file_path=None, monitor_index=1, threshold=0.8):
        """
        Waits for an image to appear on screen, then reads a CSV file.
        """
        file_path = file_path or self.default_file_path

        while True:
            time.sleep(10)
            center_coords = self.locator.get_button_coordinates(image_path)
            if center_coords:
                print(f"Image '{image_path}' found at {center_coords}. Waiting for 1 more minute...")
                time.sleep(10)
                break
            else:
                print(f"Image '{image_path}' not found. Still waiting...")
                time.sleep(10)

        try:
            print("Reading the results file...")
            data = pd.read_csv(file_path, skiprows=[1])
            cols_to_select = ['Hardness', 'Modulus', 'X', 'Y']
            selected_data = data.loc[:, cols_to_select].iloc[:-3]
            print("File read successfully:")
            print(selected_data)
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        return data, selected_data

    def wait_and_read_file_blitz(self, image_path, file_path=None, monitor_index=1, threshold=0.8):
        """
        Waits for an image to appear on screen, then reads a CSV file.
        """
        file_path = file_path or self.default_file_path

        while True:
            time.sleep(10)
            center_coords = self.locator.get_button_coordinates(image_path)
            if center_coords:
                print(f"Image '{image_path}' found at {center_coords}. Waiting for 2 more minute...")
                time.sleep(120)
                break
            else:
                print(f"Image '{image_path}' not found. Still waiting...")
                time.sleep(10)

        try:
            print("Reading the results file...")
            data = pd.read_csv(file_path, skiprows=[1])
            cols_to_select = ['X Position', 'Y Position', 'Z Position', 'MODULUS', 'HARDNESS']
            selected_data = data.loc[:, cols_to_select].iloc[:-3]
            print("File read successfully:")
            print(selected_data)
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        return data, selected_data

    @staticmethod
    def save_adjusted_centers_to_file(circle_centers, crosshair_x, crosshair_y, scale_x, scale_y, directory, filename="circle_centers.txt"):
        """
        Saves the adjusted centers of circles to a text file in the specified directory.
        """
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as file:
            for x, y in circle_centers:
                adjusted_x = (x - crosshair_x)/scale_x
                adjusted_y = (-y + crosshair_y)/scale_y
                file.write(f"{adjusted_x}, {adjusted_y}\n")
        print(f"Adjusted centers saved to: {file_path}")
        return file_path

    @staticmethod
    def extract_coordinates(ocr_text):
        """
        Extracts Extension, X Axis Position, and Y Axis Position from OCR text.
        Handles cases where there may be blank lines or non-numeric data after the key.
        """
        lines = ocr_text.splitlines()
        x_value, y_value, extension_value = None, None, None

        def find_next_number(index):
            """Helper function to find the next numeric value after the given index."""
            for j in range(index + 1, len(lines)):
                try:
                    # Attempt to parse the line as a number
                    return float(lines[j].strip().split()[0])
                except (ValueError, IndexError):
                    # Skip invalid or empty lines
                    continue
            return None

        for i, line in enumerate(lines):
            # Normalize line: remove spaces and make lowercase
            line_normalized = re.sub(r"\s+", "", line.strip().lower())

            if "extension" in line_normalized:
                extension_value = find_next_number(i)
            elif "xaxisposition" in line_normalized:
                x_value = find_next_number(i)
            elif "yaxisposition" in line_normalized:
                y_value = find_next_number(i)

        return x_value, y_value, extension_value

    def get_xyz_positions(self):
        """
        Extracts the XYZ positions (X Axis, Y Axis, Extension) using OCR on a captured screenshot.
        """
        x1, y1, x2, y2 = self.locator.get_bounding_box(
            image_dir=self.image_directory, corner_1="Bbox_XYZ_1", corner_2="Bbox_XYZ_2"
        )
        screenshot = ScreenUtils.capture_screen_area(x1, y1, x2, y2)
        screenshot_np = np.array(screenshot)
        ocr_result = pytesseract.image_to_string(screenshot_np, lang='eng')
        # print(ocr_result)
        return self.extract_coordinates(ocr_result)

    def set_extension(self, number, t=2):
        """
        Sets the extension value through the automation workflow.
        """
        if number <= 11.01:
            Z_control_X, Z_control_Y = self.locator.get_button_coordinates('Z control')
            pyautogui.click(Z_control_X, Z_control_Y)
            time.sleep(t)

            Extension_positions = self.locator.get_absolute_from_window_coordinates(
                "Extension control", relative_positions='extension'
            )
            displacement_positions = self.locator.get_absolute_from_window_coordinates(
                "displacement window", relative_positions='displacement'
            )

            OriginX_small, OriginY_small, Extension_origin = self.get_xyz_positions()
            if number > Extension_origin:
                pyautogui.click(displacement_positions['displacement number'][0], displacement_positions['displacement number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(12.5), interval=0.1)
                time.sleep(t)
                pyautogui.click(displacement_positions['displacement set'][0], displacement_positions['displacement set'][1])
                time.sleep(t)
                pyautogui.click(Extension_positions['Extension number'][0], Extension_positions['Extension number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(number), interval=0.1)
                pyautogui.click(Extension_positions['Extension set'][0], Extension_positions['Extension set'][1])
                time.sleep(t)
                pyautogui.click(Extension_positions['Extension number'][0], Extension_positions['Extension number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(0.00), interval=0.1)
                time.sleep(t)
                pyautogui.click(displacement_positions['displacement number'][0], displacement_positions['displacement number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(0.0), interval=0.1)
                time.sleep(t)
            else:
                pyautogui.click(Extension_positions['Extension number'][0], Extension_positions['Extension number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(number), interval=0.1)
                pyautogui.click(Extension_positions['Extension set'][0], Extension_positions['Extension set'][1])
                time.sleep(t)
                pyautogui.click(Extension_positions['Extension number'][0], Extension_positions['Extension number'][1])
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(0.00), interval=0.1)
                time.sleep(t)
        else:
            raise ValueError(f"Extension cannot be greater than 11. Given value: {number}")

    def engage(self):
        """
        Clicks the 'Engage' button on the extension control window.
        """
        Z_control_X, Z_control_Y = self.locator.get_button_coordinates('Z control')
        pyautogui.click(Z_control_X, Z_control_Y)
        time.sleep(2)

        Extension_positions = self.locator.get_absolute_from_window_coordinates(
            "Extension control", relative_positions='extension'
        )
        pyautogui.click(Extension_positions['Engage'][0], Extension_positions['Engage'][1])

    def align_focus(self):
        """
        Guides the user to move to three positions and collects XYZ coordinates.
        Returns the parameters of linear interpolation for Z based on X and Y.
        """
        print("Please move to the first position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x1, y1, z1 = self.get_xyz_positions()

        print("Please move to the second position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x2, y2, z2 = self.get_xyz_positions()

        print("Please move to the third position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x3, y3, z3 = self.get_xyz_positions()

        # Perform linear interpolation to calculate plane parameters
        A = np.array([
            [x1, y1, 1],
            [x2, y2, 1],
            [x3, y3, 1]
        ])
        b = np.array([z1, z2, z3])

        plane_params = np.linalg.solve(A, b)
        print("Linear interpolation parameters (Z = ax + by + c):", plane_params)

        return plane_params  # Returns [a, b, c]

    def focus(self, plane_params):
        """
        Focuses by calculating the Z position for the given X and Y and sets the extension accordingly.
        """
        a, b, c = plane_params
        x, y, z2 = self.get_xyz_positions()
        z = round(a * x + b * y + c, 3)
        print(f"Calculated Z for X={x}, Y={y} is Z={z}")
        self.set_extension(z)

    def change_method(self, method='normal'):
        """
        Changes method file.
        """
        method_X, method_Y = self.locator.get_button_coordinates('method')
        pyautogui.click(method_X, method_Y)
        time.sleep(2)
        open_X, open_Y = self.locator.get_button_coordinates('method_open')
        pyautogui.click(open_X, open_Y)
        time.sleep(2)
        if method == 'normal':
            method_file_X, method_file_Y = self.locator.get_button_coordinates('normal_method_file')
            pyautogui.click(method_file_X, method_file_Y)
            pyautogui.click(method_file_X, method_file_Y)
            time.sleep(2)
        elif method == 'blitz':
            method_file_X, method_file_Y = self.locator.get_button_coordinates('blitz_method_file')
            pyautogui.click(method_file_X, method_file_Y)
            pyautogui.click(method_file_X, method_file_Y)
            time.sleep(2)
    
    def save_and_export_results(self, file_path_imicro, random_name):
        """
        Automates the process of saving and exporting results, including file renaming and exporting as CSV.

        Parameters:
            file_path_imicro (str): The file path to be entered during the 'Save As' step.
            random_name (str): The random name to be used for saving the file.
        """
        # Step 1: Click on 'Review Data'
        review_data_X, review_data_Y = self.locator.get_button_coordinates('review data')
        pyautogui.click(review_data_X, review_data_Y)
        time.sleep(2)
        
        new_data_X, new_data_Y = self.locator.get_button_coordinates('new data available')
        pyautogui.click(new_data_X, new_data_Y)
        time.sleep(2)

        # Step 2: Click on 'Sample File'
        sample_file_X, sample_file_Y = self.locator.get_button_coordinates('sample file')
        pyautogui.click(sample_file_X, sample_file_Y)
        time.sleep(2)

        # Step 3: Click on 'Save As'
        saveas_X, saveas_Y = self.locator.get_button_coordinates('save as')
        pyautogui.click(saveas_X, saveas_Y)
        time.sleep(2)

        # Step 4: Enter the file path for 'Save As'
        image_name = 'save as file name'
        window_image_path = f"{self.image_directory}/{image_name}.png"
        edges = ScreenUtils.find_image_edges_on_screen(window_image_path, monitor_index=2, threshold=0.8)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = edges

        # Click at the rightmost and center Y
        click_x = top_left_x
        click_y = (top_left_y + bottom_right_y) // 2
        pyautogui.click(click_x, click_y)
        time.sleep(2)

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(2)
        pyautogui.write(file_path_imicro, interval=0.1)
        time.sleep(2)
        pyautogui.press('enter')

        # Step 5: Rename the file with a random name
        image_name = 'file name for saving'
        window_image_path = f"{self.image_directory}/{image_name}.png"
        edges = ScreenUtils.find_image_edges_on_screen(window_image_path, monitor_index=2, threshold=0.8)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = edges

        # Click at the rightmost and center Y
        click_x = bottom_right_x
        click_y = (top_left_y + bottom_right_y) // 2
        pyautogui.click(click_x, click_y)
        time.sleep(2)

        # Enter the random name
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(2)
        pyautogui.write(random_name, interval=0.1)
        time.sleep(2)

        save_for_saving_X, save_for_saving_Y = self.locator.get_button_coordinates('save for saving')
        pyautogui.click(save_for_saving_X, save_for_saving_Y)
        time.sleep(2)

        # Step 6: Click on 'Sample File' again
        sample_file_X, sample_file_Y = self.locator.get_button_coordinates('sample file')
        pyautogui.click(sample_file_X, sample_file_Y)
        time.sleep(2)

        # Step 7: Export the results
        export_X, export_Y = self.locator.get_button_coordinates('export')
        pyautogui.click(export_X, export_Y)
        time.sleep(2)

        csv_X, csv_Y = self.locator.get_button_coordinates('csv')
        pyautogui.click(csv_X, csv_Y)
        time.sleep(2)

        # Step 8: Click on 'InView Run Test'
        inview_X, inview_Y = self.locator.get_button_coordinates('inview run test')
        pyautogui.click(inview_X, inview_Y)
        time.sleep(2)
        
        
    def start_single_Normal_tests(self, name=None, length=8):
        if name is None:            
            # Generate a random name
            random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            name=random_name
        # Engage
        self.engage()
        while True:
             time.sleep(10)
             center_coords = self.locator.get_button_coordinates("abort")
             
             if not center_coords:
                   print(f"Image 'abort' not found. Rechecking in 10 seconds...")
                   time.sleep(10)
                   center_coords_second_check = self.locator.get_button_coordinates("abort")
                   if not center_coords_second_check:
                         print(f"Image 'abort' confirmed as not present. Waiting for 30 more seconds...")
                         time.sleep(30)
                         break
                   else:
                          print("Second check failed. Restarting wait loop...")
             else:
                   print("Image 'abort' found. Still waiting for it to disappear...")
                   
        # Click the "start" button
        start_X, start_Y = self.locator.get_button_coordinates("start")
        pyautogui.click(start_X, start_Y)
        time.sleep(2)
        
		# Find edges of the image
        image_name='file name'
        window_image_path = f"{self.image_directory}/{image_name}.png"
        edges = ScreenUtils.find_image_edges_on_screen(window_image_path, monitor_index=2, threshold=0.8)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = edges

        # Click at the rightmost and center Y
        click_x = bottom_right_x
        click_y = (top_left_y + bottom_right_y) // 2
        pyautogui.click(click_x, click_y)
        time.sleep(2)

        # Enter the random name
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(2)
        pyautogui.write(name, interval=0.1)
        time.sleep(2)
        
        save_X, save_Y = self.locator.get_button_coordinates("save")  
        pyautogui.click(save_X, save_Y)
		# Now the test is started
        
        while True:
            time.sleep(10)
            center_coords = self.locator.get_button_coordinates('start')
            if center_coords:
                print(f"Image start found at {center_coords}. Waiting for 1 more minute...")
                time.sleep(60)
                break
            else:
                print(f"Image start not found. Still waiting...")
                time.sleep(60) 
                
        # Set extension to 10
        self.set_extension(10, t=2)


    def starting_tests_circles(self, sample_name, t=2):
        
        Add_X,Add_Y = self.locator.get_button_coordinates('add')
        Edit_X, Edit_Y= self.locator.get_button_coordinates('edit')
        Remove_X, Remove_Y= self.locator.get_button_coordinates('remove')
        ClearAll_X, ClearAll_Y= self.locator.get_button_coordinates('clear all')
        dynamic_button_positions = self.locator.evaluate_dynamic_buttons(self.image_directory)
        
        # Perform the sequence of actions
        time.sleep(t)
        pyautogui.click(dynamic_button_positions['sample1'][0], dynamic_button_positions['sample1'][1])
        
        time.sleep(t)
        pyautogui.click(Add_X, Add_Y)
        
        time.sleep(t)
        pyautogui.click(dynamic_button_positions['sample_name'][0], dynamic_button_positions['sample_name'][1])
        
        time.sleep(t)        
        pyautogui.write(sample_name, interval=0.1)
        continue_X,continue_Y = self.locator.get_button_coordinates('continue') 
        
        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)
        
        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)
        
        C_X, C_Y=self.locator.get_button_coordinates('C')
        array_X, array_Y = self.locator.get_button_coordinates('array')  
        
        pyautogui.click(C_X, C_Y)
        time.sleep(t)
        
        pyautogui.click(array_X, array_Y)
        time.sleep(t)
        
        import_X,import_Y = self.locator.get_button_coordinates('import')
        pyautogui.click(import_X,import_Y)
        time.sleep(t)
        
        trial_X,trial_Y = self.locator.get_button_coordinates('trial 1')
        pyautogui.doubleClick(trial_X,trial_Y)
        time.sleep(t)
        
        try:
            filename_X, filename_Y = self.locator.get_button_coordinates('circles_centers')
            pyautogui.doubleClick(filename_X, filename_Y)
            time.sleep(t)
            
        except Exception as e:
            print(f"Error occurred while getting coordinates for 'circles_centers': {e}")
            
            # Try getting 'date modified' coordinates and double-clicking
            date_modified_X, date_modified_Y = self.locator.get_button_coordinates('date modified')
            pyautogui.doubleClick(date_modified_X, date_modified_Y)
            time.sleep(t)
            
            # Retry getting 'circles_centers' coordinates and double-clicking
            filename_X, filename_Y = self.locator.get_button_coordinates('circles_centers')
            pyautogui.doubleClick(filename_X, filename_Y)
            time.sleep(t)           
        
        pyautogui.click(continue_X, continue_Y)
        time.sleep(t)
    

   
    
    
		

    
        




    
    

    
