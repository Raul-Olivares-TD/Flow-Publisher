import os
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


class GoogleDrive:
    def __init__(self):
        """Authenticate with Google Drive using the credentials json file."""
        self.creds = None
        # Grant Permissions: If modifying these scopes, delete the file token.json.
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        token_path = "D:\\HoudiniDev\\houdiniTools\\token.json"
        cred_path = "D:\\HoudiniDev\\houdiniTools\\credentials.json"

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())

        # Log in client 
        self.service = build("drive", "v3", credentials=self.creds)

    def folder_project_id(self, project):
        """Gets the id of the project folder from Google Drive.
        
        :param project: Project name.
        :return: The id of the project folder.
        :rtype: str
        """
        
        query = f"name='{project}'"

        # Call the Drive v3 API
        results = (
            self.service.files()
            .list(q=query, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])[0]["id"]
        
        # "127763ygaqshjvajsayfs651gv"        
        return items

    def folder_assets_id(self, parent_id, folder_name):
        """Gets the id of the assets folder from Google Drive.
        
        :param parent_id: The id from te parent folder.
        :param folder_name: The name of the folder to save the files.
        :return: The id of the project folder.
        :rtype: str
        """
        
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        result = self.service.files().list(q=query, fields="files(id, name)").execute()
        folders = result.get("files", [])
        
        # "127763ygaqshjvajsayfs651gv"     
        return folders[0]["id"]      
    
    def create_folder(self, folder_name, assets_folder_id):        
        """Creates a folder in Google Drive and returns its ID.
        
        :param folder_name: Name of the folder to create.
        :param assets_folder_id: Id of the parent folder.
        :return: The id of the new folder.
        :rtype: str
        """
        
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [assets_folder_id]
        }
        
        folder = (
            self.service.files()
            .create(body=file_metadata, fields="id")
            .execute()
        )
        
        # "127763ygaqshjvajsayfs651gv"
        return folder["id"]
    
    def upload_file(self, file_path, parent_id):
        """Upload a file to Google Drive within a specific folder.
        
        :param file_path: Path where the file are.
        :param parent_id: Id of the parent folder.
        :return: The id of the file.
        :rtype: str
        """

        file_name = os.path.basename(file_path)
        file_metadata = {"name": file_name, "parents": [parent_id]}
        media = MediaFileUpload(file_path, resumable=True)

        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        
        # "127763ygaqshjvajsayfs651gv"
        return file.get("id")
    
    def upload_folder(self, folder_path, parent_id):
        """Upload a folder and all its contents to Google Drive.
        
        :param folder_path: Path where the folder are.
        :param parent_id: Id of the parent folder.
        :return: The id of the folder.
        :rtype: str
        """

        folder_name = os.path.basename(folder_path)
        folder_id = self.create_folder(folder_name, parent_id)

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):  # Solo sube archivos (ignora subcarpetas)
                self.upload_file(file_path, folder_id)

        # "127763ygaqshjvajsayfs651gv"
        return folder_id

    def share_link(self, file_id):
        """Create the link to share and get public permisions at the file.
        
        :param file_id: File id to create the link.
        :return: The link from the file to share.
        :rtype: str
        """
        
        # Grant permissions so anyone with the link can view the file
        self.service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()

        # Generate public link
        link = f"https://drive.google.com/file/d/{file_id}/view"
        
        return link
     
