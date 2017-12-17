import argparse
import cv2
import logging
import sys
import time

from desmond.perception import sensor
from desmond import types

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--name", help="Sensor name", default="Camera")
    parser.add_argument("--show", '-s', action="store_true",
                        help="Display images as they are captured.")
    parser.add_argument("--min_period", '-p', type=int, default=25,
                        help="Minimum delay (in milliseconds) between frames")
    return parser.parse_args()

def main():
    args = parse_args()
    video_capture = cv2.VideoCapture(args.device)
    if not video_capture.isOpened():
        logging.error("Failed to open video capture device.")
        sys.exit(1)

    s = sensor.Sensor("Camera", types.Image)
    while True:
        start = time.time()
        ret, frame = video_capture.read()
        if not ret:
            logging.debug("Failed to read frame.")
            continue

        ret, buf = cv2.imencode('.jpg', frame)
        if not ret:
            logging.debug("Failed to encode image.")
            continue

        # One copy...
        image = types.Image(data=buf.tostring(), encoding=types.Image.JPEG)
        # Another copy...
        s.publish(image)  # And the copy to the socket buffer...
        if args.show:
            cv2.imshow("frame", frame)
            if cv2.waitKey(args.min_period) & 0xFF == ord('q'):
                break
        else:
            try:
                remaining = args.min_period / 1000.0 - (time.time() - start)
                if remaining > 0:
                    time.sleep(remaining)
            except KeyboardInterrupt:
                break


    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
