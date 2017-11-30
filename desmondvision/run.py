import argparse
import cv2
import logging
import sys

from desmond.perception import sensor

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    return parser.parse_args()

def main():
    args = parse_args()
    video_capture = cv2.VideoCapture(args.device)
    if not video_capture.isOpened():
        logging.error("Failed to open video capture device.")
        sys.exit(1)

    while True:
        ret, image = video_capture.read()
        if not ret:
            logging.debug("Failed to read frame.")
            continue

        cv2.imshow("frame", image)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
