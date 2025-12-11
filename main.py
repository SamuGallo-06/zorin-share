from shared_elements import SharedFolder
import utils
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
from dialogs import AddFolderDialog, EditFolderDialog

class ZorinShare(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.zorinos.zorinshare", flags=gi.repository.Gio.ApplicationFlags.FLAGS_NONE)
        self.sharedFolders = []
        self.connect("activate", self.OnActivate)
    
    def OnActivate(self, app):
        """Create and show the main application window."""
        window = Gtk.ApplicationWindow(application=app, title="Zorin Share")
        window.set_default_size(600, 400)

        headerBar = Gtk.HeaderBar()
        headerBar.set_show_title_buttons(True)
        window.set_titlebar(headerBar)

        # Hamburger Menu (GTK4 style)
        self.menuButton = Gtk.MenuButton()
        self.menuButton.set_icon_name("open-menu-symbolic")
        headerBar.pack_end(self.menuButton)

        # Create menu model
        self.menu = Gio.Menu()
        self.menu.append("Refresh List", "app.refresh")
        self.menu.append("About", "app.about")
        self.menu.append("Quit", "app.quit")
        
        self.menuButton.set_menu_model(self.menu)
        
        # Create actions
        refreshAction = Gio.SimpleAction.new("refresh", None)
        refreshAction.connect("activate", lambda a, p: self.UpdateList())
        self.add_action(refreshAction)
        
        aboutAction = Gio.SimpleAction.new("about", None)
        aboutAction.connect("activate", lambda a, p: self.ShowAboutDialog())
        self.add_action(aboutAction)
        
        quitAction = Gio.SimpleAction.new("quit", None)
        quitAction.connect("activate", lambda a, p: self.quit())
        self.add_action(quitAction)

        mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        mainBox.set_margin_start(20)
        mainBox.set_margin_end(20)
        mainBox.set_margin_top(20)
        mainBox.set_margin_bottom(20)

        self.listBox = Gtk.ListBox()
        self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.UpdateList()

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_child(self.listBox)

        mainBox.append(scrolledWindow)
        scrolledWindow.set_vexpand(True)

        # Add Folder Button
        addButton = Gtk.Button(label="New Shared Folder")
        addButton.set_hexpand(True)
        addButton.set_margin_top(10)
        addButton.connect("clicked", self.OnAddFolder)
        mainBox.append(addButton)

        window.set_child(mainBox)
        window.present()

    def UpdateList(self):
        self.sharedFolders = utils.ParseSmbConf("./smb.conf")

        # Clear existing items
        while self.listBox.get_first_child() is not None:
            self.listBox.remove(self.listBox.get_first_child())

        folder: SharedFolder
            
        for folder in self.sharedFolders:
            row = Gtk.ListBoxRow()
            
            rowBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            rowBox.set_margin_top(5)
            rowBox.set_margin_bottom(5)
            
            folderName = folder.name if folder.name else os.path.basename(folder.path) if folder.path else "Unnamed Folder"
            readOnlyStatus = "<span color='orange'>Read-Only</span>" if folder.read_only else "Writable"
            guestStatus = "Guests allowed" if folder.guest_ok else "<span color='red'>Guests not allowed</span>"

            details = f"<b>{folderName}</b>\n<i>{folder.comment}</i>\nPath: {folder.path}\n{readOnlyStatus}\n{guestStatus}{'' if not folder.valid_users else f'\n<span color="green">Restricted Users</span>'}"

            detailsLabel = Gtk.Label(
                label=details, 
                use_markup=True,
                xalign=0
            )
            detailsLabel.set_wrap(True)

            contentBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            contentBox.set_hexpand(True)
            contentBox.append(detailsLabel)
            detailsLabel.set_hexpand(True)


            # Edit Button
            editIcon = Gtk.Image.new_from_icon_name("document-edit-symbolic")
            editButton = Gtk.Button(child=editIcon)
            editButton.set_valign(Gtk.Align.CENTER)
            contentBox.append(editButton)
            editButton.set_tooltip_text("Edit Shared Folder")
            editButton.connect("clicked", self.OnEditFolder, folder)

            # Delete Button
            deleteIcon = Gtk.Image.new_from_icon_name("edit-delete-symbolic")
            deleteButton = Gtk.Button(child=deleteIcon)
            deleteButton.set_valign(Gtk.Align.CENTER)
            contentBox.append(deleteButton)
            deleteButton.set_tooltip_text("Delete Shared Folder")
            deleteButton.connect("clicked", self.OnDeleteFolder, folder)


            rowBox.append(contentBox)
            row.set_child(rowBox)
            self.listBox.append(row)

    def OnAddFolder(self, button):
        dialog = AddFolderDialog(self.get_active_window())
        print("Add Shared Folder Dialog opened")
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        dialog.set_resizable(False)
        dialog.set_deletable(False)
        newFolder = dialog.Run()
        print("Add Shared Folder Dialog closed")
        if newFolder:
            print(f"New folder to add: {newFolder.path}")
            self.sharedFolders.append(newFolder)
            utils.AddShareToSmbConf(newFolder)
            self.UpdateList()

    def OnEditFolder(self, button, folder:SharedFolder):
        dialog = EditFolderDialog(self.get_active_window(), folder)
        print("Edit Shared Folder Dialog opened")
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        dialog.set_resizable(False)
        dialog.set_deletable(False)
        result = dialog.Run()
        print("Edit Shared Folder Dialog closed")
        if result:
            print(f"Folder edited: {folder.path}")
            utils.UpdateShareInSmbConf(folder, result)
        self.UpdateList()
    
    def OnDeleteFolder(self, button, folder:SharedFolder):
        #Show critical dialog
        messageDialog = Gtk.MessageDialog(
            transient_for=self.get_active_window(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Are you sure you want to delete the shared folder '{folder.name}'?"
        )
        messageDialog.format_secondary_text("This action cannot be undone.")
        response = messageDialog.run()
        messageDialog.destroy()
        if response == Gtk.ResponseType.OK:
            print(f"Deleting folder: {folder.path}")
            self.sharedFolders.remove(folder)
            utils.RemoveShareFromSmbConf(folder)
            self.UpdateList()
    
    def ShowAboutDialog(self):
        """Show the About dialog in GNOME style."""
        aboutDialog = Gtk.AboutDialog()
        aboutDialog.set_transient_for(self.get_active_window())
        aboutDialog.set_modal(True)
        
        # Application info
        aboutDialog.set_program_name("Zorin Share")
        aboutDialog.set_version("1.0.0")
        aboutDialog.set_comments("A modern GTK4 application for managing Samba shared folders")
        aboutDialog.set_website("https://github.com/SamuGallo-06/zorin-share")
        aboutDialog.set_website_label("GitHub Repository")
        
        # Copyright and license
        aboutDialog.set_copyright("© 2025 Samuele Gallicani")
        aboutDialog.set_license_type(Gtk.License.GPL_3_0)
        
        # Authors
        aboutDialog.set_authors(["SamuGallo-06"])
        
        aboutDialog.set_logo_icon_name("folder-remote")
        
        aboutDialog.present()


if __name__ == "__main__":
    app = ZorinShare()
    exit_status = app.run(None)
    import sys
    sys.exit(exit_status)