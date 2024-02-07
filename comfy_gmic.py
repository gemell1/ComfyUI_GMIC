import io
import os
import random
import tempfile

from PIL import Image

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
        inpath = "{}\{}".format(self.output_dir, fname)

        filter_id = command.split(" ")[0]
        fd, outpath = tempfile.mkstemp(
            prefix="GMIC--{}".format(filter_id),
            suffix=".png",
            dir=None,
        )
        autodash = "" if command.startswith(('-', '+')) else "-"
        gmic_cli_command = 'gmic -input {} {}{} -output "{}"'.format(
            inpath, autodash, command, outpath)
        os.system(gmic_cli_command)

        image3 = LoadImage.load_image(self, outpath)

        return (image3[0], )


NODE_CLASS_MAPPINGS = {
    "GmicCliWrapper": GmicCliWrapper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GmicCliWrapper": "GMIC Image Processing",
}
