import os  
import re  
import subprocess as sp  
from subprocess import * 
import argparse

class ChapterExtractor:
  def __init__(self, infile):
    self.infile = infile
    self.chapters = []
    
  def checkInputFile(self):
    """
    Checks if the input file has a valid extension.
    Raises:
      ValueError: If the input file does not have an '.m4b' extension.
    """
    if not self.infile.lower().endswith('.m4b'):
      raise ValueError("Input file must be an m4b file")

  def parseChapters(self):
    """
    Parses chapters from the input media file using ffmpeg.
    This method runs an ffmpeg command to extract chapter information from the input file.
    It then processes the output to find chapter details and appends them to the `chapters` attribute.
    Raises:
      CalledProcessError: If the ffmpeg command fails.
    Appends:
      dict: A dictionary containing chapter information with keys:
        - "name": The chapter identifier (e.g., "0:0").
        - "start": The start time of the chapter (e.g., "0.000000").
        - "end": The end time of the chapter (e.g., "10.000000").
    """
    command = ["ffmpeg", '-i', self.infile]
    output = ""
    try:
        output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
    except CalledProcessError as e:
        output = e.output

    for line in iter(output.splitlines()):
        m = re.match(r".*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+).*", line)
        if m:
            self.chapters.append({"name": m.group(1), "start": m.group(2), "end": m.group(3)})
    print(f"Parsed chapters: {self.chapters}")

  def getChapters(self):
    """
    Extracts chapter information and prepares output filenames.
    This method processes the chapters associated with the input file,
    generating output filenames based on the chapter names and the input
    file's base name and extension. It also stores the original input file
    name in each chapter's dictionary.
    Returns:
      list: A list of dictionaries, each containing chapter information
          including 'outfile' (the generated output filename) and
          'origfile' (the original input file name).
    """
    fbase, fext = os.path.splitext(self.infile)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    for chap in self.chapters:
        chap['outfile'] = os.path.join(output_dir, chap['name'].split(':')[1] + " " + fbase + fext)
        chap['origfile'] = self.infile
    print(f"Chapters with output filenames: {self.chapters}")
    return self.chapters

  def convertChapters(self):
    """
    Converts chapters of an audio or video file using ffmpeg.
    This method iterates over the chapters stored in the `self.chapters` attribute,
    and for each chapter, it constructs and executes an ffmpeg command to extract
    the chapter from the original file and save it to the specified output file.
    Raises:
      RuntimeError: If the ffmpeg command returns an error.
    Example:
      self.chapters = [
        {
          'origfile': 'input.mp4',
          'start': '00:00:00',
          'end': '00:05:00',
          'outfile': 'chapter1.mp4'
        },
        ...
      ]
      self.convertChapters()
    """
    for chap in self.chapters:
        command = [
            "ffmpeg", '-i', chap['origfile'],
            '-vcodec', 'copy',
            '-acodec', 'copy',
            '-ss', chap['start'],
            '-to', chap['end'],
            chap['outfile']]
        try:
            sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
            print(f"Converted chapter {chap['name']} to {chap['outfile']}")
        except CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract chapters from a m4b file")
  parser.add_argument("-f", "--file", dest="infile", required=True, help="m4v file to extract chapters from")
  args = parser.parse_args()
  
  extractor = ChapterExtractor(args.infile)
  extractor.checkInputFile()
  extractor.parseChapters()
  extractor.getChapters()
  extractor.convertChapters()