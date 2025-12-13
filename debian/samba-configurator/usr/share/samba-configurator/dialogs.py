import gi
gi.require_version('Gtk', '4.0')
from gi.repository import (
    Gtk,
    GObject
)
from i18n import _
import os, sys
from shared_elements  import SharedFolder

class AddFolderDialog(Gtk.Window):
    def __init__(self, parent):
        super().__init__(title=_("Add Shared Folder"), transient_for=parent)
        self.set_modal(True)
        self.set_default_size(400, 250)

        self._response = Gtk.ResponseType.CANCEL

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        self.set_child(vbox)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        vbox.append(grid)

        #_____________________________________________________________________________________________
        # Basic Options Section
        #_____________________________________________________________________________________________

        # Name Path
        nameLabel = Gtk.Label(label="Name:")
        nameLabel.set_halign(Gtk.Align.START)
        self.nameEntry = Gtk.Entry()
        grid.attach(nameLabel, 0, 0, 1, 1)
        grid.attach(self.nameEntry, 1, 0, 1, 1)

        # Folder Path
        pathLabel = Gtk.Label(label="Folder Path:")
        pathLabel.set_halign(Gtk.Align.START)
        browseButton = Gtk.Button(label=_("Browse"))
        browseButton.set_tooltip_text(_("Browse for folder"))
        browseButton.connect("clicked", self.on_browse_clicked)
        browseButton.set_icon_name("folder-open-symbolic")
        grid.attach(browseButton, 2, 1, 1, 1)
        self.pathEntry = Gtk.Entry()
        grid.attach(pathLabel, 0, 1, 1, 1) # ROW, COLUMN, WIDTH, HEIGHT
        grid.attach(self.pathEntry, 1, 1, 1, 1)

        # Comment
        commentLabel = Gtk.Label(label="Comment:")
        commentLabel.set_halign(Gtk.Align.START)
        self.commentEntry = Gtk.Entry()
        grid.attach(commentLabel, 0, 2, 1, 1)
        grid.attach(self.commentEntry, 1, 2, 1, 1)

        # Read Only
        self.readOnlyCheck = Gtk.CheckButton(label=_("Read Only"))
        self.readOnlyCheck.set_halign(Gtk.Align.START)
        grid.attach(self.readOnlyCheck, 0, 3, 2, 1)

        # Guest OK
        self.guestOkCheck = Gtk.CheckButton(label=_("Guest Access"))
        self.guestOkCheck.set_halign(Gtk.Align.START)
        grid.attach(self.guestOkCheck, 0, 4, 2, 1)

        #____________________________________________________________________________________________
        # Advanced options hidden section to prevent unsophisticated users from modifying them
        #____________________________________________________________________________________________

        advancedOptionsSection = Gtk.Expander.new(_("Advanced Options (For Expert Users)"))
        advancedOptionsSection.set_expanded(False)
        grid.attach(advancedOptionsSection, 0, 5, 2, 1)

        advancedOptionsGrid = Gtk.Grid()
        advancedOptionsGrid.set_row_spacing(10)
        advancedOptionsGrid.set_column_spacing(10)

        # Separator
        separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        advancedOptionsGrid.attach(separator, 0, 0, 2, 1)

        # Directory Mask
        directoryMaskLabel = Gtk.Label(label=_("Directory Mask:"))
        directoryMaskLabel.set_halign(Gtk.Align.START)
        self.directoryMaskEntry = Gtk.Entry()
        self.directoryMaskEntry.set_text("0755")
        advancedOptionsGrid.attach(directoryMaskLabel, 0, 1, 1, 1)
        advancedOptionsGrid.attach(self.directoryMaskEntry, 1, 1, 1, 1)

        # Create Mask
        createMaskLabel = Gtk.Label(label=_("Create Mask:"))
        createMaskLabel.set_halign(Gtk.Align.START)
        self.createMaskEntry = Gtk.Entry()
        self.createMaskEntry.set_text("0755")
        advancedOptionsGrid.attach(createMaskLabel, 0, 2, 1, 1)
        advancedOptionsGrid.attach(self.createMaskEntry, 1, 2, 1, 1)

        # Browseable
        self.browseableCheck = Gtk.CheckButton(label=_("Allow Browsing"))
        self.browseableCheck.set_halign(Gtk.Align.START)
        self.browseableCheck.set_active(True)
        advancedOptionsGrid.attach(self.browseableCheck, 0, 3, 2, 1)

        advancedOptionsSection.set_child(advancedOptionsGrid)

        #____________________________________________________________________________________________
        # Valid Users List (Inside advanced Options)
        #____________________________________________________________________________________________

        validUsersLabel = Gtk.Label(label=_("Valid Users:"))
        validUsersLabel.set_halign(Gtk.Align.START)
        validUsersLabel.set_valign(Gtk.Align.START)
        advancedOptionsGrid.attach(validUsersLabel, 0, 4, 1, 1)

        # Container for list and buttons
        validUsersBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # ListBox for users
        self.validUsersListBox = Gtk.ListBox()
        self.validUsersListBox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.validUsersListBox.set_size_request(-1, 100)
        
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_child(self.validUsersListBox)
        scrolledWindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        validUsersBox.append(scrolledWindow)
        
        # Buttons for add/remove
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        self.validUsersEntry = Gtk.Entry()
        self.validUsersEntry.set_placeholder_text(_("Enter username..."))
        self.validUsersEntry.set_hexpand(True)
        buttonBox.append(self.validUsersEntry)
        
        addUserButton = Gtk.Button(label=_("Add"))
        addUserButton.connect("clicked", self.OnAddValidUser)
        buttonBox.append(addUserButton)
        
        removeUserButton = Gtk.Button(label=_("Remove"))
        removeUserButton.connect("clicked", self.OnRemoveValidUser)
        buttonBox.append(removeUserButton)
        
        validUsersBox.append(buttonBox)
        advancedOptionsGrid.attach(validUsersBox, 1, 4, 1, 1)
        
        #____________________________________________________________________________________________
        # Buttons Section
        #____________________________________________________________________________________________

        vbox.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        button_box.set_halign(Gtk.Align.END)
        vbox.append(button_box)

        #Cancel Button
        cancel_button = Gtk.Button(label=_("Cancel"))
        cancel_button.connect("clicked", self.OnCancelClicked)
        button_box.append(cancel_button)

        #OK Button
        ok_button = Gtk.Button(label=_("OK"))
        ok_button.get_style_context().add_class("suggested-action")
        ok_button.connect("clicked", self.OnOkClicked)
        button_box.append(ok_button)

    def on_browse_clicked(self, button):
        # Create a FileDialog in GTK 4
        dialog = Gtk.FileDialog()
        dialog.set_title(_("Select Folder"))
        
        def on_folder_selected(dialog, result):
            try:
                folder = dialog.select_folder_finish(result)
                if folder:
                    self.pathEntry.set_text(folder.get_path())
            except Exception as e:
                pass  # User cancelled
        
        dialog.select_folder(self, None, on_folder_selected)

    def OnCancelClicked(self, button):
        print(_("Cancel clicked"))
        self._response = Gtk.ResponseType.CANCEL
        if hasattr(self, '_loop'):
            self._loop.quit()
        self.destroy()

    def OnAddValidUser(self, button):
        username = self.validUsersEntry.get_text().strip()
        if username:
            label = Gtk.Label(label=username, xalign=0)
            row = Gtk.ListBoxRow()
            row.set_child(label)
            self.validUsersListBox.append(row)
            self.validUsersEntry.set_text("")
    
    def OnRemoveValidUser(self, button):
        row = self.validUsersListBox.get_selected_row()
        if row:
            self.validUsersListBox.remove(row)
    
    def GetValidUsers(self):
        users = []
        row = self.validUsersListBox.get_first_child()
        while row:
            label = row.get_child()
            if label:
                users.append(label.get_label())
            row = row.get_next_sibling()
        return users

    def OnOkClicked(self, button):
        print(_("OK clicked"))
        self._response = Gtk.ResponseType.OK
        if hasattr(self, '_loop'):
            self._loop.quit()
        self.destroy()

    def Run(self) -> SharedFolder | None:
        self._loop = GObject.MainLoop()
        
        def on_close_request(widget, *args):
            self._loop.quit()
            return True

        self.connect("close-request", on_close_request)
        
        self.show()
        
        self._loop.run() 
        
        if self._response == Gtk.ResponseType.OK:
            print(_("Creating SharedFolder from dialog inputs"))
            name = self.nameEntry.get_text()
            path = self.pathEntry.get_text()
            comment = self.commentEntry.get_text()
            read_only = self.readOnlyCheck.get_active()
            guest_ok = self.guestOkCheck.get_active()

            if(path == "" or comment == "" or name == ""):
                print(_('[ERROR] Cannot create shared folder: Missing required fields: {name} {path} {comment}').format(name="{name}" if name == '' else '', path="{path}" if path == '' else '', comment="{comment}" if comment == '' else ''))
                MessageDialog(_("Error"), _("Missing required fields: Name, Path, and Comment are required."), self)
                return None
            
            if(not os.path.exists(path)):
                print(_('[ERROR] Cannot create shared folder: Path does not exist: {path}').format(path=path))
                MessageDialog(_("Error"), _("Path does not exist: {path}").format(path=path), self)
                return None

            folder = SharedFolder(
                name=name,
                path=path,
                comment=comment,
                read_only=read_only,
                guest_ok=guest_ok,
                create_mask="0755",
                directory_mask="0755",
                browseable=True,
                writeable=not read_only,
                valid_users=self.GetValidUsers()
            )
            return folder
        else:
            print(_("Dialog cancelled"))
            return None
        
