SNAKE = r"""  \
   \    ___
    \  (o o)
        \_/ \
         λ \ \
           _\ \_
          (_____)_
         (________)=Oo°
"""


def bubble(message):
    """Format message inside a snake speech bubble.

    Preconditions & Boundaries:
    - Line 13: bubble_length = len(message) + 2 (1 space of padding on each side of message).
    - Lines 14-17: Bubble layout composed of top border ('_'), enclosed message line,
      and bottom border ('‾').
    """
    padding = 2
    border_width = len(message) + padding
    top_border = "_" * border_width
    bottom_border = "‾" * border_width
    return f"""
 {top_border}
( {message} )    
 {bottom_border}"""


def say(message):
    print(bubble(message.replace("s", "ss").replace("S", "SS")))
    print(SNAKE)
