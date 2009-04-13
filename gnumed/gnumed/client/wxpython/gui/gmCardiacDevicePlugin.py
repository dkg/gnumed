"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on proper mime type handling at the OS level.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmCardiacDevicePlugin.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, logging


import wx


from Gnumed.wxpython import gmMeasurementWidgets, gmPlugin

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()



_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class gmCardiacDevicePlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate document tree."""

	tab_name = _("Cardiac Devices")

	def name (self):
		return gmCardiacDevicePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmMeasurementWidgets.cCardiacDevicePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('tools', _('Show &cardiac devices'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		if kwds['sort_mode'] == 'review':
			self._widget._on_sort_by_review_selected(None)
		return True
	#--------------------------------------------------------
#	def populate_toolbar (self, tb, widget):
#		wxID_TB_BTN_show_page = wx.NewId()
#		tool1 = tb.AddTool(
#			wxID_TB_BTN_show_page,
#			images_Archive_plugin.getreportsBitmap(),
#			shortHelpString=_("show document"),
#			isToggle=False
#		)
#		wx.EVT_TOOL(tb, wxID_TB_BTN_show_page, self._widget._doc_tree.display_selected_part)
#		tb.AddControl(wx.StaticBitmap(
#			tb,
#			-1,
#			images_Archive_plugin.getvertical_separator_thinBitmap(),
#			wx.DefaultPosition,
#			wx.DefaultSize
#		))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	# 3rd party
	import wx

	# GNUmed
	from Gnumed.business import gmPerson
	from Gnumed.wxpython import gmSOAPWidgets
	
	_log.info("starting Notebooked cardiac device input plugin...")

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "None patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		# display standalone multisash progress notes input
		application = wx.wx.PyWidgetTester(size = (800,600))
		multisash_notes = gmMeasurementWidgets.cCardiacDeviceMeasurementsPnl(application.frame, -1)

		application.frame.Show(True)
		application.MainLoop()

		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.exception("unhandled exception caught !")
		# but re-raise them
		raise

	_log.info("closing Notebooked cardiac device input plugin...")
#================================================================
# $Log: gmCardiacDevicePlugin.py,v $
# Revision 1.3  2009-04-13 15:34:55  shilbert
# - renamed class cCardiacDeviceMeasurmentPnl to cCardiacDevicePluginPnl
#
# Revision 1.2  2009/04/12 20:22:12  shilbert
# - make it run in pywidgettester
#
# Revision 1.1  2009/04/09 11:37:37  shilbert
# - first iteration of cardiac device management plugin
#
# Revision 1.75  2008/07/10 08:37:44  ncq
# - no more toolbar
#
# Revision 1.74  2008/01/28 16:14:34  ncq
# - missing import
#
# Revision 1.73  2007/12/26 18:35:57  ncq
# - cleanup++, no more standalone
#
# Revision 1.72  2007/12/23 21:19:17  ncq
# - cleanup
#
# Revision 1.71  2007/06/10 10:16:05  ncq
# - properly display doc from toolbar tool
#
# Revision 1.70  2007/03/08 11:54:44  ncq
# - cleanup
#
# Revision 1.69  2006/11/07 00:35:28  ncq
# - cleanup
#
# Revision 1.68  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.67  2006/05/28 16:17:58  ncq
# - cleanup
# - populate now handled by plugin base class already
#
# Revision 1.66  2006/05/20 18:56:03  ncq
# - use receive_focus() interface
#
# Revision 1.65  2006/05/12 22:02:25  ncq
# - override _on_raise_by_signal()
#
# Revision 1.64  2006/05/07 15:39:18  ncq
# - move plugin tree panel to wxpython/gmMedDocWidgets.py where it belongs
#
# Revision 1.63  2005/10/30 22:09:03  shilbert
# - more wx2.6-ification
#
# Revision 1.62  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.61  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.60  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.59  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.58  2004/10/17 15:53:55  ncq
# - cleanup
#
# Revision 1.57  2004/10/17 00:05:36  sjtan
#
# fixup for paint event re-entry when notification dialog occurs over medDocTree graphics
# area, and triggers another paint event, and another notification dialog , in a loop.
# Fixup is set flag to stop _repopulate_tree, and to only unset this flag when
# patient activating signal gmMedShowDocs to schedule_reget, which is overridden
# to include resetting of flag, before calling mixin schedule_reget.
#
# Revision 1.56  2004/10/14 12:15:21  ncq
# - cleanup
#
# Revision 1.55  2004/09/19 15:12:26  ncq
# - cleanup
#
# Revision 1.54  2004/09/13 21:12:36  ncq
# - convert to use cRegetMixin so it plays really nice with xdt connector
#
# Revision 1.53  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.52  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.51  2004/07/15 20:42:18  ncq
# - support if-needed updates again
#
# Revision 1.50  2004/07/15 07:57:21  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.49  2004/06/29 22:58:43  ncq
# - add missing gmMedDocWidgets. qualifiers
#
# Revision 1.48  2004/06/26 23:39:34  ncq
# - factored out widgets for re-use
#
# Revision 1.47	 2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.46	 2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.45	 2004/06/17 11:43:18  ihaywood
# Some minor bugfixes.
# My first experiments with wxGlade
# changed gmPhraseWheel so the match provider can be added after instantiation
# (as wxGlade can't do this itself)
#
# Revision 1.44	 2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.43	 2004/06/01 07:55:46  ncq
# - use cDocumentFolder
#
# Revision 1.42	 2004/04/16 00:36:23  ncq
# - cleanup, constraints
#
# Revision 1.41	 2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.40	 2004/03/20 19:48:07  ncq
# - adapt to flat id list from get_patient_ids
#
# Revision 1.39	 2004/03/20 18:30:54  shilbert
# - runs standalone again
#
# Revision 1.38	 2004/03/19 21:26:15  shilbert
# - more module import fixes
#
# Revision 1.37	 2004/03/19 08:29:21  ncq
# - fix spurious whitespace
#
# Revision 1.36	 2004/03/19 08:08:41  ncq
# - fix import of gmLoginInfo
# - remove dead code
#
# Revision 1.35	 2004/03/07 22:19:26  ncq
# - proper import
# - re-fix gmTmpPatient -> gmPatient (fallout from "Syan's commit")
#
# Revision 1.34	 2004/03/06 21:52:02  shilbert
# - adapted code to new API since __set/getitem is gone
#
# Revision 1.33	 2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.32	 2004/01/06 23:19:52  ncq
# - use whoami
#
# Revision 1.31	 2003/11/17 10:56:40  sjtan
#
# synced and commiting.
#
# Revision 1.30	 2003/11/16 11:53:32  shilbert
# - fixed stanalone mode
# - makes use of toolbar
#
# Revision 1.29	 2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.28	 2003/08/27 12:31:41  ncq
# - some cleanup
#
# Revision 1.27	 2003/08/24 12:50:20  shilbert
# - converted from __show_error() to gmGUIHelpers.gm_show_error()
#
# Revision 1.26	 2003/06/29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.25	 2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.24	 2003/06/19 15:31:37  ncq
# - cleanup, page change vetoing
#
# Revision 1.23	 2003/04/28 12:11:30  ncq
# - refactor name() to not directly return _(<name>)
#
# Revision 1.22	 2003/04/20 15:39:36  ncq
# - call_viewer was moved to gmMimeLib
#
# Revision 1.21	 2003/04/19 15:01:33  ncq
# - we need import re both standalone and plugin
#
# Revision 1.20	 2003/04/18 22:34:44  ncq
# - document context menu, mainly for descriptions, currently
#
# Revision 1.19	 2003/04/18 17:45:05  ncq
# - add quit button
#
# Revision 1.18	 2003/04/18 16:40:04  ncq
# - works again as standalone
#
# Revision 1.17	 2003/04/04 20:49:22  ncq
# - make plugin work with gmCurrentPatient
#
# Revision 1.16	 2003/04/01 12:31:53  ncq
# - we can't use constant reference self.patient if we don't register interest
#	in gmSignals.patient_changed, hence, acquire patient when needed
#
# Revision 1.15	 2003/03/25 19:57:09  ncq
# - add helper __show_error()
#
# Revision 1.14	 2003/03/23 02:38:46  ncq
# - updated Hilmar's fix
#
# Revision 1.13	 2003/03/02 17:03:19  ncq
# - make sure metadata is retrieved
#
# Revision 1.12	 2003/03/02 11:13:01  hinnef
# preliminary fix for crash on ReceiveFocus()
#
# Revision 1.11	 2003/02/25 23:30:31  ncq
# - need sys.exc_info() in LogException
#
# Revision 1.10	 2003/02/24 23:14:53  ncq
# - adapt to get_patient_ids actually returning a flat list of IDs now
#
# Revision 1.9	2003/02/21 13:54:17	 ncq
# - added even more likely and unlikely user warnings
#
# Revision 1.8	2003/02/20 01:25:18	 ncq
# - read login data from config file again
#
# Revision 1.7	2003/02/19 15:19:43	 ncq
# - remove extra print()
#
# Revision 1.6	2003/02/18 02:45:21	 ncq
# - almost fixed standalone mode again
#
# Revision 1.5	2003/02/17 16:10:50	 ncq
# - plugin mode seems to be fully working, actually calls viewers on files
#
# Revision 1.4	2003/02/15 14:21:49	 ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.3	2003/02/11 18:26:16	 ncq
# - fix exp_base buglet in OnActivate
#
# Revision 1.2	2003/02/09 23:41:09	 ncq
# - reget doc list on receiving focus thus being able to react to selection of a different patient
#
# Revision 1.1	2003/02/09 20:07:31	 ncq
# - works as a plugin, patient hardcoded, though
#
# Revision 1.8	2003/01/26 17:00:18	 ncq
# - support chunked object retrieval
#
# Revision 1.7	2003/01/25 00:21:42	 ncq
# - show nr of bytes on object in metadata :-)
#