from shared_elements import SharedFolder
import utils
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject
from dialogs import AddFolderDialog, EditFolderDialog

from i18n import _ # Import translation function

PROGRAM_NAME = "Samba Configurator"
APPLICATION_ID = "com.samugallo.samba-configurator"

class ZorinShare(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APPLICATION_ID, flags=gi.repository.Gio.ApplicationFlags.FLAGS_NONE)
        self.sharedFolders = []
        self.connect("activate", self.OnActivate)
    
    def OnActivate(self, app):
        """Create and show the main application window."""
        # Check Samba status before showing the window
        sambaStatus = utils.CheckSambaStatus()
        
        if not sambaStatus['installed']:
            self.ShowSambaErrorDialog(_('Samba Not Installed'), 
                                     _('Samba is not installed on your system. This application requires Samba to function.\n\nPlease install Samba using:\nsudo apt install samba'),
                                     critical=True)
            return
        
        if not sambaStatus['running']:
            self.ShowSambaWarningDialog()
        
        window = Gtk.ApplicationWindow(application=app, title=PROGRAM_NAME)
        window.set_default_size(600, 400)

        headerBar = Gtk.HeaderBar()
        headerBar.set_show_title_buttons(True)
        window.set_titlebar(headerBar)

        # Hamburger Menu (GTK4 style)
        self.menuButton = Gtk.MenuButton()
        self.menuButton.set_icon_name("open-menu-symbolic")
        headerBar.pack_end(self.menuButton)

        # Samba Start/Stop Button
        self.sambaStartStopButton = Gtk.Button()
        headerBar.pack_start(self.sambaStartStopButton)
        self.sambaStartStopButton.connect("clicked", self.OnSambaStartStopClicked)
        self.sambaStartStopButton.set_tooltip_text(_("Start/Stop Samba Service"))
        self.sambaStartStopButton.set_icon_name("system-shutdown-symbolic")

        #Status Indicator
        self.sambaStatusIndicator = Gtk.Image()
        self.sambaStatusIndicator.set_pixel_size(16)
        headerBar.pack_start(self.sambaStatusIndicator)
        self.sambaStatusIndicator.set_tooltip_text(_("Samba Service Status"))
        self.UpdateSambaStatusIndicator()

        # Create menu model
        self.menu = Gio.Menu()
        self.menu.append((_('Refresh List')), "app.refresh")
        self.menu.append(_("About"), "app.about")
        self.menu.append(_("Quit"), "app.quit")
        
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
        addButton = Gtk.Button(label=_("New Shared Folder"))
        addButton.set_hexpand(True)
        addButton.set_margin_top(10)
        addButton.connect("clicked", self.OnAddFolder)
        mainBox.append(addButton)

        window.set_child(mainBox)
        window.present()

    def OnSambaStartStopClicked(self, button):
        sambaStatus = utils.CheckSambaStatus()
        if sambaStatus['running']:
            # Stop Samba
            if utils.StopSambaService():
                self.ShowInfoDialog(_("Success"), _("Samba service stopped successfully"))
            else:
                self.ShowErrorDialog(_("Error"), _("Failed to stop Samba service.\n\nPlease stop it manually:\nsudo systemctl stop smbd"))
        else:
            # Start Samba
            if utils.StartSambaService():
                self.ShowInfoDialog(_("Success"), _("Samba service started successfully"))
            else:
                self.ShowErrorDialog(_("Error"), _("Failed to start Samba service.\n\nPlease start it manually:\nsudo systemctl start smbd"))
        self.UpdateSambaStatusIndicator()

    def UpdateSambaStatusIndicator(self):
        sambaStatus = utils.CheckSambaStatus()
        if sambaStatus['running']:
            self.sambaStatusIndicator.set_from_icon_name("network-transmit-receive-symbolic")
            self.sambaStatusIndicator.set_tooltip_text(_("Samba Service is Running"))
        else:
            self.sambaStatusIndicator.set_from_icon_name("network-offline-symbolic")
            self.sambaStatusIndicator.set_tooltip_text(_("Samba Service is Stopped"))

    def UpdateList(self):
        self.sharedFolders = utils.ParseSmbConf()

        # Clear existing items
        while self.listBox.get_first_child() is not None:
            self.listBox.remove(self.listBox.get_first_child())

        folder: SharedFolder
            
        for folder in self.sharedFolders:
            row = Gtk.ListBoxRow()
            
            rowBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            rowBox.set_margin_top(5)
            rowBox.set_margin_bottom(5)
            
            folderName = folder.name if folder.name else os.path.basename(folder.path) if folder.path else _("Unnamed Folder")
            readOnlyStatus = "<span color='orange'>" + _("Read-Only") + "</span>" if folder.read_only else _("Writable")
            guestStatus = _("Guests allowed") if folder.guest_ok else "<span color='red'>" + _("Guests not allowed") + "</span>"

            details = f"<b>{folderName}</b>\n<i>{folder.comment}</i>\n" + _("Path") + f": {folder.path}\n{readOnlyStatus}\n{guestStatus}{'' if not folder.valid_users else f'\n<span color=\"green\"> {_("Restricted Users")} </span>'}"

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
            editButton.set_tooltip_text(_("Edit Shared Folder"))
            editButton.connect("clicked", self.OnEditFolder, folder)

            # Delete Button
            deleteIcon = Gtk.Image.new_from_icon_name("edit-delete-symbolic")
            deleteButton = Gtk.Button(child=deleteIcon)
            deleteButton.set_valign(Gtk.Align.CENTER)
            contentBox.append(deleteButton)
            deleteButton.set_tooltip_text(_("Delete Shared Folder"))
            deleteButton.connect("clicked", self.OnDeleteFolder, folder)


            rowBox.append(contentBox)
            row.set_child(rowBox)
            self.listBox.append(row)

    def OnAddFolder(self, button):
        dialog = AddFolderDialog(self.get_active_window())
        print(_("Add Shared Folder Dialog opened"))
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        dialog.set_resizable(False)
        dialog.set_deletable(False)
        newFolder = dialog.Run()
        print(_("Add Shared Folder Dialog closed"))
        if newFolder:
            print(_("New folder to add: ") + newFolder.path)
            self.sharedFolders.append(newFolder)
            utils.AddShareToSmbConf(newFolder)
            self.UpdateList()

    def OnEditFolder(self, button, folder:SharedFolder):
        dialog = EditFolderDialog(self.get_active_window(), folder)
        print(_("Edit Shared Folder Dialog opened"))
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        dialog.set_resizable(False)
        dialog.set_deletable(False)
        result = dialog.Run()
        print(_("Edit Shared Folder Dialog closed"))
        if result:
            print(_("Folder edited: ") + folder.path)
            utils.UpdateShareInSmbConf(folder, result)
        self.UpdateList()
    
    def OnDeleteFolder(self, button, folder:SharedFolder):
        #Show critical dialog
        messageDialog = Gtk.MessageDialog(
            transient_for=self.get_active_window(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_("Are you sure you want to delete the shared folder " + folder.name + "?")
        )
        messageDialog.format_secondary_text(_("This action cannot be undone."))
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
        aboutDialog.set_program_name(PROGRAM_NAME)
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
    
    def ShowSambaWarningDialog(self):
        """Show warning dialog when Samba is not running."""
        dialog = Gtk.AlertDialog()
        dialog.set_message(_("Samba Service Not Running"))
        dialog.set_detail(_("The Samba service is installed but not currently running.\n\nWould you like to start it now?"))
        dialog.set_buttons([_("Cancel"), _("Start Samba")])
        dialog.set_default_button(1)
        dialog.set_cancel_button(0)
        
        def on_response(dialog, result):
            try:
                response = dialog.choose_finish(result)
                if response == 1:  # Start Samba button
                    if utils.StartSambaService():
                        self.ShowInfoDialog(_("Success"), _("Samba service started successfully"))
                    else:
                        self.ShowErrorDialog(_("Error"), _("Failed to start Samba service.\n\nPlease start it manually:\nsudo systemctl start smbd"))
            except Exception as e:
                pass  # User cancelled
        
        dialog.choose(self.get_active_window(), None, on_response)
    
    def ShowSambaErrorDialog(self, title: str, message: str, critical: bool = False):
        """Show error dialog for Samba issues."""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons([_("Quit") if critical else _("OK")])
        
        def on_response(dialog, result):
            try:
                dialog.choose_finish(result)
                if critical:
                    self.quit()
            except Exception:
                if critical:
                    self.quit()
        
        dialog.choose(None, None, on_response)
    
    def ShowInfoDialog(self, title: str, message: str):
        """Show info dialog."""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons([_("OK")])
        dialog.choose(self.get_active_window(), None, lambda d, r: d.choose_finish(r))
    
    def ShowErrorDialog(self, title: str, message: str):
        """Show error dialog."""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_buttons([_("OK")])
        dialog.choose(self.get_active_window(), None, lambda d, r: d.choose_finish(r))


if __name__ == "__main__":
    app = ZorinShare()
    exit_status = app.run(None)
    import sys
    sys.exit(exit_status)