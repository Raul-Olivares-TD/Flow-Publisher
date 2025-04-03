import hou # type: ignore
import os

class Publisher:
    def __init__(self, name, version, type, output_path):
        self.name = name
        self.version = version
        self.type = type
        self.output_path = output_path  
        
        os.makedirs(self.output_path, exist_ok=True)    
    
    def build_version(self):
        """Build the asset version correctly depending on the version number 
        it has.
        
        :return: A string with the version correctly like _v004 or _v034
        :rtype: str    
        """
        
        # Three digit numbers
        final_version = f"_v{self.version:03d}"
        
        # "_v123" | "_v041" | "_v002"
        return final_version
    
    def export_assets(self):
        """Export the assets acording the type."""
        
        hda = hou.pwd()
        output_path = f"{self.output_path}{self.name}{self.build_version()}"
        
        # Save nodes from the HDA according to the node type
        nodes_types ={
            "rop_fbx" : None,
            "rop_alembic": None,
            "filecache::2.0": None,
            "usdexport": None
        }
        
        # Get each rop node insde the hda
        for node in hda.children():
            if node.type().name() in nodes_types:
                nodes_types[node.type().name()] = node
                
        # Settings of each node for export the assets
        export_setting = {
            ".fbx": {
                "node": nodes_types["rop_fbx"],
                "param": "sopoutput",
                "extension": ".fbx",
            },
            
            ".abc": {
                "node": nodes_types["rop_alembic"],
                "param": "filename",
                "extension": ".abc",
            },
            
            ".vdb": {
                "node": nodes_types["filecache::2.0"],
                "param": "basename",
                "param2": "basedir",
                "extension": None
            },
            
            ".usd": {
                "node": nodes_types["usdexport"],
                "param": "lopoutput",
                "extension": ".usd",
            },
            
        }        
        
        if self.type in export_setting:
            # Gets the export settings block of the corresponding node
            type = export_setting[self.type]
            node = type["node"]
            
            # If node no exists create it at the export_settings dict
            if node:
                if self.type == ".vdb":
                    vdb_name = f"{self.name}{self.build_version()}"
                    node.parm(type["param"]).set(vdb_name)
                    node.parm(type["param2"]).set(self.output_path)
                
                else:
                    # Nodes that isn't vdb type "fbx"|"abc"|"usd"...
                    out_file = f"{output_path}{type['extension']}"
                    node.parm(type["param"]).set(out_file)
            
            else:
                hou.ui.displayMessage(f"Unexist {self.type} node" 
                                      f"at export settings")
        
        # Button pressed for export the assets        
        node.parm("execute").pressButton()
        
        