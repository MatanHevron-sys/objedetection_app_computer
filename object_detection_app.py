# object_detection_app.py
 
import os
import tkinter as tk
from object_detection_yolov5 import ObjectDetectionYOLOv5
from distance_calculation import DistanceCalculation
from gui import GUI
import logging
import cv2

def main():
    """
    Main function to initialize logging, object detection, distance calculation, and the GUI.
    """
    # Configure logging
    logging.basicConfig(
        filename='app.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    logging.info("Application started.")

    # Initialize object detection
    try:
        object_detector = ObjectDetectionYOLOv5()
    except Exception as e:
        logging.error(f"Failed to initialize object detector: {e}")
        print(f"Failed to initialize object detector: {e}")
        return

    # Initialize distance calculation with default parameters
    # These parameters should be adjusted based on your camera setup
    fov_horizontal = 55  # Example field of view in degrees; adjust as needed
    cameras_distance = 0.265  # Distance between cameras in meters; adjust as needed

    distance_calculator = DistanceCalculation(
        fov_horizontal=fov_horizontal,
        cameras_distance=cameras_distance
    )

    # Initialize Tkinter root
    root = tk.Tk()

    # Create the GUI instance with the callback
    gui = GUI(root, None)  # Temporary callback, will set below

    # Define the callback function to handle selected images
    def handle_selected_images(file_paths):
        """
        Processes the selected images: object detection, distance calculation, and information printing.

        :param file_paths: Tuple containing paths to the two selected images.
        """
        try:
            logging.info(f"Selected images: {file_paths}")
            print(f"\nSelected images: {file_paths}")

            # Read both images
            left_image_path = file_paths[0]
            right_image_path = file_paths[1]

            print(f"\nProcessing Left Image: {left_image_path}")
            logging.info(f"Processing Left Image: {left_image_path}")
            img_left = cv2.imread(left_image_path)
            if img_left is None:
                logging.error(f"Failed to read left image: {left_image_path}")
                print(f"Failed to read left image: {left_image_path}")
                return

            print(f"\nProcessing Right Image: {right_image_path}")
            logging.info(f"Processing Right Image: {right_image_path}")
            img_right = cv2.imread(right_image_path)
            if img_right is None:
                logging.error(f"Failed to read right image: {right_image_path}")
                print(f"Failed to read right image: {right_image_path}")
                return

            # Extract resolutions
            res_left = (img_left.shape[1], img_left.shape[0])  # (width, height)
            res_right = (img_right.shape[1], img_right.shape[0])  # (width, height)

            logging.info(f"Left image resolution: {res_left[0]}x{res_left[1]}")
            logging.info(f"Right image resolution: {res_right[0]}x{res_right[1]}")

            print(f"\nLeft Image Resolution: {res_left[0]}x{res_left[1]}")
            print(f"Right Image Resolution: {res_right[0]}x{res_right[1]}")

            # Update pixel_to_angle_ratio_x based on left image's width
            distance_calculator.update_pixel_to_angle_ratio(res_left[0])

            # Perform object detection on both images
            detected_img_left, bounding_boxes_left = object_detector.detect_objects(img_left)
            detected_img_right, bounding_boxes_right = object_detector.detect_objects(img_right)

            # Save the output images
            output_dir_left = os.path.join(os.path.dirname(left_image_path), 'detected_images')
            output_dir_right = os.path.join(os.path.dirname(right_image_path), 'detected_images')
            os.makedirs(output_dir_left, exist_ok=True)
            os.makedirs(output_dir_right, exist_ok=True)

            output_filename_left = f"detected_{os.path.basename(left_image_path)}"
            output_filename_right = f"detected_{os.path.basename(right_image_path)}"
            output_path_left = os.path.join(output_dir_left, output_filename_left)
            output_path_right = os.path.join(output_dir_right, output_filename_right)

            cv2.imwrite(output_path_left, cv2.cvtColor(detected_img_left, cv2.COLOR_RGB2BGR))
            cv2.imwrite(output_path_right, cv2.cvtColor(detected_img_right, cv2.COLOR_RGB2BGR))
            logging.info(f"Saved detected left image to {output_path_left}")
            logging.info(f"Saved detected right image to {output_path_right}")
            print(f"\nSaved detected left image to {output_path_left}")
            print(f"Saved detected right image to {output_path_right}")

            # Assuming one object per image for simplicity
            # If multiple objects per image, additional logic is needed to match objects across images
            if len(bounding_boxes_left) != 1 or len(bounding_boxes_right) != 1:
                logging.warning("Number of detected objects in left and right images do not match or are not equal to 1.")
                print("Warning: Number of detected objects in left and right images do not match or are not equal to 1.")

            # Proceed only if exactly one object is detected in both images
            if len(bounding_boxes_left) == 1 and len(bounding_boxes_right) == 1:
                bbox_left = bounding_boxes_left[0]
                bbox_right = bounding_boxes_right[0]

                # Calculate centers
                obj_center_left_x = (bbox_left['xmin'] + bbox_left['xmax']) // 2
                img_center_left_x = res_left[0] // 2
                angle_of_view_left_x = (img_center_left_x - obj_center_left_x) * distance_calculator.fov_horizontal / res_left[0]

                obj_center_right_x = (bbox_right['xmin'] + bbox_right['xmax']) // 2
                img_center_right_x = res_right[0] // 2
                angle_of_view_right_x = (img_center_right_x - obj_center_right_x) * distance_calculator.fov_horizontal / res_right[0]
                

                # Prepare dictionaries for DistanceCalculation
                left_image_params = {
                    'img_center_x': img_center_left_x,
                    'obj_center_x': obj_center_left_x,
                    'angle_of_view_x': angle_of_view_left_x
                }

                right_image_params = {
                    'img_center_x': img_center_right_x,
                    'obj_center_x': obj_center_right_x,
                    'angle_of_view_x': angle_of_view_right_x
                }

                # Calculate distance
                distance_info = distance_calculator.calculate_distance(left_image_params, right_image_params)

                # Calculate for print
                res_width_detected_img_right = detected_img_right.shape[1]
                res_height_detected_img_right = detected_img_right.shape[0]
                res_width_detected_img_right = detected_img_right.shape[1]
                res_height_detected_img_right = detected_img_right.shape[0]

                # Print additional parameters
                print(f"\nAdditional Parameters:")
                print(f"  img_center_right_x: {img_center_right_x}")
                print(f"  img_center_left_x: {img_center_left_x}")
                print(f"  obj_center_right_x: {obj_center_right_x}")
                print(f"  obj_center_left_x: {obj_center_left_x}")
                print(f"  angle_of_view_right_x: {angle_of_view_right_x:.2f}")
                print(f"  angle_of_view_left_x: {angle_of_view_left_x:.2f}")
                print(f"  res_img_left_width: {res_left[0]}") #should be 640
                print(f"  res_img_left_height: {res_left[1]}") #should be 480
                print(f"  res_img_right_width: {res_right[0]}") #should be 640
                print(f"  res_img_right_height: {res_right[1]}") #should be 480
                print(f"  res_detected_img_right_width: {res_width_detected_img_right}") #should be 640
                print(f"  res_detected_img_right_height: {res_height_detected_img_right}") #should be 480
                print(f"  res_detected_img_left_width: {res_width_detected_img_right}") #should be 640
                print(f"  res_detected_img_left_height: {res_height_detected_img_right}") #should be 480
                

                # Display images and resolutions in the GUI
                gui.display_images(detected_img_left, detected_img_right)
                gui.update_resolution(
                    res_left=res_left,
                    res_right=res_right
                )

                ### try to calculate with other mathematic way 
                distance_info_disparity = distance_calculator.calculate_distance_using_disparity(left_image_params, right_image_params)
                print(f"Distance (using disparity): {distance_info_disparity['distance']:.2f} meters")

                # Print distance information
                if distance_info['distance'] is not None:
                    print(f"\nDistance to the object: {distance_info['distance']:.2f} meters ({distance_info['details']})")
                    logging.info(f"Distance to the object: {distance_info['distance']:.2f} meters ({distance_info['details']})")
                else:
                    print(f"\nDistance to the object: Undefined ({distance_info['details']})")
                    logging.warning(f"Distance to the object: Undefined ({distance_info['details']})")
            else:
                print("\nUnable to calculate distance due to multiple or unmatched detections.")
                logging.warning("Unable to calculate distance due to multiple or unmatched detections.")

            print("\nProcessing complete.")
            logging.info("Image processing complete.")
        except Exception as e:
            logging.error(f"Error during image processing: {e}")
            print(f"Error during image processing: {e}")

    # Assign the callback after defining it
    gui.on_select_callback = handle_selected_images

    # Start the Tkinter main loop
    root.mainloop()

    logging.info("Application closed.")

if __name__ == "__main__":
    main()
