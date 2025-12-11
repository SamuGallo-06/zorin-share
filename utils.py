from shared_elements import SharedFolder
import os

SMB_CONF_PATH = "./smb.conf"

def CraftSmbEntry(folder: SharedFolder) -> str:
        entry = f"""## Created By Zorin Share ##
[{folder.name}]
   comment = {folder.comment}
   path = {folder.path}
   read only = {'yes' if folder.read_only else 'no'}
   guest ok = {'yes' if folder.guest_ok else 'no'}
   create mask = {folder.create_mask}
   directory mask = {folder.directory_mask}
   browseable = {'yes' if folder.browseable else 'no'}
   writeable = {'yes' if folder.writeable else 'no'}
   {"valid users = " + ', '.join(folder.valid_users) if folder.valid_users else ''}
"""
        return entry

def ParseSmbConf(configPath: str = SMB_CONF_PATH) -> list:
        values = {}
        folders = []
        currentSection = None

        try:
                with open(configPath, "r") as f:
                        smbConf = f.read()
        except FileNotFoundError:
                print(f"[ERROR] Config file not found: {configPath}")
                return []
        except PermissionError:
                print(f"[ERROR] Permission denied reading: {configPath}")
                return []
    
        for line in smbConf.splitlines():
                line = line.strip() 

                # Ignore empty lines and comments
                if not line or line.startswith('#') or line.startswith(';'):
                        continue
                
                # Identify sections ([section_name])
                if line.startswith('[') and line.endswith(']'):
                        sectionName = line[1:-1].strip()
                        currentSection = sectionName
                        values[currentSection] = {}
                
                # Identify parameters (key = value)
                elif '=' in line:
                        # Ensure there is a current section before adding parameters
                        if currentSection is None:
                                continue 
                        
                        key, val = line.split('=', 1)
                        
                        # Clean key and value
                        key = key.strip()
                        val = val.strip()
                        
                        # Save the parameter in the current section
                        values[currentSection][key] = val
            
        # System sections to ignore (not user shares)
        systemSections = ['global', 'printers', 'print$', 'homes', 'netlogon', 'profiles']
        
        for section, params in values.items():
                # Ignore system sections
                if section.lower() in systemSections:
                        continue
                
                path = params.get('path', '')
                
                # Skip sections without a path (likely not a file share)
                if not path:
                        continue
                comment = params.get('comment', '')
                readOnly = params.get('read only', 'yes').lower() == 'yes'
                guestOk = params.get('guest ok', 'no').lower() == 'yes'
                createMask = params.get('create mask', '0755')
                directoryMask = params.get('directory mask', '0755')
                browseable = params.get('browseable', 'yes').lower() == 'yes'
                writeable = params.get('writeable', 'no').lower() == 'yes'
                
                validUsersStr = params.get('valid users', '')
                validUsers = [user.strip() for user in validUsersStr.split(',')] if validUsersStr else []
                        
                folder = SharedFolder(
                        name=section,
                        path=path,
                        comment=comment,
                        read_only=readOnly,
                        guest_ok=guestOk,
                        create_mask=createMask,
                        directory_mask=directoryMask,
                        browseable=browseable,
                        writeable=writeable,
                        valid_users=validUsers
                        )
                folders.append(folder)
                
        return folders

def RemoveShareFromSmbConf(folder: SharedFolder, configPath: str = SMB_CONF_PATH) -> bool:
        try:
                with open(configPath, "r") as f:
                        smbConf = f.read()
        except FileNotFoundError:
                print(f"[ERROR] Config file not found: {configPath}")
                return False
        except PermissionError:
                print(f"[ERROR] Permission denied reading: {configPath}")
                return False
        
        # Split the config into sections
        sections = smbConf.split('[')
        newSections = []
        
        for section in sections:
                if section.startswith(folder.name + ']'):
                        # Skip this section to remove it
                        continue
                if section.strip():  # Avoid adding empty sections
                        newSections.append('[' + section)
        
        newSmbConf = '\n'.join(newSections)
        
        try:
                with open(configPath, "w") as f:
                        f.write(newSmbConf)
        except PermissionError:
                print(f"[ERROR] Permission denied writing to: {configPath}")
                return False
        
        return True

def AddShareToSmbConf(folder: SharedFolder, configPath: str = SMB_CONF_PATH) -> bool:
        entry = CraftSmbEntry(folder)
        
        try:
                with open(configPath, "a") as f:
                        f.write('\n' + entry)
        except PermissionError:
                print(f"[ERROR] Permission denied writing to: {configPath}")
                return False
        
        return True

def UpdateShareInSmbConf(folder: SharedFolder, new_folder: SharedFolder, configPath: str = SMB_CONF_PATH) -> bool:
        if not RemoveShareFromSmbConf(folder, configPath):
                return False
        if not AddShareToSmbConf(new_folder, configPath):
                return False
        return True
        
                      