class EditFolderDialog(Gtk.Window):
    def __init__(self, parent, folder:SharedFolder=None):
        super().__init__(title=_("Edit Shared Folder"), transient_for=parent)
        self.set_modal(True)
        self.set_default_size(400, 250)

        self.originalFolder = folder
        self._response = Gtk.ResponseType.CANCEL

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        self.set_child(vbox)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        vbox.append(grid)

        #_____________________________________________________________________________________________
        # Basic Options Section
        #_____________________________________________________________________________________________

        # Name Path
        nameLabel = Gtk.Label(label=_("Name:"))
        nameLabel.set_halign(Gtk.Align.START)
        self.nameEntry = Gtk.Entry()
        self.nameEntry.set_text(self.originalFolder.name if self.originalFolder else "")
        grid.attach(nameLabel, 0, 0, 1, 1)
        grid.attach(self.nameEntry, 1, 0, 1, 1)

        # Folder Path
        pathLabel = Gtk.Label(label=_("Folder Path:"))
        pathLabel.set_halign(Gtk.Align.START)
        self.pathEntry = Gtk.Entry()
        self.pathEntry.set_text(self.originalFolder.path if self.originalFolder else "")
        grid.attach(pathLabel, 0, 1, 1, 1) # ROW, COLUMN, WIDTH, HEIGHT
        grid.attach(self.pathEntry, 1, 1, 1, 1)

        # Comment
        commentLabel = Gtk.Label(label=_("Comment:"))
        commentLabel.set_halign(Gtk.Align.START)
        self.commentEntry = Gtk.Entry()
        self.commentEntry.set_text(self.originalFolder.comment if self.originalFolder else "")
        grid.attach(commentLabel, 0, 2, 1, 1)
        grid.attach(self.commentEntry, 1, 2, 1, 1)

        # Read Only
        self.readOnlyCheck = Gtk.CheckButton(label=_("Read Only"))
        self.readOnlyCheck.set_halign(Gtk.Align.START)
        if self.originalFolder:
            self.readOnlyCheck.set_active(self.originalFolder.read_only == "yes")
        grid.attach(self.readOnlyCheck, 0, 3, 2, 1)

        # Guest OK
        self.guestOkCheck = Gtk.CheckButton(label=_("Guest Access"))
        self.guestOkCheck.set_halign(Gtk.Align.START)
        if self.originalFolder:
            self.guestOkCheck.set_active(self.originalFolder.guest_ok == "yes")
        grid.attach(self.guestOkCheck, 0, 4, 2, 1)

        #____________________________________________________________________________________________
        # Advanced options hidden section to prevent unsophisticated users from modifying them
        #____________________________________________________________________________________________

        advancedOptionsSection = Gtk.Expander.new(_("Advanced Options (For Expert Users)"))
        advancedOptionsSection.set_expanded(False)
        grid.attach(advancedOptionsSection, 0, 5, 2, 1)

        advancedOptionsGrid = Gtk.Grid()
        advancedOptionsGrid.set_row_spacing(10)
        advancedOptionsGrid.set_column_spacing(10)

        # Separator
        separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        advancedOptionsGrid.attach(separator, 0, 0, 2, 1)

        # Directory Mask
        directoryMaskLabel = Gtk.Label(label=_("Directory Mask:"))
        directoryMaskLabel.set_halign(Gtk.Align.START)
        self.directoryMaskEntry = Gtk.Entry()
        self.directoryMaskEntry.set_text(self.originalFolder.directory_mask if self.originalFolder else "")
        advancedOptionsGrid.attach(directoryMaskLabel, 0, 1, 1, 1)
        advancedOptionsGrid.attach(self.directoryMaskEntry, 1, 1, 1, 1)

        # Create Mask
        createMaskLabel = Gtk.Label(label=_("Create Mask:"))
        createMaskLabel.set_halign(Gtk.Align.START)
        self.createMaskEntry = Gtk.Entry()
        self.createMaskEntry.set_text(self.originalFolder.create_mask if self.originalFolder else "")
        advancedOptionsGrid.attach(createMaskLabel, 0, 2, 1, 1)
        advancedOptionsGrid.attach(self.createMaskEntry, 1, 2, 1, 1)

        # Browseable
        self.browseableCheck = Gtk.CheckButton(label=_("Allow Browsing"))
        self.browseableCheck.set_halign(Gtk.Align.START)
        self.browseableCheck.set_active(self.originalFolder.browseable == "yes" if self.originalFolder else True)
        advancedOptionsGrid.attach(self.browseableCheck, 0, 3, 2, 1)

        #____________________________________________________________________________________________
        # Valid Users List (Inside advanced Options)
        #____________________________________________________________________________________________

        validUsersLabel = Gtk.Label(label=_("Valid Users:"))
        validUsersLabel.set_halign(Gtk.Align.START)
        validUsersLabel.set_valign(Gtk.Align.START)
        advancedOptionsGrid.attach(validUsersLabel, 0, 4, 1, 1)

        # Container for list and buttons
        validUsersBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # ListBox for users
        self.validUsersListBox = Gtk.ListBox()
        self.validUsersListBox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.validUsersListBox.set_size_request(-1, 100)
        
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_child(self.validUsersListBox)
        scrolledWindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        validUsersBox.append(scrolledWindow)
        
        # Populate existing valid users
        if self.originalFolder and self.originalFolder.valid_users:
            for user in self.originalFolder.valid_users:
                label = Gtk.Label(label=user, xalign=0)
                row = Gtk.ListBoxRow()
                row.set_child(label)
                self.validUsersListBox.append(row)
        
        # Buttons for add/remove
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        self.validUsersEntry = Gtk.Entry()
        self.validUsersEntry.set_placeholder_text(_("Enter username..."))
        self.validUsersEntry.set_hexpand(True)
        buttonBox.append(self.validUsersEntry)
        
        addUserButton = Gtk.Button(label=_("Add"))
        addUserButton.connect("clicked", self.OnAddValidUser)
        buttonBox.append(addUserButton)
        
        removeUserButton = Gtk.Button(label=_("Remove"))
        removeUserButton.connect("clicked", self.OnRemoveValidUser)
        buttonBox.append(removeUserButton)
        
        validUsersBox.append(buttonBox)
        advancedOptionsGrid.attach(validUsersBox, 1, 4, 1, 1)

        advancedOptionsSection.set_child(advancedOptionsGrid)
        
        #____________________________________________________________________________________________
        # Buttons Section
        #____________________________________________________________________________________________

        vbox.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        button_box.set_halign(Gtk.Align.END)
        vbox.append(button_box)

        #Cancel Button
        cancel_button = Gtk.Button(label=_("Cancel"))
        cancel_button.connect("clicked", self.OnCancelClicked)
        button_box.append(cancel_button)

        #Save Button
        ok_button = Gtk.Button(label=_("Save"))
        ok_button.get_style_context().add_class("suggested-action")
        ok_button.connect("clicked", self.OnSave)
        button_box.append(ok_button)

    def OnAddValidUser(self, button):
        username = self.validUsersEntry.get_text().strip()
        if username:
            label = Gtk.Label(label=username, xalign=0)
            row = Gtk.ListBoxRow()
            row.set_child(label)
            self.validUsersListBox.append(row)
            self.validUsersEntry.set_text("")
    
    def OnRemoveValidUser(self, button):
        row = self.validUsersListBox.get_selected_row()
        if row:
            self.validUsersListBox.remove(row)
    
    def GetValidUsers(self):
        users = []
        row = self.validUsersListBox.get_first_child()
        while row:
            label = row.get_child()
            if label:
                users.append(label.get_label())
            row = row.get_next_sibling()
        return users

    def OnCancelClicked(self, button):
        print(_("Cancel clicked"))
        self._response = Gtk.ResponseType.CANCEL
        if hasattr(self, '_loop'):
            self._loop.quit()
        self.destroy()

    def OnSave(self, button):
        print(_("Save clicked"))
        self._response = Gtk.ResponseType.OK
        if hasattr(self, '_loop'):
            self._loop.quit()
        self.destroy()

    def Run(self) -> SharedFolder | None:
        self._loop = GObject.MainLoop()
        
        def on_close_request(widget, *args):
            self._loop.quit()
            return True

        self.connect("close-request", on_close_request)
        
        self.show()
        
        self._loop.run() 
        
        if self._response == Gtk.ResponseType.OK:
            print(_("Updating SharedFolder from dialog inputs"))
            name = self.nameEntry.get_text()
            path = self.pathEntry.get_text()
            comment = self.commentEntry.get_text()
            read_only = self.readOnlyCheck.get_active()
            guest_ok = self.guestOkCheck.get_active()

            if(path == "" or comment == "" or name == ""):
                print(_('[ERROR] Cannot edit shared folder: Missing required fields: {name} {path} {comment}').format(name="{name}" if name == '' else '', path="{path}" if path == '' else '', comment="{comment}" if comment == '' else ''))
                MessageDialog(_("Error"), _("Missing required fields: Name, Path, and Comment are required."), self)
                return None
            
            if(not os.path.exists(path)):
                print(_('[ERROR] Cannot edit shared folder: Path does not exist: {}').format(path))
                MessageDialog(_("Error"), _("Path does not exist: {}").format(path), self)
                return None

            newFolder = SharedFolder(
                name=name,
                path=path,
                comment=comment,
                read_only=read_only,
                guest_ok=guest_ok,
                create_mask="0755",
                directory_mask="0755",
                browseable=self.originalFolder.browseable == "yes" if self.originalFolder else True,
                writeable=not read_only,
                valid_users=self.GetValidUsers()
            )
            return newFolder
        else:
            print(_("Dialog cancelled"))
            return None

def MessageDialog(mTitle: str, mMessage: str, parent: Gtk.Window):
    dialog = Gtk.AlertDialog()
    dialog.set_message(mMessage)
    dialog.set_modal(True)
    dialog.set_buttons([_("OK")])
    dialog.choose(parent, None, lambda _obj, _result: None)

def CriticalDialog(mTitle: str, mMessage: str, parent: Gtk.Window, accept:callable, cancel:callable):
    dialog = Gtk.AlertDialog()
    dialog.set_message(mMessage)
    dialog.set_modal(True)
    dialog.set_buttons([_("Cancel"), _("OK")])
    dialog.set_cancel_button(0)
    dialog.set_default_button(1)
    
    def on_response(_dialog, result):
        try:
            response = dialog.choose_finish(result)
            if response == 1:  # OK button
                accept()
            else:
                cancel()
        except:
            cancel()
    
    dialog.choose(parent, None, on_response)