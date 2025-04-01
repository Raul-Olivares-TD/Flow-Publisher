import os
import shotgun_api3


class Flow:
	def __init__(self):
		self.sg = shotgun_api3.Shotgun(os.environ["FLOW_URL"],
									   script_name=os.environ["FLOW_SCRIPT"],
									   api_key=os.environ["FLOW_KEY"])

	def get_user_id(self):
		"""Gets the ID of the user autenitcate at Flow.
  
		:return: The user id.
		:rtype: int
  		"""
		SG_USER = os.environ["FLOW_USER"] 
		filters = [["email", "is", SG_USER]]
		user_data = self.sg.find_one("HumanUser", filters, fields=["id"])
		
		# 88
		return user_data["id"]                             

	def projects(self):
		"""Get the project on the user is assigned to.

		:return: List with a dictionary with the name, id and type of the projects.
		:rtype: list
		"""
  
		filters = [["id", "is", self.get_user_id()]]
		fields = ["projects"]
		user_projects = self.sg.find_one("HumanUser", filters, fields=fields)
		
		# [{"name": "EPF", "id": 123, "type": "Project"}]...
		return user_projects["projects"]

	def tasks(self):
		"""Get the tasks on the user is assigned to.

		:return: List with a dictionary with the name, 
		id, shot and project of each task.
		:rtype: list
		"""
  
		tasks = []
		for project in self.projects():
			filters = [
				["project", "is", {"type": "Project", "id": project["id"]}],
				["task_assignees", "is", {"type": "HumanUser", "id": self.get_user_id()}],
			]
			fields = ["content", "entity", "project"]
			tasks += self.sg.find("Task", filters, fields)
			
		# [{"name": "fxDesintegracion", "id": 1292, "Shot": "LT_0010", "Project": "EPF"}]
		return tasks

	def shots(self):
		"""Creates the shots names from the tasks.
		
		:return: A list with the shots names.
		:rtype: list
		"""
  
		# Gets the id, name, type of the shots
		shots = [shot["entity"] for shot in self.tasks()]

		# ["LT_0010", "DF_0010", "DF_0020"]...
		return shots

	def sequences(self):
		"""Creates the sequences names from the tasks.
		
		:return: A list with the sequences names.
		:rtype: list
		"""

		# Gets the name of each sequence
		sequence = [sequence["entity"]["name"].split("_")[0]
				    for sequence in self.tasks()]
  		
		# ["LT", "DF", "MFR", "SE"]...
		return sequence

	def tasks_data(self):
		"""Creates a dictionary with the task names and id.
		
		:return: A dictionary with the task names and id.
		:rtype: dict
		"""
  
		# The task name like key and the id like value
		task = {task["content"] : task["id"] for task in self.tasks()}

		# {"fxFire": 1245, "fxDestruction": 1453}...
		return task

	def project_data(self):
		"""Creates a dictionary with the project names and id.
		
		:return: A dictionary with the projects names and id.
		:rtype: dict
		"""
  
		# The project name like key and the id like value
		project = {project["name"] : project["id"] 
             	   for project in self.projects()}

		# {"EPF": 123, "NPT": 124}...
		return project

	def asset_type(self):
		"""Gets the types of the assets assign at the project.

		:return: A list with the type of assets like ["Model", "Camera"].
		:rtype: list
  		"""
    
		r = self.sg.find("Asset", [], fields=["sg_asset_type"])

		type_list = [type["sg_asset_type"] for type in r]
		
		# ["Model", "Environment", "Camera"]...
		return list(dict.fromkeys(type_list))

	def asset_id(self, asset_name, project_name):
		"""Get the id of the asset at the project.

		:param asset_name: Name of the asset to search for.
		:param project_name: Name of the project in which the asset is located.
		:return: The asset id.
		:rtype: int
  		"""		
    
		project_id = self.project_data()[project_name]
		
		filters = [
			["project", "is", {"type": "Project", "id": project_id}],
			["code", "is", asset_name]
		]

		r = self.sg.find("Asset", filters, fields=["id"])
  
		# 123...
		return r[0]["id"]


class UploadToFlow(Flow):
	def __init__(self):
		super().__init__()
		
	def upload_flipbook(self, outputpath, project_name, task_name,
                     	description, basename):
		"""Upload the flipbook to flow getting the data from houdini.
		But first creates the version and after upload the flipbook to Flow.
  
		:param output_path: Path where the file are.
		:param project_name: Name of the project work on.
		:param task_name: Name of task work on.
		:param description: Description content to upload.
		:param basename: Basename of the movie to upload.
  		"""

		project_id = self.project_data()[project_name]
		task_id = self.tasks_data()[task_name]
		user_id = self.get_user_id()
  
		data = {
			"project": {"type": "Project", "id": project_id},
			"sg_task": {"type": "Task", "id": task_id},
			"code": "fxDesintegracion_v004",
			"description": description,
			"sg_status_list": "rev",
			"user": {"type": "HumanUser", "id": user_id}
		}

		# Creates the version of the mp4 first
		r = self.sg.create("Version",data, return_fields=["id"])

		movie = os.path.join(outputpath, f"{basename}.mp4")

		# Upload the flipbook at the version creates before
		self.sg.upload("Version", r["id"], movie, 
                      	field_name="sg_uploaded_movie")

	def check_asset_exists(self, project_name, asset_name, version, 
                           asset_link):
		"""Check if the asset exist at Flow for create it if not exist or upload
  		a version directly if the asset exists.	
    
		:param project_name: Name of the project.
		:param asset_name: Name of the asset.
		:param version: Number of the asset version.
		:param asset_link: The link with the file are saved.
     	"""
      
		p_id = self.project_data()[project_name]
  
		filters = [
      	["project", "is", {"type": "Project", "id": p_id}],
       ]		
  
		r = self.sg.find("Asset", filters, fields=["code"])

		assets_name = [name["code"] for name in r]
    
		asset_version = f"{asset_name}_v{version:03d}"
        
		if asset_name in assets_name:
			asset_id = self.asset_id(asset_name, project_name)
			self.up_asset_version(project_name, asset_id, asset_version, 
                         		  asset_link)

		else:
			asset_id = self.create_asset(project_name, asset_name)
			self.up_asset_version(project_name, asset_id, asset_version, 
                                  asset_link)

	def create_asset(self, project_name, asset_name):
		"""Create an asset in the Asset Entity Type of Flow.
  
		:param project_name: Name of the project.
		:param asset_name: Name of the asset.
		:return: The asset id.
		:rtype: int
  		"""
		
		p_id = self.project_data()[project_name]
     
		data = {
			"project": {"type": "Project", "id": p_id},
			"code": asset_name,
			"sg_asset_type": "Model",
		}

		r = self.sg.create("Asset",data, return_fields=["id"])

		# 89
		return r["id"]

	def up_asset_version(self, project_name, asset_id, asset_version, 
                      	 asset_link):
		"""Upload a version of the asset to Flow.

		:param project_name: Name of the project.
		:param asset_id: Asset id for upload the version.
		:param asset_version: Asset name+version.
		:param asset_link: Link where the asset is saved.
  		"""
     
		project_id = self.project_data()[project_name]
		user_id = self.get_user_id()
     
		data = {
			"project": {"type": "Project", "id": project_id},
			"entity": {"type": "Asset", "id": asset_id},
			"code": asset_version,
			"sg_status_list": "rev",
			"sg_path_to_geometry": asset_link,
			"user": {"type": "HumanUser", "id": user_id}
		}

		self.sg.create("Version",data, return_fields=["id"])
  		
