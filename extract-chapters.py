# Import necessary modules
import os  # For interacting with the operating system
import re  # For regular expression matching
import subprocess as sp  # For running external commands
from subprocess import *  # Import subprocess module
from optparse import OptionParser  # For parsing command line options

# Function to parse chapters from a video file using FFmpeg
def parseChapters(filename):
  chapters = []  # Initialize list to store chapters
  command = [ "ffmpeg", '-i', filename]  # FFmpeg command to get information about chapters
  output = ""  # Initialize output variable
  try:
    # Run FFmpeg command and capture its output
    output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
  except CalledProcessError as e:
    output = e.output  # Capture output if an error occurs

  # Iterate through each line of the FFmpeg output
  for line in iter(output.splitlines()):
    # Use regular expression to match chapter information in each line
    m = re.match(r".*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+).*", line)
    num = 0  # Initialize counter
    if m != None:
      # If chapter information is found, extract and store it
      chapters.append({ "name": m.group(1), "start": m.group(2), "end": m.group(3)})
      num += 1  # Increment counter
  return chapters  # Return list of chapters

# Function to get chapters from user input
def getChapters():
  # Initialize option parser
  parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
  # Add option for input file
  parser.add_option("-f", "--file",dest="infile", help="Input File", metavar="FILE")
  # Parse command line options
  (options, args) = parser.parse_args()
  # Check if input file is provided
  if not options.infile:
    parser.error('Filename required')  # Display error message if input file is missing
  # Parse chapters from input file
  chapters = parseChapters(options.infile)
  fbase, fext = os.path.splitext(options.infile)
  # Iterate through chapters
  for chap in chapters:
    # Print start time of each chapter
    print("start:" +  chap['start'])
    # Generate output file name for each chapter
    chap['outfile'] = chap['name'].split(':')[1] + " " + fbase + fext
    chap['origfile'] = options.infile  # Store original file name
    print(chap['outfile'])  # Print generated output file name
  return chapters  # Return list of chapters

# Function to convert chapters into separate video files
def convertChapters(chapters):
  for chap in chapters:
    # Print start time of each chapter
    print("start:" +  chap['start'])
    print(chap)  # Print chapter information
    # FFmpeg command to extract chapter into a separate file
    command = [
        "ffmpeg", '-i', chap['origfile'],
        '-vcodec', 'copy',
        '-acodec', 'copy',
        '-ss', chap['start'],
        '-to', chap['end'],
        chap['outfile']]
    output = ""  # Initialize output variable
    try:
      # Run FFmpeg command and capture its output
      output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
    except CalledProcessError as e:
      output = e.output  # Capture output if an error occurs
      # Raise runtime error with detailed error message
      raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

# Main function
if __name__ == '__main__':
  # Get chapters from input file
  chapters = getChapters()
  # Convert chapters into separate video files
  convertChapters(chapters)
