import flowConnections
import hou # type: ignore


class Parameters:
    def menu_project(self):
        """Creates the project menu data from flow."""
        
        projects = flowConnections.Flow().projects()

        token = []
        label = []

        for project in projects:
            name = project["name"]
            token.append(name)
            label.append(name)

        node_type = hou.pwd().type().definition()
        group = node_type.parmTemplateGroup() 

        project_menu = hou.pwd().parm("project").parmTemplate()
        project_menu.setMenuItems(token)
        project_menu.setMenuLabels(label)

        group.replace("project", project_menu)
        node_type.setParmTemplateGroup(group)    
            
    
    def menu_sequence(self):
        """Creates the sequence menu data from flow."""
        
        sequences = flowConnections.Flow().sequences()

        token = []
        label = []

        for sequence in sequences:
            token.append(sequence)
            label.append(sequence)

        node_type = hou.pwd().type().definition()
        group = node_type.parmTemplateGroup() 

        tokens = list(dict.fromkeys(token))
        labels = list(dict.fromkeys(label))

        sequence_menu = hou.pwd().parm("seq").parmTemplate()
        sequence_menu.setMenuItems(tokens)
        sequence_menu.setMenuLabels(labels)

        group.replace("seq", sequence_menu)
        node_type.setParmTemplateGroup(group)
    
    def menu_shot(self):
        """Creates the shot menu data from flow."""    
        
        shots = flowConnections.Flow().shots()

        token = []
        label = []

        for shot in shots:
            name = shot["name"]
            token.append(name)
            label.append(name)

        tokens = list(dict.fromkeys(token))
        labels = list(dict.fromkeys(label))

        node_type = hou.pwd().type().definition()
        group = node_type.parmTemplateGroup() 

        shot_menu = hou.pwd().parm("shot").parmTemplate()
        shot_menu.setMenuItems(tokens)
        shot_menu.setMenuLabels(labels)

        group.replace("shot", shot_menu)
        node_type.setParmTemplateGroup(group)
    
    def menu_task(self):
        """Creates the task menu data from flow."""
        
        tasks = flowConnections.Flow().tasks()

        token = []
        label = []

        for task in tasks:
            name = task["content"]
            token.append(name)
            label.append(name)

        node_type = hou.pwd().type().definition()
        group = node_type.parmTemplateGroup() 

        sequence_menu = hou.pwd().parm("task").parmTemplate()
        sequence_menu.setMenuItems(token)
        sequence_menu.setMenuLabels(label)

        group.replace("task", sequence_menu)
        node_type.setParmTemplateGroup(group)
        
    def menu_parameters_default(self):
        """Sets the parameters of each flow menu based on the current values
        ​​of the scene you are working on.
        """
        
        basename = hou.hipFile.basename()
        basename_split = basename.split("_")
        project = basename_split[0]
        seq = basename_split[1]
        shot = basename_split[2]+"_"+basename_split[3]
        task = basename_split[4]

        # Project
        label_project = hou.pwd().parm("project").menuLabels()
        index_project = label_project.index(project)
        sets_project = hou.pwd().parm("project").set(index_project)

        # Seq
        label_seq = hou.pwd().parm("seq").menuLabels()
        index_seq = label_seq.index(seq)
        sets_seq = hou.pwd().parm("seq").set(index_seq)

        # Shot
        label_shot = hou.pwd().parm("shot").menuLabels()
        index_shot = label_shot.index(shot)
        sets_shot = hou.pwd().parm("shot").set(index_shot)    

        # Task
        label_task = hou.pwd().parm("task").menuLabels()
        index_task = label_task.index(task)
        sets_task = hou.pwd().parm("task").set(index_task)
            
            