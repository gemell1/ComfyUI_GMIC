import os
import random
import shlex
import subprocess
from pathlib import Path

import folder_paths
from nodes import LoadImage, SaveImage
import torch

class GmicCliWrapper:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(
            random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

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
    FUNCTION = "gmicCli"
    CATEGORY = "image/preprocessors"

    def gmicCli(self, command, images):
        temp_dir = Path(self.output_dir)
        
        results = []
        for (batch_number, image) in enumerate(images):
            imgtemp = SaveImage.save_images(self, image[None])
            fname = imgtemp['ui']['images'][0]['filename']
            inpath = Path(temp_dir / fname)
            outpath = Path(temp_dir / fname.replace('.png', '-out.png'))
            
            try:
                autodash = "" if command.startswith(('-', '+')) else "-"
                gmic_command_args = shlex.split(autodash + command)
                
                subprocess_args = [
                    'gmic',
                    '-input',
                    str(inpath),
                ] + gmic_command_args + [
                    '-output',
                    str(outpath),
                ]
                
                subprocess.check_call(subprocess_args)
                result_image = LoadImage.load_image(self, str(outpath))
                results.append(result_image[0])
            finally:
                if outpath.exists():
                    outpath.unlink()
                if inpath.exists():
                    inpath.unlink()
            
        if len(results) > 1:
            results = torch.cat(results, dim=0)
        else:
            results = results[0]
        
        return (results, )

class GmicQtWrapper:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(
            random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "reapply_first": ("BOOLEAN", {"default": False}),
                "layers": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", )
    FUNCTION = "gmicQt"
    CATEGORY = "image/preprocessors"

    def gmicQt(self, images, reapply_first, layers):
        temp_dir = Path(self.output_dir)
        
        results = []
        multiple_inpath = []
        for (batch_number, image) in enumerate(images):
            imgtemp = SaveImage.save_images(self, image[None])
            fname = imgtemp['ui']['images'][0]['filename']
            inpath = Path(temp_dir / fname)
            multiple_inpath.append(inpath)
        
        multiple_outpath = []
        for inpath in multiple_inpath:
            outpath = inpath.with_name("processed-" + inpath.name)
            multiple_outpath.append(outpath)
        
        try:
            multiple_input = [str(i) for i in multiple_inpath]
            
            placeholder = "processed-%f"
            multiple_output = str(Path(temp_dir / placeholder))
            subprocess_args = [
                'gmic_qt',
                '--output',
                multiple_output
            ]
            subprocess_args += multiple_input
            
            subprocess.check_call(subprocess_args)
            for outpath in multiple_outpath:
                result_image = LoadImage.load_image(self, str(outpath))
                results.append(result_image[0])
        finally:
            for outpath in multiple_outpath:
                if outpath.exists():
                    outpath.unlink()
            for inpath in multiple_inpath:
                if inpath.exists():
                    inpath.unlink()

        if len(results) > 1:
            results = torch.cat(results, dim=0)
        else:
            results = results[0]
        
        return (results, )


NODE_CLASS_MAPPINGS = {
    "GmicCliWrapper": GmicCliWrapper,
    "GmicQtWrapper": GmicQtWrapper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GmicCliWrapper": "G'MIC Cli",
    "GmicQtWrapper": "G'MIC-Qt",
}
