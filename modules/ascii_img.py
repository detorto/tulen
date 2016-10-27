#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os
from PIL import Image
import requests
from  StringIO import StringIO
import PIL.ImageOps  

def get_random_start_and_end_points_in_file(file_data):
    start_point = random.randint(2500, len(file_data))
    end_point = start_point + random.randint(0, len(file_data) - start_point)
 
    return start_point, end_point
 
def splice_a_chunk_in_a_file(file_data):
    start_point, end_point = get_random_start_and_end_points_in_file(file_data)
    section = file_data[start_point:end_point]
    repeated = ''
 
    for i in range(1, random.randint(1,5)):
        repeated += section
 
    new_start_point, new_end_point = get_random_start_and_end_points_in_file(file_data)
    file_data = file_data[:new_start_point] + repeated + file_data[new_end_point:]
    return file_data
   
def glitch_an_image(local_image):
    file_handler = open(local_image, 'r')
    file_data = file_handler.read()
    file_handler.close()
 
    for i in range(1, random.randint(1,5)):
        file_data = splice_a_chunk_in_a_file(file_data)
 
    file_handler = open(local_image, 'w')
    file_handler.write(file_data)
    file_handler.close
 
    return local_image
 
def negate_image( img):
    return PIL.ImageOps.invert(img)        
def poster_image(img):
    return PIL.ImageOps.posterize(img, random.randint(1,8))
def solar_image(img):
    return PIL.ImageOps.solarize(img, threshold=random.randint(0,255))

class Processor:

    def __init__(self,vkuser):
        self.user = vkuser

  
    def process_message(self, message, chatid, userid):
        
        message_body = message["body"].lower()
        try:
            photo_url = message["attachments"][0]["photo"]["photo_604"]
            r = requests.get(photo_url)
            i = Image.open(StringIO(r.content))
        except:
            return
    
        if message_body == u"негатни":
            negate_image(i).save("./files/neg.jpg")
            a = u"Негатнул"
        elif message_body == u"постерни":
                poster_image(i).save("./files/neg.jpg")
                a = u"Постернул"
        elif message_body == u"соларни":
                solar_image(i).save("./files/neg.jpg")
                a = u"Соларнул"
        elif message_body == u"фильтрани":
                random.choice(curve_filts())(i).save("./files/neg.jpg")
                a = u"Фильранул"
        elif message_body == u"рандомни":
                randomnize(i).save("./files/neg.jpg")
                a = u"Рандомнул"
        elif message_body == u"гличани":
                i.save("./files/neg.jpg")
		glitch_an_image("./files/neg.jpg")
                a = u"Гличанул"
        else:
            return

        msg_attachments = self.user.upload_images_files(["./files/neg.jpg",])

        if not msg_attachments:
            return

        self.user.send_message(text=a, attachments = msg_attachments, chatid = chatid, userid=userid)

        wall_attachments = self.user.upload_images_files_wall(["./files/neg.jpg",])
        if not wall_attachments:
            print "Error in wall attachments"
            return
        self.user.post(a, attachments = wall_attachments, chatid = chatid, userid=userid)


"""
The extraction of the curves from the acv files are from here:
  
  https://github.com/vbalnt/filterizer
"""

from struct import unpack
from scipy import interpolate

from PIL import Image
import numpy
import scipy

import sys
import glob
class Filter:

  def __init__(self, acv_file_path, name):
    self.name = name
    with open(acv_file_path, 'rb') as acv_file:
      self.curves = self._read_curves(acv_file)
    self.polynomials = self._find_coefficients()
  
  def _read_curves(self, acv_file):
    _, nr_curves = unpack('!hh', acv_file.read(4))
    curves = []
    for i in xrange(0, nr_curves):
      curve = []
      num_curve_points, = unpack('!h', acv_file.read(2))
      for j in xrange(0, num_curve_points):
        y, x = unpack('!hh', acv_file.read(4))
        curve.append((x,y))
      curves.append(curve)

    return curves

  def _find_coefficients(self):
    polynomials = []
    for curve in self.curves:
      xdata = [x[0] for x in curve]
      ydata = [x[1] for x in curve]
      p = interpolate.lagrange(xdata, ydata)
      polynomials.append(p)
    return polynomials

  def get_r(self):
    return self.polynomials[1]

  def get_g(self):
    return self.polynomials[2]

  def get_b(self):
    return self.polynomials[3]

  def get_c(self):
    return self.polynomials[0]

class FilterManager:

  def __init__(self):
    self.filters = {}
    #add some stuff here

  def add_filter(self,filter_obj):
    # Overwrites if such a filter already exists
    # NOTE: Fix or not to fix?
    self.filters[filter_obj.name] = filter_obj

  def apply_filter(self,filter_name,image_array):

    if image_array.ndim < 3:
      raise Exception('Photos must be in color, meaning at least 3 channels')
    else:
      def interpolate(i_arr, f_arr, p, p_c):
        p_arr = p_c(f_arr)
        return p_arr 

      # NOTE: Assumes that image_array is a numpy array
      image_filter = self.filters[filter_name]
      # NOTE: What happens if filter does not exist?
      width,height,channels = image_array.shape
      filter_array = numpy.zeros((width, height, 3), dtype=float) 

      p_r = image_filter.get_r()
      p_g = image_filter.get_g()
      p_b = image_filter.get_b()
      p_c = image_filter.get_c()

      filter_array[:,:,0] = p_r(image_array[:,:,0])
      filter_array[:,:,1] = p_g(image_array[:,:,1])
      filter_array[:,:,2] = p_b(image_array[:,:,2])
      filter_array = filter_array.clip(0,255)
      filter_array = p_c(filter_array)

      filter_array = numpy.ceil(filter_array).clip(0,255)

      return filter_array.astype(numpy.uint8)
def cvf(f):
    img_filter = Filter(f, 'crgb')
    filter_manager = FilterManager()
    filter_manager.add_filter(img_filter)
    def apply_(img):

        image_array = numpy.array(img)

        filter_array = filter_manager.apply_filter('crgb', image_array)
        return Image.fromarray(filter_array)
    return apply_
        

def curve_filts():
    return  [cvf(f) for f in glob.glob("./modules/curves/*.acv")]

def randomnize(img):
    filts = [solar_image, poster_image, negate_image] + curve_filts();

    for i in xrange(random.randint(3, len(filts))):
        img = random.choice(filts)(img)
    return img
if __name__ == '__main__':

  if len(sys.argv) < 3:
    print "Wrong number of arguments"
    print """  Usage: \
          python filter.py [curvefile] [imagefile] """
  else:


    im = Image.open(sys.argv[2])

    im.show()

    randomnize(im).show()

