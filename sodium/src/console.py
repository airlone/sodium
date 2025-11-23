from typing import Tuple
import datetime
import shutil
import os 
class GradientConsole:
    def __init__(
        self,
        start_color: Tuple[int, int, int],
        end_color: Tuple[int, int, int],
    ):
        
        self.start_color = start_color
        self.end_color = end_color
        self.steps = 20
        self.i = 0
        self.direction = 1  

    """
    Interpolates between start_color and end_color.
    returns: Tuple[int, int, int] 
    """
    def interpolate(
        self
    ) -> Tuple[int, int, int]:
        
        ratio = self.i / (self.steps - 1)
        r = int(self.start_color[0] * (1 - ratio) + self.end_color[0] * ratio)
        g = int(self.start_color[1] * (1 - ratio) + self.end_color[1] * ratio)
        b = int(self.start_color[2] * (1 - ratio) + self.end_color[2] * ratio)

        self.i += self.direction
        if self.i >= self.steps - 1:
            self.i = self.steps - 1
            self.direction = -1  
        elif self.i <= 0:
            self.i = 0
            self.direction = 1   

        return (r, g, b)
    """
    Prints text to console in color between start and end colors
    """
    def println(
        self, 
        text: str | None = " ",
    ) -> None:
        r, g, b = self.interpolate()
        end_text = f"\t[\033[38;2;{r};{g};{b}m{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\033[0m]\n"
        terminal_width = shutil.get_terminal_size().columns
    

        line_length = len(text) + len(end_text)
        if line_length >= terminal_width:
            print("[INFO]\t\t" + text + " " + end_text, end="")
        else:
            spaces = terminal_width - line_length
            print("[INFO]\t\t" + text + " " * spaces + end_text, end="")


    @staticmethod
    def clear() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')