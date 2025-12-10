import cv2
import numpy as np

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        image = param
        # Get the BGR color of the pixel
        bgr_color = image[y, x]
        
        # Convert to HSV
        hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
        
        print(f"Clicked at ({x}, {y})")
        print(f"BGR: {bgr_color}")
        print(f"HSV: {hsv_color}")
        print(f"Suggested Lower Bound: [{max(0, hsv_color[0]-10)}, {max(0, hsv_color[1]-40)}, {max(0, hsv_color[2]-40)}]")
        print(f"Suggested Upper Bound: [{min(179, hsv_color[0]+10)}, {min(255, hsv_color[1]+40)}, {min(255, hsv_color[2]+40)}]")
        print("-" * 20)

def main():
    image_path = 'GAMBARNYA NICH.jpg'
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # Resize for better view if needed
    image = cv2.resize(image, (640, 480))

    cv2.namedWindow('HSV Picker')
    cv2.setMouseCallback('HSV Picker', mouse_callback, image)

    print("Klik pada bola merah atau hijau untuk melihat nilai HSV-nya.")
    print("Tekan ESC untuk keluar.")

    while True:
        cv2.imshow('HSV Picker', image)
        k = cv2.waitKey(1) & 0xFF
        if k == 27: # ESC
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
