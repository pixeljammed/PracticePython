import cv2
import numpy as np
import argparse

class LaserPointerDetector:
    def __init__(self, min_area=10, max_area=500, brightness_threshold=200):
        """
        Initialize laser pointer detector

        Args:
            min_area: Minimum area of detected blob
            max_area: Maximum area of detected blob
            brightness_threshold: Minimum brightness for laser detection
        """
        self.min_area = min_area
        self.max_area = max_area
        self.brightness_threshold = brightness_threshold

        # Previous position for smoothing
        self.prev_pos = None

    def detect_laser(self, frame):
        """
        Detect laser pointer in frame

        Args:
            frame: Input frame from camera

        Returns:
            tuple: (x, y) coordinates of laser pointer, or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Threshold to find bright spots
        _, thresh = cv2.threshold(blurred, self.brightness_threshold, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Filter contours by area and find the brightest one
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Calculate average brightness in the region
                roi = gray[y:y+h, x:x+w]
                avg_brightness = np.mean(roi)

                valid_contours.append((contour, avg_brightness))

        if not valid_contours:
            return None

        # Select the brightest contour
        brightest_contour = max(valid_contours, key=lambda x: x[1])[0]

        # Calculate centroid
        M = cv2.moments(brightest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Simple smoothing with previous position
            if self.prev_pos is not None:
                cx = int(0.7 * cx + 0.3 * self.prev_pos[0])
                cy = int(0.7 * cy + 0.3 * self.prev_pos[1])

            self.prev_pos = (cx, cy)
            return (cx, cy)

        return None

    def detect_laser_hsv(self, frame, laser_color='red'):
        """
        Alternative detection method using HSV color space
        Useful for colored laser pointers

        Args:
            frame: Input frame
            laser_color: 'red', 'green', or 'blue'

        Returns:
            tuple: (x, y) coordinates of laser pointer, or None if not found
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define HSV ranges for different laser colors
        color_ranges = {
            'red': [(0, 50, 50), (10, 255, 255)],  # Red range 1
            'red2': [(170, 50, 50), (180, 255, 255)],  # Red range 2 (wraps around)
            'green': [(40, 50, 50), (80, 255, 255)],
            'blue': [(100, 50, 50), (130, 255, 255)]
        }

        if laser_color == 'red':
            # Red has two ranges due to HSV wrap-around
            mask1 = cv2.inRange(hsv, np.array(color_ranges['red'][0]), np.array(color_ranges['red'][1]))
            mask2 = cv2.inRange(hsv, np.array(color_ranges['red2'][0]), np.array(color_ranges['red2'][1]))
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower, upper = color_ranges[laser_color]
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        # Apply morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if self.min_area <= area <= self.max_area:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy)

        return None

def main():
    parser = argparse.ArgumentParser(description='Laser Pointer Detection')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--method', choices=['brightness', 'hsv'], default='brightness',
                       help='Detection method (default: brightness)')
    parser.add_argument('--color', choices=['red', 'green', 'blue'], default='red',
                       help='Laser color for HSV method (default: red)')
    parser.add_argument('--threshold', type=int, default=200,
                       help='Brightness threshold (default: 200)')
    parser.add_argument('--min-area', type=int, default=10,
                       help='Minimum detection area (default: 10)')
    parser.add_argument('--max-area', type=int, default=500,
                       help='Maximum detection area (default: 500)')

    args = parser.parse_args()

    # Initialize detector
    detector = LaserPointerDetector(
        min_area=args.min_area,
        max_area=args.max_area,
        brightness_threshold=args.threshold
    )

    # Initialize camera
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Error: Could not open camera {args.camera}")
        return

    print("Laser Pointer Detection Started")
    print("Press 'q' to quit, 's' to save current frame, 'c' to clear trail")

    # Trail for visualization
    trail_points = []
    max_trail_length = 50

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Detect laser pointer
        if args.method == 'brightness':
            laser_pos = detector.detect_laser(frame)
        else:
            laser_pos = detector.detect_laser_hsv(frame, args.color)

        # Draw detection results
        if laser_pos:
            x, y = laser_pos

            # Add to trail
            trail_points.append((x, y))
            if len(trail_points) > max_trail_length:
                trail_points.pop(0)

            # Draw current position
            cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            # Draw coordinates
            cv2.putText(frame, f"Laser: ({x}, {y})", (x + 15, y - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw trail
        for i in range(1, len(trail_points)):
            alpha = i / len(trail_points)  # Fade effect
            color = (0, int(255 * alpha), 0)
            cv2.line(frame, trail_points[i-1], trail_points[i], color, 2)

        # Display detection method and parameters
        info_text = f"Method: {args.method} | Threshold: {args.threshold}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        if args.method == 'hsv':
            color_text = f"Color: {args.color}"
            cv2.putText(frame, color_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Show frame
        cv2.imshow('Laser Pointer Detection', frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('laser_detection_frame.jpg', frame)
            print("Frame saved as 'laser_detection_frame.jpg'")
        elif key == ord('c'):
            trail_points.clear()
            print("Trail cleared")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()