import cv2
import math
import matplotlib.pyplot as plt
from automation import Automation
from micro_macro_alignment import MicroMacroAlignment
from image_processing import ImageProcessing

class AlignmentAutomation:
    def __init__(self, macro_image_path=None, macro_scale_x=None, macro_scale_y=None):
        """
        Initialize the AlignmentAutomation object with optional macro image path and scaling factors.
        If macro image parameters are not provided, only micro alignment functionality will be available.
        """
        self.auto = Automation()
        self.rotated_macro_image = None  # To store the rotated macro image
        self.new_origin_macro = None  # To store the new origin of the macro image
        self.new_origin_micro = None  # To store the new origin in the micro image
        self.new_origin_micro_single_test = None  # To store the single-test origin in the micro image
        self.where_we_are_micro = None  # To store the current location in pixels during single-test mode

        # Macro image setup is optional
        if macro_image_path and macro_scale_x and macro_scale_y:
            self.alignment = MicroMacroAlignment(
                macro_image_path=macro_image_path,
                macro_scale_x=macro_scale_x,
                macro_scale_y=macro_scale_y
            )
        else:
            self.alignment = None  # No macro alignment functionality available
    

    def rotate_image_opencv(self, image, angle):
        """
        Rotates an image by a given angle using OpenCV.
        """
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h))
        return rotated

    def automate_alignment(self):
        """
        Automates the alignment process between the micro and macro images.
        """
        # Step 1: Load the macro image
        self.alignment.load_macro_image()

        # Step 2: User clicks on two reference points
        print("Please click on two reference points in the macro image.")
        self.alignment.click_reference_points()

        # Step 3: Get reference points and calculate distances
        reference_points = self.alignment.get_reference_points()
        print(f"Reference points: {reference_points}")
        distance_x, distance_y = self.alignment.calculate_distance_in_microns()
        print(f"Macro Image Distance in X: {distance_x} microns")
        print(f"Macro Image Distance in Y: {distance_y} microns")

        # Step 4: User moves the indenter to the first position
        input("Move the indenter to the first position and press Enter when ready.")
        origin_x, origin_y, origin_extension = self.auto.get_xyz_positions()
        print(f"First Position - X: {origin_x}, Y: {origin_y}, Extension: {origin_extension}")

        # Step 5: User moves the indenter to the second position
        input("Move the indenter to the second position and press Enter when ready.")
        origin_x2, origin_y2, origin_extension2 = self.auto.get_xyz_positions()
        print(f"Second Position - X: {origin_x2}, Y: {origin_y2}, Extension: {origin_extension2}")

        # Step 6: Calculate angles
        Xrange_big, Yrange_big = distance_x, distance_y
        Xrange, Yrange = origin_x - origin_x2, origin_y - origin_y2

        radian_big = math.atan(Yrange_big / Xrange_big)
        degrees_big = math.degrees(radian_big)

        radian_small = math.atan(Yrange / Xrange)
        degrees_small = math.degrees(radian_small)

        rotation_angle = -degrees_small + degrees_big
        # if rotation_angle <= 0:
        #     rotation_angle += 180

        print(f"Small Image Angle: {degrees_small}°")
        print(f"Big Image Angle: {degrees_big}°")
        print(f"Rotation Angle: {rotation_angle}°")

        # Step 7: Rotate the macro image
        self.rotated_macro_image = self.rotate_image_opencv(self.alignment.macro_image, rotation_angle)

        # Step 8: Redefine the origin on the rotated macro image
        print("Please select the new origin on the rotated macro image.")
        self.new_origin_macro = self.select_new_origin()
        self.new_origin_micro = (origin_x2, origin_y2)

        print(f"New origin selected at: {self.new_origin_macro}")

        # Step 9: Display the rotated image
        plt.imshow(cv2.cvtColor(self.rotated_macro_image, cv2.COLOR_BGR2RGB))
        plt.title(f"Rotated Image by {rotation_angle}°")
        plt.axis("on")
        plt.show()

        # Return the rotated image
        return self.rotated_macro_image
    
    def select_new_origin(self):
        """
        Allows the user to select the new origin on the rotated macro image.
        Opens the rotated macro image in a zoomable and pannable window for origin selection.

        Returns:
            tuple: New origin coordinates (x, y) in the rotated macro image.
        """
        if self.rotated_macro_image is None:
            raise ValueError("Rotated macro image not available. Call 'automate_alignment' first.")

        # Convert variables to instance variables to avoid local binding issues
        self.zoom_scale = 1.0  # Initial zoom level
        self.pan_x, self.pan_y = 0, 0  # Initial pan offset
        self.dragging = False  # Dragging state
        self.drag_start_x, self.drag_start_y = 0, 0  # Drag starting coordinates
        points = []  # Store the selected point

        def update_display():
            """ Update the displayed image based on current zoom and pan settings. """
            height, width = self.rotated_macro_image.shape[:2]
            resized = cv2.resize(
                self.rotated_macro_image, (int(width * self.zoom_scale), int(height * self.zoom_scale))
            )
            view_x, view_y = max(0, -self.pan_x), max(0, -self.pan_y)
            end_x = min(resized.shape[1], view_x + width)
            end_y = min(resized.shape[0], view_y + height)
            visible_image = resized[view_y:end_y, view_x:end_x]
            cv2.imshow("Select New Origin", visible_image)

        def click_event(event, x, y, flags, param):
            """ Handles mouse events for selecting, panning, and zooming. """
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((int((x + self.pan_x) / self.zoom_scale), int((y + self.pan_y) / self.zoom_scale)))
                print(f"New Origin Selected: {points[-1]}")
                cv2.destroyWindow("Select New Origin")  # Close the window after selection

            elif event == cv2.EVENT_RBUTTONDOWN:
                self.dragging = True
                self.drag_start_x, self.drag_start_y = x, y

            elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
                dx = x - self.drag_start_x
                dy = y - self.drag_start_y
                self.pan_x -= dx
                self.pan_y -= dy
                self.drag_start_x, self.drag_start_y = x, y
                update_display()

            elif event == cv2.EVENT_RBUTTONUP:
                self.dragging = False

            elif event == cv2.EVENT_MOUSEWHEEL:
                if flags > 0:
                    self.zoom_scale *= 1.1
                else:
                    self.zoom_scale /= 1.1
                self.zoom_scale = max(0.1, min(self.zoom_scale, 10))
                update_display()

        cv2.namedWindow("Select New Origin", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select New Origin", click_event)

        while True:
            update_display()
            key = cv2.waitKey(1)

            if key == 27:  # ESC key to exit without selecting
                print("No origin selected. Window closed.")
                cv2.destroyWindow("Select New Origin")
                return None

            if len(points) > 0:
                break

        return points[0]
    
    def select_points_macro(self):
        """
        Allows the user to select multiple points on the rotated macro image.
        Opens the macro image in a zoomable and pannable window for point selection.

        Controls:
            - Left Click: Select a point (can select multiple).
            - Right Click: Finish selection and close the window.
            - Scroll Wheel: Zoom in/out.
            - Right Click + Drag: Pan the image.
            - ESC: Exit without saving points.

        Returns:
            list of tuples: List of selected points (x, y) in the macro image.
        """
        if self.rotated_macro_image is None:
            raise ValueError("Rotated macro image not available. Call 'automate_alignment' first.")

        self.zoom_scale = 1.0  # Initial zoom level
        self.pan_x, self.pan_y = 0, 0  # Initial pan offsets
        self.dragging = False  # Drag state for panning
        self.drag_start_x, self.drag_start_y = 0, 0  # Drag starting coordinates
        points = []  # Store selected points

        def update_display():
            """ Update the displayed image based on the current zoom and pan settings. """
            height, width = self.rotated_macro_image.shape[:2]
            resized = cv2.resize(
                self.rotated_macro_image, (int(width * self.zoom_scale), int(height * self.zoom_scale))
            )
            view_x, view_y = max(0, -self.pan_x), max(0, -self.pan_y)
            end_x = min(resized.shape[1], view_x + width)
            end_y = min(resized.shape[0], view_y + height)
            visible_image = resized[view_y:end_y, view_x:end_x].copy()

            # Draw all selected points on the displayed image
            for point in points:
                scaled_point = (int(point[0] * self.zoom_scale - self.pan_x), int(point[1] * self.zoom_scale - self.pan_y))
                cv2.circle(visible_image, scaled_point, 5, (255, 0, 0), -1)

            cv2.imshow("Select Points in Macro Image", visible_image)

        def click_event(event, x, y, flags, param):
            """ Handles mouse events for selecting, panning, and zooming. """
            if event == cv2.EVENT_LBUTTONDOWN:
                # Left-click to select a point
                point = (int((x + self.pan_x) / self.zoom_scale), int((y + self.pan_y) / self.zoom_scale))
                points.append(point)
                print(f"Point {len(points)}: {point}")
                update_display()

            elif event == cv2.EVENT_RBUTTONDOWN:
                # Stop selection with right-click
                print("Point selection finished.")
                cv2.destroyWindow("Select Points in Macro Image")

            elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
                # Pan the image by dragging
                dx = x - self.drag_start_x
                dy = y - self.drag_start_y
                self.pan_x -= dx
                self.pan_y -= dy
                self.drag_start_x, self.drag_start_y = x, y
                update_display()

            elif event == cv2.EVENT_RBUTTONUP:
                self.dragging = False

            elif event == cv2.EVENT_MBUTTONDOWN:
                # Start dragging when middle button is pressed
                self.dragging = True
                self.drag_start_x, self.drag_start_y = x, y

            elif event == cv2.EVENT_MOUSEWHEEL:
                # Zoom in/out with scroll wheel
                if flags > 0:
                    self.zoom_scale *= 1.1
                else:
                    self.zoom_scale /= 1.1
                self.zoom_scale = max(0.1, min(self.zoom_scale, 10))
                update_display()

        # Create the OpenCV window and set the mouse callback
        cv2.namedWindow("Select Points in Macro Image", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select Points in Macro Image", click_event)

        print("Left-click to select points. Right-click to finish. ESC to exit without saving.")
        while True:
            update_display()
            key = cv2.waitKey(1)

            if key == 27:  # ESC key to exit without saving
                print("Selection cancelled. No points saved.")
                cv2.destroyWindow("Select Points in Macro Image")
                return []

        return points


    def move_to_points(self, selected_points, params=None):
        """
        Moves to the selected points in the micro image based on the macro image coordinates.

        Parameters:
            selected_points (list of tuple): List of points in the macro image coordinates.
            params (list): Focus plane parameters [a, b, c] for focus adjustment, if any.
        """
        if not selected_points:
            raise ValueError("No points selected.")
        if self.new_origin_macro is None or self.new_origin_micro is None:
            raise ValueError("New origins not set. Please ensure 'automate_alignment' was completed.")

        # Adjust points relative to the new origin in the macro image
        adjusted_points = [(x - self.new_origin_macro[0], y - self.new_origin_macro[1]) for x, y in selected_points]

        # Get the current position in the micro image
        current_x, current_y, _ = self.auto.get_xyz_positions()

        # Move to each adjusted point
        for idx, (macro_dx, macro_dy) in enumerate(adjusted_points):
            # Convert macro deltas to micro deltas
            micro_dx = round(macro_dx / self.alignment.macro_scale_x, 2)
            micro_dy = round(macro_dy / self.alignment.macro_scale_y, 2)

            # Calculate relative move in micro coordinates
            relative_dx = round(micro_dx + (current_x - self.new_origin_micro[0]), 2)
            relative_dy = round(micro_dy + (current_y - self.new_origin_micro[1]), 2)

            # Correct movement directions (macro vs micro inversion)
            move_x = "left" if relative_dx < 0 else "right"
            move_y = "down" if relative_dy > 0 else "up"

            # Move in X direction
            if relative_dx != 0:
                print(f"Moving {abs(relative_dx)} microns in X ({move_x})")
                self.auto.move(abs(relative_dx), move_x)

            # Move in Y direction
            if relative_dy != 0:
                print(f"Moving {abs(relative_dy)} microns in Y ({move_y})")
                self.auto.move(abs(relative_dy), move_y)

            # Focus if parameters are provided
            if params is not None:
                self.auto.focus(params)

            # Update the current position
            current_x, current_y, _ = self.auto.get_xyz_positions()
            
    def define_small_origin(self, origin=None):
        """
        Quickly defines the micro origin using the current XYZ position from get_xyz_positions.
        """
        if origin is None:
            current_xyz = self.auto.get_xyz_positions()
            self.new_origin_micro = (current_xyz[0], current_xyz[1])
            print(f"Defined new small origin in micro system: {self.new_origin_micro}")
        else:
            self.new_origin_micro=origin 
        print(f'origin is : {self.new_origin_micro}')       
        return self.new_origin_micro

    def single_test_origin(self, micro_image, scale_x, scale_y, initial_xyz):
        """
        Updates the X and Y origin of the micro system for single test alignment based on user-selected points
        in the micro image and the current XYZ position underneath the indenter.

        Parameters:
            micro_image (numpy.ndarray): Screenshot of the micro image.
            scale_x (float): Pixels per micron for the X-axis.
            scale_y (float): Pixels per micron for the Y-axis.
            initial_xyz (tuple): Initial XYZ position under the optical lens (X, Y, Z).

        Returns:
            tuple: Updated origin for the micro system in single-test mode (X, Y).
        """
        if self.new_origin_micro is None:
            raise ValueError("Previous origin (self.new_origin_micro) is not set. Ensure automate_alignment was completed.")

        # Display the micro image for user to select two points
        points = []

        def click_event(event, x, y, flags, param):
            """
            Captures two clicked points in the micro image.
            """
            if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
                points.append((x, y))
                print(f"Point {len(points)} selected in micro image: ({x}, {y})")
                if len(points) == 2:
                    cv2.destroyAllWindows()

        # Show the image and capture two points
        cv2.imshow("Select two points: (1) where we thought we were, (2) where we are", micro_image)
        cv2.setMouseCallback("Select two points: (1) where we thought we were, (2) where we are", click_event)
        cv2.waitKey(0)

        if len(points) != 2:
            raise ValueError("Two points must be selected in the micro image.")

        # Extract the selected points
        point_thought, point_actual = points
        print(f"Point we thought we were: {point_thought}")
        print(f"Point where we actually are: {point_actual}")

        # Save the second point as the current location in pixels
        self.where_we_are_micro = point_actual

        # Convert pixel differences to microns
        delta_x_pixels = point_actual[0] - point_thought[0]  # Pixel difference in X
        delta_y_pixels = point_actual[1] - point_thought[1]  # Pixel difference in Y

        delta_x_microns = delta_x_pixels / scale_x  # Convert to microns
        delta_y_microns = delta_y_pixels / scale_y  # Convert to microns

        print(f"Delta in microns: ΔX={delta_x_microns}, ΔY={delta_y_microns}")

        # Get the current XYZ position underneath the indenter
        current_xyz = self.auto.get_xyz_positions()
        print(f"Current XYZ under the indenter: {current_xyz}")

        # Calculate the new origin in the micro system
        old_origin_micro = self.new_origin_micro
        offset_x = current_xyz[0] - initial_xyz[0]  # Micron offset in X
        offset_y = current_xyz[1] - initial_xyz[1]  # Micron offset in Y

        # Adjust the origin to operate under the indenter
        new_origin_x = old_origin_micro[0] + offset_x + delta_x_microns
        new_origin_y = old_origin_micro[1] + offset_y + delta_y_microns

        self.new_origin_micro_single_test = (new_origin_x, new_origin_y)
        print(f"Updated single-test origin in micro system: {self.new_origin_micro_single_test}")

        return self.new_origin_micro_single_test

    def move_single_test_micro(self, micro_image, scale_x, scale_y):
        """
        Moves to a selected point in the micro image during single-test mode.

        Parameters:
            micro_image (numpy.ndarray): Screenshot of the micro image.
            scale_x (float): Pixels per micron for the X-axis.
            scale_y (float): Pixels per micron for the Y-axis.
        """
        if self.where_we_are_micro is None:
            raise ValueError("Current location (self.where_we_are_micro) is not set. Call single_test_origin first.")

        # Display the micro image for the user to select a point
        points = []

        def click_event(event, x, y, flags, param):
            """
            Captures the clicked point in the micro image.
            """
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                print(f"Point selected in micro image: ({x}, {y})")
                cv2.destroyAllWindows()

        # Show the image and capture a point
        cv2.imshow("Select a point to move to in the micro image", micro_image)
        cv2.setMouseCallback("Select a point to move to in the micro image", click_event)
        cv2.waitKey(0)

        if not points:
            raise ValueError("No point was selected in the micro image.")

        # Extract the selected point
        selected_point = points[0]
        print(f"Point selected: {selected_point}")

        # Calculate the pixel differences
        delta_x_pixels = selected_point[0] - self.where_we_are_micro[0]
        delta_y_pixels = selected_point[1] - self.where_we_are_micro[1]

        # Convert pixel differences to microns
        delta_x_microns = delta_x_pixels / scale_x
        delta_y_microns = delta_y_pixels / scale_y

        print(f"Delta in microns: ΔX={delta_x_microns}, ΔY={delta_y_microns}")

        # Move in X direction
        move_x_direction = "left" if delta_x_microns < 0 else "right"
        if delta_x_microns != 0:
            self.auto.move(abs(delta_x_microns+1.5), move_x_direction)

        # Move in Y direction
        move_y_direction = "up" if delta_y_microns < 0 else "down"
        if delta_y_microns != 0:
            self.auto.move(abs(delta_y_microns+0.25), move_y_direction)

        # Update the current location
        self.where_we_are_micro = selected_point
        print(f"Updated current location in pixels: {self.where_we_are_micro}")

    def move_to_points_single_test(self, selected_points, scale_x, scale_y):
        """
        Moves to the selected points in the micro image based on the macro image coordinates 
        in single test mode.

        Parameters:
            selected_points (list of tuple): List of points in the macro image coordinates.
            params (list): Focus plane parameters [a, b, c] for focus adjustment, if any.
        """
        if not selected_points:
            raise ValueError("No points selected.")
        if self.new_origin_macro is None or self.new_origin_micro_single_test is None:
            raise ValueError("New origins not set. Please ensure 'automate_alignment' was completed.")

        # Adjust points relative to the new origin in the macro image
        adjusted_points = [(x - self.new_origin_macro[0], y - self.new_origin_macro[1]) for x, y in selected_points]

        # Get the current position in the micro image
        current_x, current_y, _ = self.auto.get_xyz_positions()

        # Move to each adjusted point
        for idx, (macro_dx, macro_dy) in enumerate(adjusted_points):
            # Convert macro deltas to micro deltas
            micro_dx = round(macro_dx / self.alignment.macro_scale_x, 2)
            micro_dy = round(macro_dy / self.alignment.macro_scale_y, 2)

            # Calculate relative move in micro coordinates
            relative_dx = round(micro_dx + (current_x - self.new_origin_micro_single_test[0]), 2)
            relative_dy = round(micro_dy + (current_y - self.new_origin_micro_single_test[1]), 2)

            # Correct movement directions (macro vs micro inversion)
            move_x = "left" if relative_dx < 0 else "right"
            move_y = "down" if relative_dy > 0 else "up"

            # Move in X direction
            if relative_dx != 0:
                print(f"Moving {abs(relative_dx)} microns in X ({move_x})")
                self.auto.move(abs(relative_dx), move_x)

            # Move in Y direction
            if relative_dy != 0:
                print(f"Moving {abs(relative_dy)} microns in Y ({move_y})")
                self.auto.move(abs(relative_dy), move_y)
            
            # Update the current position
            current_x, current_y, _ = self.auto.get_xyz_positions()
    
    def single_test_origins(self,new_origin_micro_single_test,where_we_are_micro):
        '''defines the single test origins after alignment'''
        
        self.new_origin_micro_single_test=new_origin_micro_single_test
        self.where_we_are_micro=where_we_are_micro
        
        
    def single_test_origin_alignment_based(self, micro_image, aligner, scale_x, scale_y, initial_xyz, Z_var='MODULUS', clim=None):
        """
        Updates the X and Y origin of the micro system for single test alignment based on the crosshair 
        and user-aligned contour plot.

        Parameters:
            micro_image (numpy.ndarray): Screenshot of the micro image.
            aligner (ContourOverlayAlignerCV): Instance of ContourOverlayAlignerCV for alignment.
            scale_x (float): Pixels per micron for the X-axis.
            scale_y (float): Pixels per micron for the Y-axis.
            initial_xyz (tuple): Initial XYZ position under the optical lens (X, Y, Z).
            Z_var (str): Variable for the Z axis in the contour plot.
            clim (tuple, optional): Color limits for the contour plot. Defaults to None.

        Returns:
            tuple: Updated origin for the micro system in single-test mode (X, Y) and current location (bottom-right).
        """
        if self.new_origin_micro is None:
            raise ValueError("Previous origin (self.new_origin_micro) is not set. Ensure automate_alignment was completed.")
        print()
        # Find the red cross in the micro image
        crosshair_X, crosshair_Y, _ = ImageProcessing.find_red_cross(micro_image)
        if crosshair_X is None or crosshair_Y is None:
            raise ValueError("Red cross not found in the micro image.")
        point_thought = (crosshair_X, crosshair_Y)
        print(f"Point we thought we were: {point_thought}")
        
        # Configure and align the contour plot
        aligner.show_contour_plot(clim=clim)  # Show contour plot for user confirmation
        contour_bottom_right_x, contour_bottom_right_y = aligner.start_alignment()  # Start alignment for user to adjust the contour
        
        point_actual = (contour_bottom_right_x, contour_bottom_right_y)
        if point_actual is None:
            raise ValueError("Contour alignment was not completed or not confirmed.")
        print(f"Point where we actually are: {point_actual}")
        self.where_we_are_micro = point_actual
        
        # Convert pixel differences to microns
        delta_x_pixels = point_actual[0] - point_thought[0]  # Pixel difference in X
        delta_y_pixels = point_actual[1] - point_thought[1]  # Pixel difference in Y
        
        delta_x_microns = float(delta_x_pixels) / scale_x  # Convert to microns
        delta_y_microns = float(delta_y_pixels) / scale_y  # Convert to microns
        
        print(f"Delta in microns: ΔX={delta_x_microns}, ΔY={delta_y_microns}")
        
        # Get the current XYZ position underneath the indenter
        current_xyz = self.auto.get_xyz_positions()
        print(f"Current XYZ under the indenter: {current_xyz}")
        
        # Calculate the new origin in the micro system
        old_origin_micro = self.new_origin_micro
        offset_x = current_xyz[0] - initial_xyz[0]  # Micron offset in X
        offset_y = current_xyz[1] - initial_xyz[1]  # Micron offset in Y
        
        # Adjust the origin to operate under the indenter
        new_origin_x = float(old_origin_micro[0]) + offset_x + delta_x_microns
        new_origin_y = float(old_origin_micro[1]) + offset_y + delta_y_microns
        
        self.new_origin_micro_single_test = (new_origin_x, new_origin_y)
        print(f"Updated single-test origin in micro system: {self.new_origin_micro_single_test}")
        
        a = (new_origin_x, new_origin_y)
        b = (float(point_actual[0]), float(point_actual[1]))  # Convert to standard Python float
        print(f"a, b are {a} and {b}")
        
        return a, b

    
        
        

    
            
        
    

    


		
    

