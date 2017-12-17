import argparse
import cv2
import logging
import sys
import threading
import time
import numpy as np

from desmond.perception import sensor
from desmond.motor import actuator
from desmond import types
from gaze_pb2 import GazeShift

def cut(frame, x, y, w, h):
    x1 = max(x, 0)
    x2 = min(x+w, frame.shape[0])
    y1 = max(y, 0)
    y2 = min(y+h, frame.shape[1])
    return frame[x1:x2, y1:y2, :]

def highlight(frame, x, y, w, h):
    x1 = max(x, 0)
    x2 = min(x+w, frame.shape[0])
    y1 = max(y, 0)
    y2 = min(y+h, frame.shape[1])
    dark = (frame * 0.2).astype(np.uint8)
    dark[x1:x2, y1:y2, :] = frame[x1:x2, y1:y2, :]
    return dark


class GazeCamera(object):
    def __init__(self):
        self.focus_x = 0
        self.focus_y = 0
        self.focus_h = 300
        self.focus_w = 300

    def emit_image_stream(self, device, min_period=25, show=False):
        video_capture = cv2.VideoCapture(device)
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

            # To support some interesting activity, we will support moving the
            # focus of the camera.
            focusframe = cut(frame, self.focus_x, self.focus_y, self.focus_w,
                        self.focus_h)

            ret, buf = cv2.imencode('.jpg', focusframe)
            if not ret:
                logging.debug("Failed to encode image.")
                continue

            # One copy...
            image = types.Image(data=buf.tostring(), encoding=types.Image.JPEG)
            # Another copy...
            s.publish(image)  # And the copy to the socket buffer...
            if show:
                cv2.imshow("frame", highlight(frame, self.focus_x,
                    self.focus_y, self.focus_w, self.focus_h))
                if cv2.waitKey(min_period) & 0xFF == ord('q'):
                    break
            else:
                try:
                    remaining = min_period / 1000.0 - (time.time() - start)
                    if remaining > 0:
                        time.sleep(remaining)
                except KeyboardInterrupt:
                    break

        video_capture.release()
        cv2.destroyAllWindows()

    def handle_gaze(self):
        a = actuator.Receiver("Gaze", GazeShift)
        while True:
            cmd = a.recv_cmd()
            print(cmd.payload)
            a.send_ok(cmd.sender)
            try:
                self.focus_x += cmd.payload.dx
                self.focus_y += cmd.payload.dy
            except:
                pass

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
    gaze_cam = GazeCamera()
    t = threading.Thread(target=gaze_cam.handle_gaze)
    t.daemon = True
    t.start()

    gaze_cam.emit_image_stream(args.device, min_period=args.min_period,
            show=args.show)

if __name__ == "__main__":
    main()
