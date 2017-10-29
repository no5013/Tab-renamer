# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TabRenamer
                                 A QGIS plugin
 This plugin rename column in tab file
                              -------------------
        begin                : 2017-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Karnthep T.
        email                : karnthep.t@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from tab_renamer_dialog import TabRenamerDialog
import os.path


class TabRenamer:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TabRenamer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Tab Renamer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TabRenamer')
        self.toolbar.setObjectName(u'TabRenamer')

        #path เริ่มต้น
        self.path = '/'

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TabRenamer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = TabRenamerDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        #เชื่อมปุ่มกับช่องคำสั่งเปิด File browser
        self.dlg.pushButton.clicked.connect(self.select_output_file)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TabRenamer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Rename Tab'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Tab Renamer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #คำสั่งเลือกไฟล์
    def select_output_file(self):
        #เปิดไฟล์ Browse
        #ช่องแรกช่างแม่ง ช่องสองชื่อTitle ช่องสามPathเริ่มต้น(ตอนแรกเป็น '/' สร้างไว้ข้างบน) ช่องสี่เลือกสกุลไฟล์
        #เลือกไฟล์เสร็จเก็บเข้าตัวแปล filenames
        filenames = QFileDialog.getOpenFileNames(self.dlg, "Select tab files  ",self.path, '*.tab')

        #เช็คว่ามีไฟล์รึเปล่า
        if(len(filenames) > 0):
            #save path ก่อนหน้า
            self.path = QFileInfo(filenames[0]).path();

            #format ชื่อไฟล์ใหม่โดยเอาชื่อไฟล์มาต่อกัน คั่นด้วย ;
            filenames_string = ""
            for filename in filenames:
                filenames_string += filename + ";"
            self.dlg.lineEdit.setText(filenames_string)

    #คำสั่งทำงานตอนเปิดปลั๊กอิน
    def run(self):
        """Run method that performs all the real work"""
        #import ชื่อไฟล์ที่จะเปลี่ยน
        import db_file_names
        #เคลียร์ช่อง path
        self.dlg.lineEdit.clear()
        # เคลียร์combobox
        self.dlg.comboBox.clear()
        # นำชื่อไฟล์ไปใส่ comboBox
        self.dlg.comboBox.addItems(db_file_names.file_name_lists)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # ทำงานเมื่อกด OK
        if result:
            # ไปดึงชื่อไฟล์มา
            filenames = self.dlg.lineEdit.text()

            # เช็คว่าชื่อไหนถูกเลือก
            selectedNameIndex = self.dlg.comboBox.currentIndex()
            new_name = db_file_names.file_name_lists[selectedNameIndex]

            #วน for แต่ละไฟล์ที่แยกด้วย semicolon
            for f in filenames.split(";"):
                #ตัดช่องว่างทิ้ง
                if(f == ""):
                    break;

                #เปิดไฟล์
                file = open(f, "r")
                #อ่านไฟล์เก็บใส่ตัวแปร txt
                txt = file.read()
                #แยกบรรทัดเก็บใส่ array
                lines = txt.splitlines()

                #ประกาศชื่อ Column ว่างเปล่าไว้
                name_of_column = None

                #วนหาชื่อ Column
                #index คือจำนวนบรรทัด
                index = 0
                for line in lines:
                    # หาบรรทัดที่มีคำว่า Fields 1
                    if("Fields 1" in line):
                        # เอาบรรทัดถัดไป
                        line_contain_name = lines[index+1]

                        #เอาชือมันมาจากคำแรกของบรรทัดมา
                        name_of_column = line_contain_name.split()[0]

                        #เขียนชื่อทับอันเก่า(ยังไม่ใช่เขียนใส่ไฟล์จริง)
                        txt = txt.replace(name_of_column, new_name)
                        break
                    index+=1
                #ปิดการอ่านไฟล์
                file.close()

                if(name_of_column != None):
                    #เปิดไฟล์
                    file = open(f, "w")
                    #ลบไฟล์เก่าทิ้ง
                    file.truncate()
                    #เขียนทับ
                    file.write(txt)
                    #ปิดการเขียนไฟล์
                    file.close()
