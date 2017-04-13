#!/usr/bin/env python

# ref:
# https://www.ncbi.nlm.nih.gov/pubmed/23178538
# http://matplotlib.org/

# TODO: 
#       argparse

from __future__ import print_function
import matplotlib

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button, RadioButtons, Slider
import matplotlib.image as mpimg
from matplotlib.artist import Artist
from tkFileDialog import askopenfilename, asksaveasfilename
import os
import sys
import numpy as np
import nibabel as nib
import sc_roi

class Draw_ROI(object):
    '''
    Draw Spinal Cord ROI
    '''

    #showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, fn_fa=None, fn_b0=None, fn_dw=None):
        #figsize = (7.5, 10) if 'linux' in sys.platform else (6, 8)
        figsize = (6, 8)
        self.fig, (self.ax1, self.ax) = plt.subplots(2, 1, figsize=figsize)
        dirname = os.path.dirname(os.path.realpath(__file__))
        example = mpimg.imread(os.path.join(dirname, 'example_image.png'))
        self.ax1.imshow(example)
        self.ax1.axis([15.5, 319.5, 225.5, -9.5])
        self.ax1.axis('off')
        #self.roi_guide = sc_roi.Roi_guide(self.ax)
        self.canvas = self.fig.canvas
        self.drawings = []
        
        #self.img_fa = nib.load('IPMSA_CSPMV02_AP_3merged_xenc_dti_FA_resampled.nii.gz')
        #self.img_b0 = nib.load('IPMSA_CSPMV02_AP_3merged_xenc_b0_resampled.nii.gz')
        #self.img_dw = nib.load('IPMSA_CSPMV02_AP_3merged_xenc_dwi_resampled.nii.gz')
        shape = 268, 96, 12
        self.img_fa = None
        self.dat_fa = np.zeros(shape, dtype=np.float)
        self.img_b0 = None
        self.dat_b0 = np.zeros(shape, dtype=np.float)
        self.img_dw = None
        self.dat_dw = np.zeros(shape, dtype=np.float)
        self.dat = self.dat_fa

        self.clim_fa = [0.3, 1]
        self.clim_b0 = [0.0, 0.0]
        self.clim_dw = [0.0, 0.0]
        #self.clim_b0 = [self.dat_b0.mean(), self.dat_b0.max()/2]
        #self.clim_dw = [self.dat_dw.mean(), self.dat_dw.max()/2]
        self.clim = self.clim_fa

        self.z = 0
        self.bg = self.ax.imshow(self.dat[:,:,self.z].T, cmap='gray', vmin=self.clim[0], vmax=self.clim[1], origin='low', interpolation='none', animated=True)
        self.ax.axis('off')

        self.set_buttons()

        if fn_fa:
            self.read_img('FA', fn=fn_fa)
        if fn_b0:
            self.read_img('b0', fn=fn_b0)
        if fn_dw:
            self.read_img('DW', fn=fn_dw)

        self.roi_guide = sc_roi.Roi_guide(self.ax, shape=self.dat.shape[:2])
        self.drawings += self.roi_guide.drawings
        self.roi_guide_floats = [ self.roi_guide.to_floats() for z in range(self.dat_fa.shape[2]) ]
        self.roi_guide_float_default = self.roi_guide.to_floats()

        self.clicked = None
        self.start_point = None, None
        self.backup_point = None, None
        self.clicked_button = None
        self.clicked_button_base_weight = None

        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)

        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.roi_guide.plot()

    def draw_callback(self, event=None):
        #print('draw_callback')
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        for artist in self.drawings:
            #self.ax.draw_artist(artist)
            self.ax.draw_artist(artist)
        for artist in self.rois_drawings:
            #self.ax.draw_artist(artist)
            self.ax.draw_artist(artist)
        self.canvas.blit(self.ax.bbox)

    def draw_update(self):
        self.canvas.restore_region(self.background)
        for artist in self.drawings:
            self.ax.draw_artist(artist)
        for artist in self.rois_drawings:
            self.ax.draw_artist(artist)
        self.canvas.blit(self.ax.bbox)

    def save(self):
        '''
    save drawings (roi_guide and roi)
'''
        fn_out = asksaveasfilename(initialdir='.')
        if not fn_out:
            return
        # save current slice drawing
        self.roi_guide_floats[self.z] = self.roi_guide.to_floats()
        with open(fn_out, 'w') as fout:
            fout.write('#%s\n' % (','.join(self.drawing_names)))
            fout.write('#z,roi,num_voxel,(x,y),...\n')
            for z in range(self.dat_fa.shape[2]):
                for ind in range(len(self.rois[z])):
                    fout.write('%s,%s,%s' % (z, ind, len(self.rois[z][ind])))
                    for voxel in self.rois[z][ind]:
                        fout.write(',%s,%s' % voxel)
                    fout.write('\n')
            fout.write('#z,a-e(x,y),f-j(x)\n')
            for z in range(self.dat_fa.shape[2]):
                fout.write(','.join([str(value) for value in self.roi_guide_floats[z]]))
                fout.write('\n')

    def read_img(self, tag='FA', fn=None):
        '''
    read nifti images
'''
        if fn is None:
            fn_in = askopenfilename(initialdir='.')
        else:
            fn_in = fn
        if not fn_in:
            return None
        if not os.path.isfile(fn_in):
            return None

        img = nib.load(fn_in)
        dat = img.get_data()
        if img.affine[0][0] < 0:
            dat_swap = dat.copy()
            for x in range(dat.shape[0]):
                dat[x,:,:] = dat_swap[dat.shape[0]-1-x,:,:]
        if tag == 'FA':
            self.img_fa = img
            self.dat_fa = dat
            self.clim_fa = [0.3, 1]
        elif tag == 'b0':
            self.img_b0 = img
            self.dat_b0 = dat
            self.clim_b0 = [self.dat_b0.mean(), self.dat_b0.max()/2]
        elif tag == 'DW':
            self.img_dw = img
            self.dat_dw = dat
            self.clim_dw = [self.dat_dw.mean(), self.dat_dw.max()/2]
        else:
            print('wrong tag in read_img: %s' % tag)
            return None

        if self.radio.value_selected == tag:
            self.change_bg(tag)

    def read(self):
        '''
    read drawings (roi_guide and roi)
'''
        fn_in = askopenfilename(initialdir='.')
        if not fn_in:
            return
        with open(fn_in) as fin:
            line = fin.readline() # 1st line: roi names
            if line.strip()[1:] != ','.join(self.drawing_names):
                # check roi names
                print('Warning: roi in the save file is not the same as that in this program')
                print('  save file:    %s' % line.strip())
                print('  this program: %s' % (','.join(self.drawing_names)))

            fin.readline() # skip 2nd line: header
            while True:
                line = fin.readline()
                if line[0] == '#':
                    break
                words = line.strip().split(',')
                z, ind = int(words[0]), int(words[1])
                if int(words[2]) > 0:
                    pairs = [float(value) for value in words[3:]]
                    self.rois[z][ind] = [ (pairs[i], pairs[i+1]) for i in range(0, len(pairs), 2) ]
                else:
                    self.rois[z][ind] = []

            self.roi_guide_floats = []
            line = fin.readline() # read after header
            while line:
                self.roi_guide_floats.append([float(value) for value in line.strip().split(',')])
                line = fin.readline()

        self.roi_guide.from_floats(self.roi_guide_floats[self.z])
        self.roi_guide.update_all()
        for ind in range(len(self.rois_drawings)):
            if len(self.rois[self.z][ind]):
                self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
            else:
                self.rois_drawings[ind].set_data([],[])
        #self.canvas.blit(self.ax.bbox)
        self.draw_update()

    def set_buttons(self):
        '''
    create and locate buttons
'''
        self.button_colors = [
                'lime',
                'deeppink',
                'mediumvioletred',
                'lightgreen',
                'steelblue',
                'mediumslateblue',
                'coral',
                'lemonchiffon',
                'red',
                ]
                
        ax_l_ah  = plt.axes([0.39, 0.74, 0.08, 0.04])
        ax_l_cst = plt.axes([0.28, 0.67, 0.10, 0.04])
        ax_l_pc  = plt.axes([0.42, 0.64, 0.08, 0.04])

        ax_r_ah  = plt.axes([0.53, 0.74, 0.08, 0.04])
        ax_r_cst = plt.axes([0.62, 0.67, 0.10, 0.04])
        ax_r_pc  = plt.axes([0.50, 0.64, 0.08, 0.04])

        ax_guide = plt.axes([0.15, 0.53, 0.2, 0.04])
        ax_reset = plt.axes([0.45, 0.53, 0.1, 0.04])

        ax_prev = plt.axes([0.80, 0.53, 0.1, 0.04])
        ax_next = plt.axes([0.80, 0.57, 0.1, 0.04])
        ax_z = plt.axes([0.70, 0.53, 0.10, 0.04])
        ax_z.axis('off')
        ax_z.text(0.1, 0.4, 'slice=')
        self.text_z = ax_z.text(0.8, 0.4, self.z)

        ax_img_read_fa = plt.axes([0.13, 0.84, 0.12, 0.04])
        ax_img_read_b0 = plt.axes([0.25, 0.84, 0.12, 0.04])
        ax_img_read_dw = plt.axes([0.37, 0.84, 0.12, 0.04])
        ax_save = plt.axes([0.70, 0.84, 0.1, 0.04])
        ax_read = plt.axes([0.80, 0.84, 0.1, 0.04])

        ax_rad  = plt.axes([0.02, 0.25, 0.1, 0.1])
        self.ax_vmin = plt.axes([0.1, 0.02, 0.8, 0.03])
        self.ax_vmax = plt.axes([0.1, 0.06, 0.8, 0.03])

        self.button_l_ah  = Button(ax_l_ah, '(1)AH',   color=self.button_colors[0]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_l_cst = Button(ax_l_cst, '(2)CST', color=self.button_colors[1]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_l_pc  = Button(ax_l_pc, '(3)PC',   color=self.button_colors[2]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_r_ah  = Button(ax_r_ah, '(4)AH',   color=self.button_colors[3]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_r_cst = Button(ax_r_cst, '(5)CST', color=self.button_colors[4]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_r_pc  = Button(ax_r_pc, '(6)PC',   color=self.button_colors[5]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_guide  = Button(ax_guide, '(g)uide line', color=self.button_colors[6]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_reset  = Button(ax_reset, 'reset', color=self.button_colors[8]) #, hovercolor=(0.3, 0.2, 0.2))

        self.button_prev  = Button(ax_prev, '(-p)rev', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_next  = Button(ax_next, '(+n)ext', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))

        self.button_read_img_fa  = Button(ax_img_read_fa, 'read FA', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_read_img_b0  = Button(ax_img_read_b0, 'read b0', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_read_img_dw  = Button(ax_img_read_dw, 'read DW', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_save  = Button(ax_save, 'save', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))
        self.button_read  = Button(ax_read, 'read', color=self.button_colors[7]) #, hovercolor=(0.3, 0.2, 0.2))

        self.button_l_ah.on_clicked(lambda  x:self.button_click_callback(x, self.button_l_ah  ))
        self.button_l_cst.on_clicked(lambda x:self.button_click_callback(x, self.button_l_cst ))
        self.button_l_pc.on_clicked(lambda  x:self.button_click_callback(x, self.button_l_pc  ))
        self.button_r_ah.on_clicked(lambda  x:self.button_click_callback(x, self.button_r_ah  ))
        self.button_r_cst.on_clicked(lambda x:self.button_click_callback(x, self.button_r_cst ))
        self.button_r_pc.on_clicked(lambda  x:self.button_click_callback(x, self.button_r_pc  ))
        self.button_guide.on_clicked(lambda x:self.button_click_callback(x, self.button_guide  ))
        self.button_reset.on_clicked(self.reset_roi_guide)

        self.button_read_img_fa.on_clicked(lambda x:self.read_img(tag='FA'))
        self.button_read_img_b0.on_clicked(lambda x:self.read_img(tag='b0'))
        self.button_read_img_dw.on_clicked(lambda x:self.read_img(tag='DW'))

        self.button_prev.on_clicked(self.button_click_callback_prev)
        self.button_next.on_clicked(self.button_click_callback_next)


        self.button_save.on_clicked(lambda x:self.save())
        self.button_read.on_clicked(lambda x:self.read())

        self.drawing_buttons = [
                self.button_l_ah ,
                self.button_l_cst,
                self.button_l_pc ,
                self.button_r_ah ,
                self.button_r_cst,
                self.button_r_pc ,
                ]
        self.drawing_names = [
                'l_AH' ,    # left has smaller x index than right
                'l_CST',
                'l_PC' ,
                'r_AH' ,
                'r_CST',
                'r_PC' ,
                ]
        self.index_button = {}
        for i, button in enumerate(self.drawing_buttons):
            self.index_button[button] = i

        self.rois = [ [ list() for i in range(len(self.index_button)) ] for z in range(self.dat_fa.shape[2]) ]
        self.rois_drawings = [ Line2D([], [], linestyle='none', marker='s', markerfacecolor=self.button_colors[i], markeredgecolor=self.button_colors[i], alpha=0.5, markersize=5.0, animated=True) for i in range(len(self.rois[self.z])) ]
        #self.rois_drawings = [ self.ax.plot([], [], 's', markerfacecolor=self.button_colors[i], markeredgecolor=self.button_colors[i], alpha=0.5, markersize=5.0)[0] for i in range(len(self.rois[self.z])) ]
        for artist in self.rois_drawings:
            self.ax.add_line(artist)

        # radio buttions
        self.radio = RadioButtons(ax_rad, ('FA', 'b0', 'DW'))
        self.radio.on_clicked(self.change_bg)

        # slider
        self.slider_vmin = Slider(self.ax_vmin, 'vmin', 0, max(self.dat.max(), 1.0), valinit=self.clim[0])
        self.slider_vmax = Slider(self.ax_vmax, 'vmax', 0, max(self.dat.max(), 1.0), valinit=self.clim[1])
        self.cid_vmin = self.slider_vmin.on_changed(self.update_clim)
        self.cid_vmax = self.slider_vmax.on_changed(self.update_clim)

    def update_clim(self, val):
        '''
    callback vmin vmax slider
'''
        self.clim[0] = self.slider_vmin.val
        self.clim[1] = self.slider_vmax.val
        self.bg.set_clim(*self.clim)
        #self.canvas.draw()
        self.canvas.blit(self.ax.bbox)
        #self.ax.draw()

    def get_ind_under_point(self, event):
        '''
    get roi_guide that mouse clicked
'''
        'get the index of the vertex under point if within epsilon tolerance'
        eps = 2
        x0 = event.xdata - eps
        x1 = event.xdata + eps
        y0 = event.ydata - eps
        y1 = event.ydata + eps
        for i, point in enumerate(self.roi_guide.points2d):
            if x0 < point.x < x1 and y0 < point.y < y1:
                return point
        return None

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if event.inaxes is None:
            return
        if event.button == 1:
            if self.clicked_button is None:
                return
            if self.clicked_button is self.button_guide:
                # roi_guide
                self.clicked = self.get_ind_under_point(event)
                if self.clicked:
                    self.start_point = event.xdata, event.ydata
                    self.backup_point = self.clicked.x, self.clicked.y
            else:
                if self.clicked_button:
                    # roi
                    self.clicked = True
        elif event.button == 2:
            # fov
            self.start_point = event.xdata, event.ydata
            self.clicked = True
        elif event.button == 3:
            if self.clicked_button is None:
                return
            if self.clicked_button is self.button_guide:
                # roi_guide
                self.clicked = self.get_ind_under_point(event)
                if self.clicked:
                    self.start_point = event.xdata, event.ydata
                    self.backup_point = self.clicked.x, self.clicked.y
            else:
                if self.clicked_button:
                    # roi
                    self.clicked = True

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if event.inaxes is None:
            return
        if event.button == 1:
            if self.clicked_button is None:
                return
            if self.index_button.has_key(self.clicked_button):
                # roi
                ind = self.index_button[self.clicked_button]
                x, y = round(event.xdata), round(event.ydata)
                if (x,y) not in self.rois[self.z][ind]:
                    self.rois[self.z][ind].append((x,y))
                    if len(self.rois[self.z][ind]):
                        self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
                    else:
                        self.rois_drawings[ind].set_data([],[])
                    #self.canvas.draw()
                    #self.canvas.blit(self.ax.bbox)
                    self.draw_update()

        elif event.button == 2:
            pass

        elif event.button == 3:
            if self.clicked_button is None:
                return
            if self.index_button.has_key(self.clicked_button):
                # roi
                ind = self.index_button[self.clicked_button]
                x, y = round(event.xdata), round(event.ydata)
                if (x,y) in self.rois[self.z][ind]:
                    self.rois[self.z][ind].remove((x,y))
                    if len(self.rois[self.z][ind]):
                        self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
                    else:
                        self.rois_drawings[ind].set_data([],[])
                    #self.canvas.draw()
                    #self.canvas.blit(self.ax.bbox)
                    self.draw_update()
        else:
            return
        self.clicked = None
        self.start_point = None, None
        self.backup_point = None, None
    
    # FIXME
    def key_press_callback(self, event):
        'whenever a key is pressed'
        #if not event.inaxes:
        #    return
        if event.key == '-' or event.key == 'p':
            self.button_click_callback_prev()
        elif event.key == '=' or event.key == '+' or event.key == 'n':
            self.button_click_callback_next()
        elif event.key == 'g':
            self.button_click_callback(None, self.button_guide)
        elif event.key == '1':
            self.button_click_callback(None, self.button_l_ah )
        elif event.key == '2':
            self.button_click_callback(None, self.button_l_cst)
        elif event.key == '3':
            self.button_click_callback(None, self.button_l_pc )
        elif event.key == '4':
            self.button_click_callback(None, self.button_r_ah )
        elif event.key == '5':
            self.button_click_callback(None, self.button_r_cst)
        elif event.key == '6':
            self.button_click_callback(None, self.button_r_pc )
        elif event.key == 'a':
            self.change_bg(label='FA')
        elif event.key == 'b':
            self.change_bg(label='b0')
        elif event.key == 'c':
            self.change_bg(label='DW')

        elif event.key == 's':
            self.save()
        elif event.key == 'r':
            self.read()
        #self.canvas.draw()
        self.canvas.blit(self.ax.bbox)

    def motion_notify_callback(self, event):
        'on mouse movement'
        if self.clicked is None:
            return
        if event.inaxes is None:
            return
        if event.button == 1:
            if self.clicked_button is self.button_guide:
                # roi_guide
                x, y = event.xdata - self.start_point[0], event.ydata - self.start_point[1]

                self.roi_guide.update_point_from_event(self.clicked, self.backup_point[0]+x, self.backup_point[1]+y)
                #self.canvas.draw()
                #self.canvas.blit(self.ax.bbox)
                self.draw_update()

            # from matplotlib example: is the following better?
            #self.canvas.restore_region(self.background)
            #self.ax.draw_artist(self.poly)
            #self.ax.draw_artist(self.line)
            #self.canvas.blit(self.ax.bbox)

            else:
                if not self.index_button.has_key(self.clicked_button):
                    return
                # roi
                ind = self.index_button[self.clicked_button]
                x, y = round(event.xdata), round(event.ydata)
                if (x,y) not in self.rois[self.z][ind]:
                    self.rois[self.z][ind].append((x,y))
                    if len(self.rois[self.z][ind]):
                        self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
                    else:
                        self.rois_drawings[ind].set_data([],[])
                    #self.canvas.draw()
                    #self.canvas.blit(self.ax.bbox)
                    self.draw_update()

        elif event.button == 2:
            # fov
            x, y = event.xdata - self.start_point[0], event.ydata - self.start_point[1]
            axis = self.ax.axis()
            self.ax.axis( [axis[0]-x, axis[1]-x, axis[2]-y, axis[3]-y] )
            self.canvas.draw()
            #self.canvas.blit(self.ax.bbox)
            #self.draw_update()
            self.start_point = event.xdata, event.ydata

        elif event.button == 3:
            if self.clicked_button is self.button_guide:
                # roi_guide
                x, y = event.xdata - self.start_point[0], event.ydata - self.start_point[1]
                for point in self.roi_guide.points2d:
                    point.x += x
                    point.y += y
                self.roi_guide.update_all()
                #self.canvas.draw()
                #self.canvas.blit(self.ax.bbox)
                self.draw_update()
                self.start_point = event.xdata, event.ydata
            else:
                if not self.index_button.has_key(self.clicked_button):
                    return
                # roi
                ind = self.index_button[self.clicked_button]
                x, y = round(event.xdata), round(event.ydata)
                if (x,y) in self.rois[self.z][ind]:
                    self.rois[self.z][ind].remove((x,y))
                    if len(self.rois[self.z][ind]):
                        self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
                    else:
                        self.rois_drawings[ind].set_data([],[])
                    #self.canvas.draw()
                    #self.canvas.blit(self.ax.bbox)
                    self.draw_update()

        else:
            return

    def unset_button_click(self, button):
        '''
    set button text to normal
'''
        button.label.set_fontweight(self.clicked_button_base_weight)
        text = button.label.get_text()
        button.label.set_text(text[1:-1])
        self.clicked_button_base_weight = None
        self.clicked_button = None

    def button_click_callback(self, event, button):
        '''
    when button clicked, make font bold
'''
        if button is self.clicked_button:
            self.unset_button_click(button)
        else:
            if self.clicked_button is not None:
                self.unset_button_click(self.clicked_button)

            #button.label.set_fontweight(self.clicked_button_base_weight)
            self.clicked_button_base_weight = button.label.get_fontweight()
            button.label.set_fontweight(1000)
            text = button.label.get_text()
            button.label.set_text('[%s]' % text)
            self.clicked_button = button

        #button.ax.draw_artist(button)
        self.canvas.blit(button.ax.bbox)
        #self.canvas.draw()

    def button_click_callback_prev(self, event=None):
        '''
        z--
'''
        if self.z <= 0:
            return

        # save roi_guide
        self.roi_guide_floats[self.z] = self.roi_guide.to_floats()

        self.z -= 1
        self.text_z.set_text(self.z)

        # update bg
        self.bg.set_data(self.dat[:,:,self.z].T)
        self.bg.set_clim(*self.clim)

        # read roi_guide
        self.roi_guide.from_floats(self.roi_guide_floats[self.z])
        self.roi_guide.update_all()

        # read roi
        for ind in range(len(self.rois_drawings)):
            if len(self.rois[self.z][ind]):
                self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
            else:
                self.rois_drawings[ind].set_data([],[])
        self.canvas.draw()
        #self.canvas.blit(self.ax.bbox)
        #self.draw_update()

    # duplicate. TODO: merge prev and next
    def button_click_callback_next(self, event=None):
        '''
        z++
'''
        if self.z >= self.dat_fa.shape[2]-1:
            return

        # save roi_guide
        self.roi_guide_floats[self.z] = self.roi_guide.to_floats()

        self.z += 1
        self.text_z.set_text(self.z)

        # update bg
        self.bg.set_data(self.dat[:,:,self.z].T)
        self.bg.set_clim(*self.clim)

        # read roi_guide
        self.roi_guide.from_floats(self.roi_guide_floats[self.z])
        self.roi_guide.update_all()

        # read roi
        for ind in range(len(self.rois_drawings)):
            if len(self.rois[self.z][ind]):
                self.rois_drawings[ind].set_data(zip(*self.rois[self.z][ind]))
            else:
                self.rois_drawings[ind].set_data([],[])
        self.canvas.draw()
        #self.canvas.blit(self.ax.bbox)
        #self.draw_update()

    def reset_roi_guide(self, event=None):
        '''
    reset roi_guide
'''
        self.roi_guide.from_floats(self.roi_guide_float_default)
        self.roi_guide.update_all()
        #self.canvas.draw()
        #self.canvas.blit(self.ax.bbox)
        self.draw_update()

    def change_bg(self, label):
        '''
    change background image 
'''
        self.slider_vmin.disconnect(self.cid_vmin)
        self.slider_vmax.disconnect(self.cid_vmax)

        if label == 'FA':
            self.dat = self.dat_fa
            self.clim = self.clim_fa
        elif label == 'b0':
            self.dat = self.dat_b0
            self.clim = self.clim_b0
        elif label == 'DW':
            self.dat = self.dat_dw
            self.clim = self.clim_dw

        self.bg.set_data(self.dat[:,:,self.z].T)
        self.bg.set_clim(*self.clim)

        # this does not working. cannot update valmin/max. Instead, remove sliders and make new ones.
        #self.slider_vmin.valmax = self.dat.max()
        #self.slider_vmax.valmax = self.dat.max()
        #self.slider_vmin.set_val(self.clim[0])
        #self.slider_vmax.set_val(self.clim[1])
        self.slider_vmin.ax.clear()
        self.slider_vmax.ax.clear()
        del self.slider_vmin, self.slider_vmax
        self.slider_vmin = Slider(self.ax_vmin, 'vmin', 0, max(self.dat.max(), 1.0), valinit=self.clim[0])
        self.slider_vmax = Slider(self.ax_vmax, 'vmax', 0, max(self.dat.max(), 1.0), valinit=self.clim[1])
        self.cid_vmin = self.slider_vmin.on_changed(self.update_clim)
        self.cid_vmax = self.slider_vmax.on_changed(self.update_clim)

        self.canvas.draw()
        #self.canvas.blit(self.ax.bbox)
        #self.draw_update()

if __name__ == '__main__':
    fn_fa = None
    fn_b0 = None
    fn_dw = None
    if len(sys.argv) > 1:
        fn_fa = sys.argv[1]
    if len(sys.argv) > 2:
        fn_b0 = sys.argv[2]
    if len(sys.argv) > 3:
        fn_dw = sys.argv[3]

    #plt.ion() # for debug
    draw = Draw_ROI(fn_fa, fn_b0, fn_dw)
    plt.show()

