# SC_ROI
Spinal cord ROI [^1] drawing tool

## Dependency
#### Python 2.7
- numpy
- matplotlib (>= 1.5 works but GUI was optimized on version 2.0)
- nibabel

#### [python-tk](https://wiki.python.org/moin/TkInter):
- Ubuntu/Debian: `sudo apt-get install python-tk`
- Fedora: `yum install tkinter`

## Installation
We don't have any fancy installation method yet.
1. Download to any directory: `git clone git@github.com:junqianxulab/SC_ROI.git`
2. Give executable permission to the main file: `chmod +x {download_directory}/SC_ROI/draw_sc_roi/draw_sc_roi.py`
3. Make a symbolic link in a user directory (e.g. `ln -s {download_directory}/SC_ROI/draw_sc_roi/draw_sc_roi.py ${HOME}/bin`) or a system directory (e.g. `ln -s {download_directory}/SC_ROI/draw_sc_roi/draw_sc_roi.py /local/bin`).
- Note that the directory containing the symbolic link should be in a PATH environment.
4. Try `draw_sc_roi.py`

## Documentation
- [Manual](manual/manual.md)

#### under construction


## References
[^1]: Xu et al., Improved in vivo diffusion tensor imaging of human cervical spinal cord, NeuroImage, 2013

