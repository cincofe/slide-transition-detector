# -*- coding: utf-8 -*-

import cv2
try:
    from icecream import ic
except ImportError:
    ic = lambda *args, **kwargs: None  # No-op if icecream is not installed  # noqa: E731

MatLike = cv2.typing.MatLike

class Timeline(object):
    """
    The Timeline represents a logical sequence of frames, where the
    rendering of frames from the video stream will be done through
    lazy evaluation.
    The reader_head property is synchronized with the current
    position of the video stream, which is the current frame that
    is being read. The reader_head will be incremented by the step
    size after each frame is read. The step size is defined in the
    default initializer.
    """
    # reader_head = 0

    def __init__(self, stream:cv2.VideoCapture, step:int=1) -> None:
        """
        Default Initializer
        :param stream: the video stream from OpenCV
        :param step: the step size for reading frames from the video stream. 
        """
        self.step: int = step
        self.stream: cv2.VideoCapture = stream
        self.len: int = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps: float = stream.get(cv2.CAP_PROP_FPS)

    def __del__(self):
        """ Destructor to release the video stream when the Timeline object is deleted. """
        if hasattr(self, 'stream') and isinstance(self.stream, cv2.VideoCapture):
            self.stream.release()
    
    @property
    def reader_head(self) -> int:
        """ Returns the current position of the reader head in the
        video stream, which is the current frame being read.
        This is synchronized with the current position of the video stream.
        :return: the current position of the reader head in the video stream
        """
        if not isinstance(self.stream, cv2.VideoCapture):
            raise ValueError("The stream is not a valid cv2.VideoCapture object.")
        return int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
    
    @reader_head.setter
    def reader_head(self, value: int) -> None:
        """ Sets the current position of the reader head in the
        video stream, which is the frame that will be read next.
        This will also set the position of the video stream to the
        specified value.
        :param value: the position of the reader head in the video stream
        """
        if not isinstance(self.stream, cv2.VideoCapture):
            raise ValueError("The stream is not a valid cv2.VideoCapture object.")
        # No need to check if value is within bounds, as OpenCV will
        # automatically handle it by clipping the value to the valid range.
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, value)

    def next_frame(self) -> tuple[int, MatLike | None]:
        """
        This method reads the next frame from the video stream and
        append it to the rendered_frames list. It also increments the
        reader_head by  self.step.
        :return: A tuple containing the position of the frame in the
        sequence and the frame itself.
        If the video stream has been completely read, it will return
        the current position and None.
        """
        pos = self.reader_head
        # if pos >= self.len:
        #     # Workaround for the issue below
        #     ic("Reached end of video stream")
        #     return pos, None
        
        ret, frame = self.stream.read()
        if not ret:
            return pos, None

        if self.step > 1:
            self.reader_head += self.step - 1  
            # -1 because the stram.read() already increments the reader_head by 1

        return pos, frame

    def get_frame(self, pos: int) -> MatLike | None:
        """
        Returns the frame at the given position of the frame sequence
        and increments the reader_head by self.step.
        If the position is out of bounds, it will return None and will 
        not modify the reader_head.
        :param pos: the position of the frame in the sequence
        :return: the frame at the specified position
        """
        if pos < 0 or pos >= self.len:
            return None
    
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = self.stream.read()
        if not ret:
            return None

        if self.step > 1:
            self.reader_head = pos + self.step - 1  
            # -1 because the stram.read() already increments the reader_head by 1
        
        return frame

    def get_frames(self, start, end) -> list[MatLike | None]:
        """
        Returns the list of frames at between the specified start and
        end position in the frame sequence, stepping every self.step.
        The reader_head will be updated to self.step beyond the last 
        returned frame.
        :param start: Where the frame sequence should start
        :param end: Where the frame sequence should end
        :return: the frame sequence from start to end
        """
        assert end >= start
        assert start >= 0

        result = []
        for i in range(start, end,  self.step):
            result.append(self.get_frame(i))
        return result

    def release_stream(self):
        self.stream.release()


# # The SlidingWindow class is currently not used in the codebase.
# # It is provided here for reference and potential future use.
#
# class SlidingWindow(object):
#     """
#     This class represents an adaptive sliding window. Meaning
#     that it has a pointer to the start position of the window
#     and its size. The size of the window can be changed at any
#     time. Move operations and shrink and expand operations are
#     included.
#     """
#     def __init__(self, timeline, pos=0, size=2):
#         """
#         Default Initializer for the sliding window
#         :param timeline: the timeline where the sliding window
#         should be applied
#         :param pos: the position where the beginning of the
#         window points to
#         :param size: the size of the window
#         """
#         self.timeline = timeline
#         self.pos = pos
#         self.size = size

#     def move_right(self):
#         """
#         This method does this:
#         ░|░|█|█|░|░ => ░|░|░|█|█|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.pos += 1

#     def move_left(self):
#         """
#         This method does this:
#         ░|░|█|█|░|░ => ░|█|█|░|░|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.pos -= 1

#     def shrink_from_left(self):
#         """
#         This method does this:
#         ░|░|█|█|░|░ => ░|░|░|█|░|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.pos += 1
#         self.size -= 1

#     def shrink_from_right(self):
#         """
#         This method does this:
#         ░|░|█|█|░|░ => ░|░|█|░|░|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.size -= 1

#     def expand_to_left(self):
#         """
#         This method does this:
#         ░|░|█|█|░|░ => ░|█|█|█|░|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.pos -= 1
#         self.size += 1

#     def expand_to_right(self):
#         """
#         This method does$$ this:
#         ░|░|█|█|░|░ => ░|░|█|█|█|░
#         1 2 3 4 5 6    1 2 3 4 5 6
#         :return: the changed list of frame
#         """
#         self.size += 1

#     def get_frames(self):
#         """
#         Retrieves all the frames that are currently in this adaptive
#         sliding window.
#         :return: the frames in the sliding window
#         """
#         return self.timeline.get_frames(self.pos, self.pos + self.size)

#     def get_frame(self, pos):
#         return self.timeline.get_frame(self.pos)

#     def get_start_frame(self):
#         return self.timeline.get_frame(self.pos)

#     def get_end_frame(self):
#         return self.timeline.get_frame(self.pos + self.size - 1)

#     def at_end(self):
#         return self.pos + self.size == self.timeline.len
