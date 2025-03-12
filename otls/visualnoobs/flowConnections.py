# import flipbookGenerator
import hou # type: ignore
import os
import shotgun_api3


class Flow:
	def __init__(self):
		self.sg = shotgun_api3.Shotgun(os.environ["FLOW_URL"],
									   script_name=os.environ["FLOW_SCRIPT"],
									   api_key=os.environ["FLOW_KEY"])

	def get_user_id(self):
		"""Gets the ID of the user autenitcate at Flow.
  
		:return: The user id
		:rtype: int
  		"""
		SG_USER = os.environ["FLOW_USER"] # Usa variables de entorno
		filters = [["email", "is", SG_USER]]
		user_data = self.sg.find_one("HumanUser", filters, fields=["id"])
		
		return user_data["id"]                             

	def projects(self):
		"""Get the project on the user is assigned to.

		:return: List with a dictionary with the name, id and type of the projects.
		:rtype: list
		"""
  
		filters = [["id", "is", self.get_user_id()]]
		fields = ["projects"]
		user_data = self.sg.find_one("HumanUser", filters, fields=fields)
		
		return user_data["projects"]

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
			
		return tasks

	def shots(self):
		"""Creates the shots names from the tasks.
		
		:return: A list with the shots names.
		:rtype: list
		"""
  
		# Gets the id, name, type of the shots
		shots = [shot["entity"] for shot in self.tasks()]

		return shots

	def sequences(self):
		"""Creates the sequences names from the tasks.
		
		:return: A list with the sequences names.
		:rtype: list
		"""

		# Gets the name of each sequence
		sequence = [sequence["entity"]["name"].split("_")[0]
				    for sequence in self.tasks()]
  		
		return sequence

	def tasks_data(self):
		"""Creates a dictionary with the task names and id.
		
		:return: A dictionary with the task names and id.
		:rtype: dict
		"""
  
		# The task name like key and the id like value
		task = {task["content"] : task["id"] for task in self.tasks()}

		return task

	def project_data(self):
		"""Creates a dictionary with the project names and id.
		
		:return: A dictionary with the projects names and id.
		:rtype: dict
		"""
  
		# The project name like key and the id like value
		project = {project["name"] : project["id"] 
             	   for project in self.projects()}

		return project


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


# # MANERA DE LLAMAR LA SUBIDA DE FLIPBOOKS A FLOW
# outputpath = "D:/EPF/flipbook/"
# project_name = hou.pwd().parm("project").evalAsString()		
# task_name = hou.pwd().parm("task").evalAsString()
# description = hou.pwd().parm("desc").evalAsString()
# basename = flipbookGenerator.WalkIntoDirs().version_increment_flipbook()

# UploadToFlow().upload_flipbook(outputpath, project_name, task_name, description, basename)

