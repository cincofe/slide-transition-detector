# -*- coding: utf-8 -*-

import argparse
import cv2
from typing import Generator

from slidetd.analyzer import Analyzer
from slidetd import imgcomparison
from slidetd import mediaoutput
from slidetd.slides import Slide
from slidetd import timeline
from slidetd import ui

try:
    from icecream import ic
except ImportError:
    ic = lambda *args, **kwargs: None  # No-op if icecream is not installed  # noqa: E731

MatLike = cv2.typing.MatLike

# # The InfiniteCounter class is commented out because it is not used in the current implementation.
# # It was originally intended to be used for counting frames in the video stream,
# # but this required to synchronize the reader head with the current position of the video stream.
# # This is now taken care of by the Timeline class, using the reader_head property
# # that mirrors the actual reader head of the video stream.
# # It is kept here for reference in case it is needed in the future.
#
# class InfiniteCounter(object):
#     """
#     InfiniteCounter is a class that represents a counter that will
#     return the next number indefinitely. When the user calls count()
#     return the current number. Then it will increment the current
#     number by the specified steps.
#     """

#     def __init__(self, start=0, step=1):
#         """
#         Default Initializer
#         :param start: the starting value of the counter
#         :param step: the amount that should be added at each step
#         """
#         self.current = start
#         self.step = step

#     def increment(self):
#         self.current += self.step

#     def count(self):
#         """
#         The count method yields the current number and then
#         increments the current number by the specified step in the
#         default initializer
#         :return: the successor from the previous number
#         """
#         while True:
#             yield self.current
#             self.current += self.step


class Detector(Analyzer):

    def __init__(self, device, outpath:str|None=None, fileformat:str=".png", framerate:float=1.0, threshold:float=0.99):
        cap = cv2.VideoCapture(sanitize_device(device))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.step = int(fps / framerate) if fps > 0 else 1
        self.sequence = timeline.Timeline(cap, step=self.step)
        self.writer = mediaoutput.NullWriter()
        if outpath is not None:
            self.writer = mediaoutput.TimestampImageWriter(self.sequence.fps, outpath, fileformat)
        self.comparator = imgcomparison.AbsDiffHistComparator(threshold)

    def detect_slides(self):
        progress = ui.ProgressController('Analyzing Video: ', self.sequence.len)
        progress.start()
        frames = []
        name_getter = mediaoutput.TimestampImageWriter(self.sequence.fps)
        for i, frame in self.check_transition():
            progress.update(i)
            if frame is not None:
                frames.append(Slide(name_getter.next_name([i]), frame))


        progress.finish()

        # self.sequence.release_stream()  # This is not needed, as the Timeline class will handle it
        # Reset the reader head to the beginning of the video stream
        self.sequence.reader_head = 0

        return frames


    def check_transition(self) -> Generator[tuple[int, MatLike | None], None, None]:
        # prev_frame = self.sequence.next_frame()
        prev_frame: MatLike | None = None
        frame: MatLike | None = None
        START_FRAME = 0
        prev_frame = self.sequence.get_frame(START_FRAME)
        self.writer.write(prev_frame, START_FRAME)
        yield START_FRAME, prev_frame

        # ic("Starting external loop")
        while True:
            pos, frame = self.sequence.next_frame()

            if frame is None:
                ic("Reached end of video stream in the external loop")
                break

            if not self.comparator.are_same(prev_frame, frame):
                # ic("Frames are different, entering inner loop", pos)

                # I believe that the following loop that checks for similar frames
                # inside a smooth transition. If this is confirmed, the code 
                # must be modified to run the inner loop with a step size of 1
                # instead of the downsample factor, maybe a different threshold,
                # and definitely a backtracking mechanism so analyze skipped frames.
                # For the time being, I will disable the while loop if the step
                # is greater than 1.
                
                while True and self.step == 1:
                    ic("Starting inner loop")
                    if self.comparator.are_same(prev_frame, frame):
                        ic("Frames are similar, breaking inner loop", pos)
                        break
                    prev_frame = frame
                    pos, frame = self.sequence.next_frame()
                    if frame is None:
                        ic("Reached end of video stream in the inner loop", pos)
                        break
                # ic("Writing frame at position and yielding", pos)
                self.writer.write(frame, pos)
                yield pos, frame

            prev_frame = frame
            # ic("Yielding None in the outer loop for frame", pos)
            yield pos, None

    def analyze(self):
        for i, frame in self.check_transition():
            _, time = mediaoutput.TimestampImageWriter(self.sequence.fps).next_name([i])
            yield Slide(time, frame)


def sanitize_device(device):
    """returns device id if device can be converted to an integer"""
    try:
        return int(device)
    except (TypeError, ValueError):
        return device


def main(filename: str | None = None):
    Parser = argparse.ArgumentParser(description="Slide Detector")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outpath", help="path to output video file", default="slides/", nargs='?')
    Parser.add_argument("-f", "--fileformat", help="file format of the output images e.g. '.jpg'",
                        default=".png", nargs='?')
    Parser.add_argument("-r", "--framerate", help="frames per second to analyze", default=0.1, type=float, nargs='?')
    Parser.add_argument("-t", "--threshold", help="comparison threshold", default=.95, type=float, nargs='?')
    Args = Parser.parse_args()

    if filename is not None:
        Args.device = filename
    detector = Detector(Args.device, Args.outpath, Args.fileformat, Args.framerate, Args.threshold)

    detector.detect_slides()

