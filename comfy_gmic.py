import random
import shlex
import subprocess
from pathlib import Path

import folder_paths
from nodes import LoadImage, SaveImage


class GmicCliWrapper:

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(
            random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "command": ("STRING", {
                    "multiline": False
                }),
                "images": ("IMAGE", ),
            }
        }

    RETURN_TYPES = ("IMAGE", )
    FUNCTION = "gmic_filter"
    CATEGORY = "filters"

    def gmic_filter(self, command, images):
        self.compress_level = 4
        imgtemp = SaveImage.save_images(self, images)
        fname = imgtemp['ui']['images'][0]['filename']
        temp_dir = Path(self.output_dir)
        inpath = temp_dir / fname
        outpath = temp_dir / fname.replace('.png', '-out.png')
        try:
            autodash = "" if command.startswith(('-', '+')) else "-"
            gmic_command_args = shlex.split(autodash + command)
            subprocess.check_call([
                'gmic',
                '-input',
                inpath,
            ] + gmic_command_args + [
                '-output',
                outpath,
            ])
            result_image = LoadImage.load_image(self, str(outpath))
        finally:
            if outpath.exists():
                outpath.unlink()
            if inpath.exists():
                inpath.unlink()

        return (result_image[0], )


NODE_CLASS_MAPPINGS = {
    "GmicCliWrapper": GmicCliWrapper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GmicCliWrapper": "GMIC Image Processing",
}
