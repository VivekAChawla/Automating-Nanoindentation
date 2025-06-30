import numpy as np
import pyautogui
import time
from automate_alignment import AlignmentAutomation
from button_locator import ButtonLocator
from automation import Automation
from screen_utils import ScreenUtils
import matplotlib.pyplot as plt
from image_processing import ImageProcessing
from ContourOverlayAligner import ContourOverlayAlignerCV
from scipy.interpolate import griddata
import random
import string


class SingleTestAlignment:
    def __init__(self, image_directory="assets"):
        """
        Initializes the SingleTestAlignment class.
        """
        self.alignment_auto = AlignmentAutomation()
        self.auto = Automation()
        self.locator = ButtonLocator(image_directory=image_directory)
        self.image_directory = image_directory

    @staticmethod
    def generate_random_name(length=8):
        """
        Generates a random alphanumeric name.

        Parameters:
            length (int): Length of the random name. Default is 8.

        Returns:
            str: Randomly generated name.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def capture_screenshot_and_find_center(self):
        """
        Captures a screenshot of the current view and finds the crosshair center.

        Returns:
            tuple: (screenshot, crosshair_X, crosshair_Y)
        """
        print("Please make sure the iMicro origin is selected.")

        # Capture screenshot
        x1, y1, x2, y2 = self.locator.get_bounding_box(image_dir=self.image_directory)
        screenshot = ScreenUtils.capture_screen_area(x1, y1, x2, y2)
        plt.imshow(screenshot)
        plt.axis('off')
        plt.title("Captured Screenshot")
        plt.show()

        # Convert to numpy array
        screenshot_np = np.array(screenshot)

        # Find the red cross
        crosshair_X, crosshair_Y, red_mask = ImageProcessing.find_red_cross(screenshot_np)

        # Display the red cross and mask
        ImageProcessing.display_red_cross(screenshot_np, red_mask, (crosshair_X, crosshair_Y) if crosshair_X else None)

        return screenshot_np, crosshair_X, crosshair_Y

    def perform_alignment_procedure(self,screenshot_np, x_amount, x_direction, y_amount, y_direction, file_path_imicro, file_path_user, scale_x, scale_y, mini_origin, alignment_var='MODULUS'):
        """
        Executes the alignment procedure with user-specified movements and engagement.

        Parameters:
            x_amount (float): Distance to move in the X direction.
            x_direction (str): Direction for X movement ('left' or 'right').
            y_amount (float): Distance to move in the Y direction.
            y_direction (str): Direction for Y movement ('up' or 'down').
        """
        self.alignment_auto.define_small_origin(origin=mini_origin)
        initial_xyz=self.auto.get_xyz_positions()

        # Change method to blitz
        self.auto.change_method(method='blitz')

        # Set extension to 8
        self.auto.set_extension(8, t=2)

        # Perform X movement
        self.auto.move(x_amount, x_direction, t=2, tt=10)

        # Perform Y movement
        self.auto.move(y_amount, y_direction, t=2)

        # Engage
        self.auto.engage()

        # Generate a random name
        random_name = self.generate_random_name()
        
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
        pyautogui.write(random_name, interval=0.1)
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
        self.auto.set_extension(10, t=2)
        
        image_path = "start" 
        self.auto.save_and_export_results(file_path_imicro, random_name) 
        image_path = "start"
        user_file_path = f"{file_path_user}/{random_name}_Test1.csv"    
        data, selected_data=self.auto.wait_and_read_file_blitz(image_path, file_path=user_file_path, monitor_index=1, threshold=0.8)
        # # Set extension to 8
        # self.auto.set_extension(8, t=2)
        aligner = ContourOverlayAlignerCV(
			screenshot=screenshot_np,
			selected_data=selected_data,
			scale_x=scale_x,  # Pixels per micron for X-axis
			scale_y=scale_y,  # Pixels per micron for Y-axis
			Z_var=alignment_var  # Variable to plot
		)
        
        a,b =self.alignment_auto.single_test_origin_alignment_based( screenshot_np, aligner, scale_x, scale_y, initial_xyz, Z_var=alignment_var, clim=None)
        return a,b 


        

