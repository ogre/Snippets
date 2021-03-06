#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************
#
# Copyright (C) 2009 - 2014 - Thomas Mansencal - thomas.mansencal@gmail.com
#
#**********************************************************************************************************************

"""
**loader.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Loader Module.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import inspect
import itertools
import mari
import os
import re
from PythonQt.QtCore import *
from PythonQt.QtGui import *

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2010 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["unpackDefault",
	"fillPaintBuffer",
	"projectColor",
	"projectBlack",
	"projectWhite",
	"getSelectedPatches",
	"displaySelectedPatches",
	"getPatchesFromSequence",
	"selectPatches",
	"selectInputPatches",
	"playblastTimeRange",
	"writeUVsMasks",
	"exportUVsMasks"]

def unpackDefault(data, length=3, default=None):
	"""
	Unpack given iterable data with default if needed.
	
	:param data: Iterable.
	:type data: str or tuple or list
	:param length: Default length.
	:type length: int
	:param default: Default value.
	:type default: object
	:return: Definition success.
	:rtype: bool
	"""

	return itertools.islice(itertools.chain(iter(data), itertools.repeat(default)), length)

def fillPaintBuffer(color):
	"""
	Fills the paint buffer with given color.
	
	:param color: Color.
	:type color: QColor
	:return: Definition success.
	:rtype: bool
	"""

	paintBuffer = mari.canvases.paintBuffer()
	image = paintBuffer.getPaint()
	image.fill(color.rgba())
	paintBuffer.setPaint(image)
	return True

def projectColor(color):
	"""
	Projects the given color.
	
	:param color: Color.
	:type color: QColor
	:return: Definition success.
	:rtype: bool
	"""

	if fillPaintBuffer(color):
		mari.canvases.paintBuffer().bakeAndClear()
		return True

def projectBlack():
	"""
	Projects black color.

	:return: Definition success.
	:rtype: bool
	"""

	return projectColor(QColor(0, 0, 0,255))

def projectWhite():
	"""
	Projects white color.

	:return: Definition success.
	:rtype: bool
	"""

	return projectColor(QColor(255, 255, 255,255))

def getSelectedPatches():
	"""
	Returns current selected patches.

	:return: Selected patches.
	:rtype: list
	"""

	patches = []
	for patch in mari.geo.current().patches():
    		if patch.isSelected():
			patches.append(patch.name())
	return sorted(patches)

def displaySelectedPatches():
	"""
	Displays current selected patches.

	:return: Definition success.
	:rtype: bool
	"""
	
	patches = getSelectedPatches()
	print "%s | Current object: '%s'" % (inspect.getmodulename(__file__), mari.geo.current().name())
	print "%s | Selected patches: '%s'" % (inspect.getmodulename(__file__), patches)
	mari.utils.misc.message("Current object: '%s'\nSelected patches: '%s'" % (mari.geo.current().name(), ", ".join(patches)), title="Current Object Selected Patches")
	return True

def getPatchesFromSequence(sequence):
	"""
	Returns patches from the given sequence.

	:param sequence: sequence.
	:type sequence: str
	:return: Patches.
	:rtype: list
	"""
	
	patches = []
	for pattern in sequence.split(","):
		start, end, step = (item.strip() for item in unpackDefault(re.split(r"-|%", pattern), default=""))
		if start and not end:
			patches.append(int(start))
		elif start and end and not step:
			patches.extend(range(int(start), int(end) + 1))
		elif start and end and step:
			patches.extend(range(int(start), int(end) + 1, int(step)))
	return patches

def selectPatches(patches):
	"""
	Selects given patches.

	:param patches: patches.
	:type patches: list
	:return: Definition success.
	:rtype: bool
	"""
	
	patches	= [str(patch) for patch in patches]
	for patch in mari.geo.current().patches():
		patch.setSelected(patch.name() in patches)
			
	return True

def selectInputPatches():
	"""
	Selects input patches.

	:return: Definition success.
	:rtype: bool
	"""

	sequence = QInputDialog.getText(None, "Select Patches", "Patches Sequences:")
	if sequence:
        	return selectPatches(getPatchesFromSequence(sequence))

def playblastTimeRange():
	"""
	Playblasts current time range.

	:return: Definition success.
	:rtype: bool
	"""

	mari.actions.find('/Mari/Canvas/Screenshot settings').trigger()
	
	currentFrame = mari.clock.frame()
	startFrame = mari.clock.startFrame()
	endFrame = mari.clock.stopFrame()

	mari.clock.setFrame(startFrame)
	#mari.app.startProcessing("Playblasting ...", endFrame - startFrame)
	mari.app.processEvents()
	for i in range(startFrame, endFrame):
		mari.actions.find('/Mari/Canvas/Take Screenshot').trigger()
		mari.clock.stepForward()
		mari.app.processEvents()
		#mari.app.stepProgress()
	#mari.app.stopProcessing()
	mari.clock.setFrame(currentFrame)

	return True

def writeUVsMasks(directory):
	"""
	Writes UVs masks to given output directory.

	:return: Definition success.
	:rtype: bool
	"""

	if not directory:
		return

	images = mari.images.list()
	patches = mari.geo.current().patches()
	
	# mari.app.startProcessing("Exporting UVs Masks", len(patches))
	for patch in patches:
		patch.setSelected(True)
		mari.actions.find('/Mari/Geometry/Patches/UV Mask to Image Manager').trigger()
		patch.setSelected(False)
		currentImage = tuple(set(mari.images.list()).difference(images))[0]
		currentImage.saveAs(os.path.join(directory, "%s_%s.tif" % (mari.projects.current().name(), patch.name())))
		currentImage.close()
		# mari.app.stepProgress()
	# mari.app.stopProcessing()
	return True

def exportUVsMasks():
	"""
	Exports UVs masks.

	:return: Definition success.
	:rtype: bool
	"""
	
	return writeUVsMasks(QFileDialog.getExistingDirectory(None, "Select Output Directory",))


mari.menus.addAction(mari.actions.create("Show Selected Patches ...", "import common;reload(common);common.displaySelectedPatches()"), "MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Select Input Patches ...", "import common;reload(common);common.selectInputPatches()"), "MainWindow/&MPC/")
mari.menus.addSeparator("MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Export UVs Masks ...", "import common;reload(common);common.exportUVsMasks()"), "MainWindow/&MPC/")
mari.menus.addSeparator("MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Playblast Time Range ...", "import common;reload(common);common.playblastTimeRange()"), "MainWindow/&MPC/")
mari.menus.addSeparator("MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Project Black", "import common;reload(common);common.projectBlack()"), "MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Project White", "import common;reload(common);common.projectWhite()"), "MainWindow/&MPC/")
mari.menus.addSeparator("MainWindow/&MPC/")
mari.menus.addAction(mari.actions.create("Clear History Queue ...", "mari.history.clear()"), "MainWindow/&MPC/")
