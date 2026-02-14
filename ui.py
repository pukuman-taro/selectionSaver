# -*- coding: utf-8 -*-
from importlib import reload
import json
import os
from pathlib import Path
import re

from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui
import maya.api.OpenMaya as om2
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin

ver = cmds.about(v=True)

if int(ver) >= 2025:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from PySide6 import __version__
    from shiboken6 import wrapInstance

else:
    try:
        from PySide2.QtCore import *
        from PySide2.QtGui import *
        from PySide2.QtWidgets import *
        from PySide2 import __version__
        from shiboken2 import wrapInstance

    except Exception as e:
        from PySide.QtCore import *
        from PySide.QtGui import *
        from PySide import __version__
        from shiboken import wrapInstance

try:
    DIR_PATH = '/'.join(__file__.replace('\\', '/').split('/')[0:-1])
except:
    DIR_PATH = ''

class UI(MayaQWidgetDockableMixin, QMainWindow):
    """
    Usage:
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ウィンドウタイトルの設定
        self.setWindowTitle('Selection Saver')

        # ウィジェットの設定
        self.widgets()

        # show
        self.buildUI()

        # フォーカスを取得と前面配置
        self.activateWindow()
        self.raise_()

        # 保持しているボタンの情報
        self.buttonStore = []

    def buildUI(self):
        self.show(dockable=True)

    def widgets(self):
        # スクロールエリアの設定
        self.topScrollArea = QScrollArea()
        self.topScrollArea.setWidgetResizable(True)

        self.topWidget = QWidget()
        self.topScrollArea.setWidget(self.topWidget)

        self.setCentralWidget(self.topScrollArea)

        # set layout
        self.topVboxLayout = QVBoxLayout()
        self.topWidget.setLayout(self.topVboxLayout)
        self.topVboxLayout.setAlignment(Qt.AlignTop)

        # main layout
        self.mainVLay = QVBoxLayout()
        self.topVboxLayout.addLayout(self.mainVLay)

        # -------------------------
        # Options
        # -------------------------
        self.showToolTipCheckBox = QCheckBox('Show Tool Tip')
        self.mainVLay.addWidget(self.showToolTipCheckBox)
        self.showToolTipCheckBox.setToolTip('オンにしてからボタンの上にマウスカーソルを置くとGIFが再生されます')
        self.showToolTipCheckBox.setVisible(False)

        # Separator -----------------------------------
        horizontal_separator = Separator(Qt.Horizontal)
        self.mainVLay.addWidget(horizontal_separator)

        # save button
        self.saveSelectionBtn = ToolTipButton('Save Selection')
        self.saveSelectionBtn.set_gif_path('{}/data/selectionSaver_00.gif'.format(DIR_PATH))
        self.saveSelectionBtn.set_showToolTipCheckbox(self.showToolTipCheckBox)
        self.mainVLay.addWidget(self.saveSelectionBtn)
        self.saveSelectionBtn.clicked.connect(lambda: self.add_button())

        # order
        self.saveSelectionOrderBtn = ToolTipButton('Save Selection Order')
        self.saveSelectionOrderBtn.set_gif_path('{}/data/selectionSaver_00.gif'.format(DIR_PATH))
        self.saveSelectionOrderBtn.set_showToolTipCheckbox(self.showToolTipCheckBox)
        self.mainVLay.addWidget(self.saveSelectionOrderBtn)
        self.saveSelectionOrderBtn.clicked.connect(lambda: self.add_button_order())

        # save button from sets
        self.saveSelectionFromSetsBtn = ToolTipButton('Save Selection from sets')
        self.saveSelectionFromSetsBtn.set_gif_path('{}/data/selectionSaver_01.gif'.format(DIR_PATH))
        self.saveSelectionFromSetsBtn.set_showToolTipCheckbox(self.showToolTipCheckBox)
        self.mainVLay.addWidget(self.saveSelectionFromSetsBtn)
        self.saveSelectionFromSetsBtn.clicked.connect(lambda: self.add_button(True))

        # Separator -----------------------------------
        horizontal_separator = Separator(Qt.Horizontal)
        self.mainVLay.addWidget(horizontal_separator)

        # export
        self.exportAllSaveSelectionBtn = QPushButton('Export All')
        self.mainVLay.addWidget(self.exportAllSaveSelectionBtn)
        self.exportAllSaveSelectionBtn.clicked.connect(lambda: self.export_all_save_selection_btn())

        # import
        self.importAllSaveSelectionBtn = QPushButton('Import All')
        self.mainVLay.addWidget(self.importAllSaveSelectionBtn)
        self.importAllSaveSelectionBtn.clicked.connect(lambda: self.import_save_selection_btns())

        # checkbox
        self.checkBoxLay = QHBoxLayout()
        self.mainVLay.addLayout(self.checkBoxLay)
        self.addSelectionCheckBox = QCheckBox('Add Selection')
        self.checkBoxLay.addWidget(self.addSelectionCheckBox)

        # replace selection
        self.replSelLay = QHBoxLayout()
        self.mainVLay.addLayout(self.replSelLay)
        self.replSelLE = QLineEdit()
        self.replSelLE.setPlaceholderText('Enter Replace Mesh here...')
        self.replSelLay.addWidget(self.replSelLE)

        # Separator -----------------------------------
        horizontal_separator = Separator(Qt.Horizontal)
        self.mainVLay.addWidget(horizontal_separator)

    def add_button(self, from_sets=None):
        sel = cmds.ls(os=True)
        if not sel:
            return
        mainHLay = QHBoxLayout()
        mainHLay.setAlignment(Qt.AlignLeft)
        self.mainVLay.addLayout(mainHLay)
        visCheckBox = QCheckBox()
        mainHLay.addWidget(visCheckBox)
        if not '.' in sel[0]:
            if cmds.objExists(f'{sel[0]}.v'):
                sel_v = cmds.getAttr(f'{sel[0]}.v')
                if sel_v:
                    visCheckBox.setChecked(True)
        addSelectionBtn = SaveButton()
        mainHLay.addWidget(addSelectionBtn)
        addSelectionBtn.index = len(self.buttonStore)
        addSelectionBtn.repl_name_obj = self.replSelLE
        addSelectionBtn.vis_checkbox = visCheckBox
        addSelectionBtn.add_button(from_sets)
        addSelectionBtn.clicked.connect(lambda: addSelectionBtn.select(self.addSelectionCheckBox.isChecked()))
        visCheckBox.clicked.connect(lambda: addSelectionBtn.set_vis())
        self.buttonStore.append(addSelectionBtn)

    def add_button_order(self):
        sel = cmds.ls(os=True, fl=True)
        for obj in sel:
            cmds.select(obj, r=True)
            self.add_button()
        cmds.select(sel, r=True)

    def export_all_save_selection_btn(self):
        [btn.export_save_selection() for btn in self.buttonStore]

    def import_add_button(self, name, selection):
        mainHLay = QHBoxLayout()
        mainHLay.setAlignment(Qt.AlignLeft)
        self.mainVLay.addLayout(mainHLay)
        visCheckBox = QCheckBox()
        mainHLay.addWidget(visCheckBox)
        addSelectionBtn = SaveButton()
        mainHLay.addWidget(addSelectionBtn)
        addSelectionBtn.index = len(self.buttonStore)
        addSelectionBtn.repl_name_obj = self.replSelLE
        addSelectionBtn.vis_checkbox = visCheckBox
        addSelectionBtn.set_values(name, selection)
        addSelectionBtn.clicked.connect(lambda: addSelectionBtn.select(self.addSelectionCheckBox.isChecked()))
        visCheckBox.clicked.connect(lambda: addSelectionBtn.set_vis())
        self.buttonStore.append(addSelectionBtn)

    def import_save_selection_btns(self):
        open_files = show_file_dialog('open')
        for file in open_files:
            data = load_dict_from_json(file)
            for name, selection in data.items():
                self.import_add_button(name, selection)

class Separator(QFrame):
    def __init__(self, orientation=Qt.Horizontal, shadow=QFrame.Sunken, parent=None):
        super(Separator, self).__init__(parent)

        # セパレータの方向を設定
        if orientation == Qt.Horizontal:
            self.setFrameShape(QFrame.HLine)
        else:
            self.setFrameShape(QFrame.VLine)

        # セパレータの影スタイルを設定
        self.setFrameShadow(shadow)

class SaveButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.selection = []
        
        self.add_contextMenu()
        self.index = 0

        self.repl_name_obj = None

        self.vis_checkbox = None

        self.inf_list_object = None

    def add_button(self, from_sets=None):
        sel = cmds.ls(os=True, fl=True)
        if from_sets:
            if not sel:
                return
            if cmds.objectType(sel[0]) == 'objectSet':
                selection_ = cmds.sets(sel[0], q=True) or []
            else:
                selection_ = cmds.ls(sel, fl=True)
            self.selection = cmds.ls(selection_, fl=True)
            self.setText(f'{sel[0]}')
            self.setToolTip(f'{self.selection}')
        else:
            self.update_selection()
            # self.setText(f'{self.index:003}')
            label_text = "".join(self.selection)
            self.setText(f'{label_text[0:100]}')

    def get_selection(self):
        selection = [s for s in self.selection]
        repl_text = self.repl_name_obj.text()
        if repl_text != '':
            selection = [s.replace(s.split('.')[0], repl_text) for i, s in enumerate(selection)]
        return selection

    def select(self, add=None):
        selection = self.get_selection()

        if cmds.currentCtx() == 'artAttrSkinContext':
            self.inf_list_object, _ = get_infs_from_theSkinClusterInflList()
            self.select_infs_in_skinlist(selection)
        else:
            if add:
                cmds.select(selection, add=True)
            else:
                cmds.select(selection, r=True)

    def select_infs_in_skinlist(self, infs):
        cmds.treeView(self.inf_list_object, e=True, cs=True)
        for inf in infs:
            cmds.treeView(self.inf_list_object, e=True, si=(inf, True))

    def set_vis(self):
        selection = self.get_selection()
        if self.vis_checkbox.isChecked():
            [cmds.setAttr(f'{n}.v', 1) for n in selection if cmds.objExists(f'{n}.v')]
        else:
            [cmds.setAttr(f'{n}.v', 0) for n in selection if cmds.objExists(f'{n}.v')]

    def add_contextMenu(self):
        # コンテキストメニューを設定
        self.menu = QMenu(self)
        self.menu.addAction('Edit Label', self.editLabel)
        # self.menu.addAction('Create Sets', self.create_sets)
        self.menu.addAction('Update Selection', self.update_selection)
        self.menu.addAction('Export Save Selection', self.export_save_selection)
        self.menu.addAction('Invert Selection', self.invert_selection)

    def editLabel(self):
        newText, ok = QInputDialog.getText(self, 'Edit Label', 'Enter new label:', QLineEdit.Normal, self.text())
        if ok and newText:
            newText = re.sub(r'[^a-zA-Z0-9]', '_', newText)
            self.setText(newText)

    def create_sets(self):
        setsName = f'{self.text()}_sets'
        if not cmds.objExists(setsName):
            cmds.sets(em=True, n=setsName)
        for sel in self.selection:
            cmds.sets(sel, add=setsName)

    def search_selection(self):
        if cmds.currentCtx() == 'artAttrSkinContext':
            self.inf_list_object, self.selection = get_infs_from_theSkinClusterInflList()
        else:
            self.selection = cmds.ls(os=True, fl=True)

    def update_selection(self):
        self.search_selection()
        self.setToolTip(f'{self.selection}')

    def export_save_selection(self):
        export_data = {}
        export_data[self.text()] = self.selection
        save_dir = f'{DIR_PATH}/data/{Path(os.path.basename(__file__)).stem}'
        ensure_folder_exists(save_dir)
        file_path = f'{save_dir}/{self.text()}.json'
        save_dict_to_json(export_data, file_path)

    def invert_selection(self):
        sel = cmds.ls(os=True, tr=True)
        all_trs_nodes = cmds.ls(tr=True)
        invert_sel = [n for n in all_trs_nodes if not n in sel]

        shape_including = []
        for n in invert_sel:
            shapes = cmds.listRelatives(n, s=True) or []
            if shapes:
                shape_including.append(n)

        cmds.select(shape_including, r=True)

    def set_values(self, text, selection):
        self.setText(text)
        self.selection = selection
        self.setToolTip(f'{self.selection}')

    def contextMenuEvent(self, event):
        # 右クリック時にメニューを表示
        self.menu.exec_(event.globalPos())

def get_infs_from_theSkinClusterInflList():
    ui_name = 'theSkinClusterInflList'
    inf_list_object = cmds.control(ui_name, q=True, fpn=True)
    infs = cmds.treeView(inf_list_object, query=True, si=True)
    return inf_list_object, infs

class GifView(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trashGif = None
        self.file_path = None

    def read_file(self):
        self.movie = QMovie(self.file_path)
        self.setMovie(self.movie)

    def show_tooltip(self, pos):
        """ツールチップを表示"""
        self.move(pos)
        self.movie.jumpToFrame(0)
        self.show()

        original_size = self.frameRect().size()
        # 縦横比を維持して新しいサイズを計算 (幅を基準にリサイズ)
        new_width = 700  # 新しい幅
        aspect_ratio = original_size.height() / original_size.width()  # 縦横比
        new_height = int(new_width * aspect_ratio)

        # 新しいサイズを設定
        self.movie.setScaledSize(QSize(new_width, new_height))

        self.movie.start()

class ToolTipButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.showToolTipCheckbox = None

    def set_gif_path(self, file_path=None):
        self.gifView = GifView()
        self.gifView.file_path = file_path
        self.gifView.read_file()

    def set_showToolTipCheckbox(self, checkbox=None):
        self.showToolTipCheckbox = checkbox

    def enterEvent(self, event):
        """マウスがボタン上に入ったときにツールチップを表示"""
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        if self.showToolTipCheckbox.isChecked():
            self.gifView.show_tooltip(global_pos)

    def leaveEvent(self, event):
        """マウスがボタン上から出たときにツールチップを非表示"""
        self.gifView.hide()

if __name__ == '__main__':
    ui = UI()

def save_optionvar(key, value, force=True):
    """optionVarに保存

    :param str key: キー名
    :param mixin value: 値
    :param bool force: 強制的に上書きするかのブール値

    :return: 保存できたかどうかのブール値
    :rtype: bool
    """

    vStr = str(value)
    if force:
        cmds.optionVar(sv=[key, vStr])
        return True
    else:
        if not cmds.optionVar(ex=key):
            cmds.optionVar(sv=[key, vStr])
            return True
        else:
            return False


def load_optionvar(key):
    """optionVarを取得

    :param str key: キー名
    :return: 保存された値, キーが見つからない場合は None
    :rtype: value or None
    """

    if cmds.optionVar(ex=key):
        return eval(cmds.optionVar(q=key))
    else:
        return None


def remove_optionvar(key):
    """optionVarを削除

    :param str key: キー名
    :return: 削除成功したかのブール値
    :rtype: bool
    """

    if cmds.optionVar(ex=key):
        cmds.optionVar(rm=key)
        return True
    else:
        return False

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def save_dict_to_json(data, file_path):
    """
    辞書型オブジェクトをJSONファイルにエクスポートする。

    :param data: dict - 保存する辞書データ
    :param file_path: str - 出力するJSONファイルのパス
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"JSONファイルに保存しました: {file_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def load_dict_from_json(file_path):
    """
    JSONファイルを読み込み、辞書型オブジェクトに変換する。

    :param file_path: str - 読み込むJSONファイルのパス
    :return: dict - 読み込んだ辞書データ
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print("JSONファイルを読み込みました。")
        return data
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def show_file_dialog(mode=None, ext='.json'):
    '''
    モードに応じて異なるダイアログを表示する
    :param mode: 'open' (ファイルを開く), 'save' (ファイルを保存), 'directory' (ディレクトリを選択)
    '''
    if mode == 'open':
        file_path, _ = QFileDialog.getOpenFileNames(
            None, 'ファイルを開く', '', f'テキストファイル (*{ext});;すべてのファイル (*.*)'
        )
        return file_path

    elif mode == 'save':
        file_path, _ = QFileDialog.getSaveFileName(
            None, 'ファイルを保存', '', f'テキストファイル (*{ext});;すべてのファイル (*.*)'
        )
        return file_path

    elif mode == 'directory':
        directory = QFileDialog.getExistingDirectory(None, 'ディレクトリを選択', '')
        return directory
