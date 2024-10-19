# distance_calculation.py

import numpy as np
from math import sin, sqrt, radians

class DistanceCalculation:
    def __init__(self, fov_horizontal, cameras_distance):
        """
        Initialize the distance calculation class.

        :param fov_horizontal: Field of view (horizontal) in degrees.
        :param cameras_distance: Distance between the two cameras in meters.
        """
        self.fov_horizontal = fov_horizontal
        self.cameras_distance = cameras_distance
        self.pixel_to_angle_ratio_x = None  # To be calculated based on image width

        # Calculate the focal length in pixels based on FOV and image width (640 pixels here)
        # f = image_width / (2 * tan(FOV / 2))
        self.focal_length = 640 / (2 * np.tan(np.radians(fov_horizontal / 2)))  # Assuming image width is 640 pixels

    def update_pixel_to_angle_ratio(self, res_width):
        """
        Update the pixel to angle ratio based on image resolution.

        :param res_width: Resolution width of the image in pixels.
        """
        self.pixel_to_angle_ratio_x = self.fov_horizontal / res_width

    def calculate_distance(self, left_image, right_image):
        """
        Calculate the distance to the object based on left and right images.

        :param left_image: Dictionary containing 'img_center_x', 'obj_center_x', 'angle_of_view_x'.
        :param right_image: Dictionary containing 'img_center_x', 'obj_center_x', 'angle_of_view_x'.
        :return: Dictionary containing 'distance' and 'details'.
        """
        try:
            # Extract parameters from left and right images
            img_center_left_x = left_image['img_center_x']
            obj_center_left_x = left_image['obj_center_x']
            angle_of_view_left_x = left_image['angle_of_view_x']

            img_center_right_x = right_image['img_center_x']
            obj_center_right_x = right_image['obj_center_x']
            angle_of_view_right_x = right_image['angle_of_view_x']

            # Determine the case based on angles
            if angle_of_view_left_x < 0 and angle_of_view_right_x > 0:
                case = "between the cameras"
                internal_angle_left_x = 90 - abs(angle_of_view_left_x)
                internal_angle_right_x = 90 - abs(angle_of_view_right_x)
            elif angle_of_view_left_x > 0 and angle_of_view_right_x > 0:
                case = "to the left of the left camera"
                internal_angle_left_x = 90 + abs(angle_of_view_left_x)
                internal_angle_right_x = 90 - abs(angle_of_view_right_x)
            elif angle_of_view_left_x < 0 and angle_of_view_right_x < 0:
                case = "to the right of the right camera"
                internal_angle_left_x = 90 - abs(angle_of_view_left_x)
                internal_angle_right_x = 90 + abs(angle_of_view_right_x)
            else:
                case = "unknown"
                return {
                    'distance': None,
                    'details': f"Unknown case based on angles: left={angle_of_view_left_x}, right={angle_of_view_right_x}"
                }

            # Calculate internal angle of the object
            internal_angle_obj = 180 - (internal_angle_left_x + internal_angle_right_x)

            if internal_angle_obj <= 0:
                return {
                    'distance': None,
                    'details': "Invalid internal angles leading to degenerate triangle."
                }

            # Convert angles to radians
            internal_angle_right_x_rad = radians(internal_angle_right_x)
            internal_angle_left_x_rad = radians(internal_angle_left_x)
            internal_angle_obj_rad = radians(internal_angle_obj)

            # Calculate distance using trigonometric relations
            denominator = (sin(internal_angle_obj_rad) ** 2)
            if denominator == 0:
                return {
                    'distance': None,
                    'details': "Division by zero encountered in distance calculation."
                }

            numerator = (sin(internal_angle_left_x_rad) ** 2) + (sin(internal_angle_right_x_rad) ** 2)
            # Ensure that the value inside sqrt is positive
            value_inside_sqrt = 2 * (numerator / denominator) - 1
            if value_inside_sqrt < 0:
                return {
                    'distance': None,
                    'details': "Invalid value inside square root in distance calculation."
                }

            distance_to_object_x = (self.cameras_distance / 2) * sqrt(
                value_inside_sqrt
            )

            return {
                'distance': distance_to_object_x,
                'details': f"Object is {case}."
            }

        except Exception as e:
            return {
                'distance': None,
                'details': f"Error during distance calculation: {e}"
            }


    def calculate_distance_using_disparity(self, left_image, right_image):
        """
        Calculate the distance using the disparity (difference in object positions) and focal length.
        """
        try:
            # Get the object centers from the left and right images
            obj_center_left_x = left_image['obj_center_x']
            obj_center_right_x = right_image['obj_center_x']

            # Calculate the disparity (difference in x coordinates)
            disparity = obj_center_left_x - obj_center_right_x

            # Ensure disparity is not zero
            if disparity == 0:
                return {
                    'distance': None,
                    'details': "Disparity is zero, unable to calculate distance."
                }

            # Calculate the distance using disparity and focal length
            distance_to_object_disparity = (self.focal_length * self.cameras_distance) / disparity

            return {
                'distance': distance_to_object_disparity,
                'details': "Distance calculated using disparity and focal length."
            }

        except Exception as e:
            return {
                'distance': None,
                'details': f"Error calculating distance using disparity: {e}"
            }