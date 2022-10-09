#!/usr/bin/python

#########################################################################
#2022-09-24 mzhai support case 2: denpendency in vcxproj.
#2018-08-01 mzhai born 
########################################################################

import sys,re

from bs4 import BeautifulSoup
import os
#import os for opening project file to search below kind of dependencies(case 2).
#<ProjectReference Include="..\MsgCreator\MsgCreator.vcxproj">
#      <Project>{d3eada85-50f9-4a1d-a2f7-18612358b436}</Project>
#      <ReferenceOutputAssembly>false</ReferenceOutputAssembly>
#</ProjectReference>

projectsCommentMap = {
	'project1':'comment1'
	,'project2': r'comment2: <BR/>aaa'
}

class Project:
	def __init__(self, projectStr, slnpath):
		self.comments = ''
		projectNameGUIDpattern = r'Project[^=]+=\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"\{([^"]+)\}"'
		m = re.search(projectNameGUIDpattern,projectStr)
		self.name = m.group(1)
		self.GUID = m.group(3).upper()
		self._fullpath = os.path.join(slnpath,m.group(2))

		#case 1: dependency specified in solution file.
		projectDependenciesPattern = r'\{([\w-]+)\}\s=\s\{([\w-]+)\}'
		m = re.findall(projectDependenciesPattern,projectStr)
		self.dependencyList = []
		for match in m:
			if(match[0]==match[1]):
				upperDep = match[0].upper()
				if(upperDep=='755AD11C-80B9-4E33-9D3D-9A68884A3EC8'):
					pass
				self.dependencyList.append(upperDep)

		#case 2: denpendency specified in specific project file.
		# <ProjectReference Include="..\MsgCreator\MsgCreator.vcxproj">
		#      <Project>{d3eada85-50f9-4a1d-a2f7-18612358b436}</Project>
		#      <ReferenceOutputAssembly>false</ReferenceOutputAssembly>
		# </ProjectReference>
		with open(self._fullpath, "r") as file:
			contents = file.read()
			projxml = BeautifulSoup(contents, "lxml")
			find_depen = projxml.find_all('project')
			for dep in find_depen:
				if dep.parent and dep.parent.name=='ProjectReference'.lower():
					parentProj = dep.text.replace('{','')
					parentProj = parentProj.replace('}','')
					upperDep = parentProj.upper()
					if(upperDep=='755AD11C-80B9-4E33-9D3D-9A68884A3EC8'):
						pass
					self.dependencyList.append(parentProj.upper())

		self.dependencyProjects = []

	def __hash__(self):
		return hash(self.GUID)
	def __eq__(self,other):
		if(self.name==other.name and  self.GUID==other.GUID):
			return True
		return False
	
	
new_node_nocomment = '''%d [shape=none label=<<table border="0" cellspacing="0"><tr><td port="port1" border="1" color="red"><B>%s</B></td></tr></table>>]\n'''
new_node_withcomment = '''%d [shape=none label=<<table border="0" cellspacing="0"><tr><td port="port1" border="1" bgcolor="green"><B>%s</B></td></tr><tr><td port="port2" border="1">%s</td></tr></table>>]\n'''
if __name__ == '__main__':
	'''Usage: this_file 201x_sln_file'''
	slnFileName = sys.argv[1]
	#slnFileName = r'C:\cpp\xalan-c-Xalan-C_1_11_0\Projects\Win32\VC15\Xalan.sln'
	slnpath = os.path.dirname(slnFileName)

	slnFile = open(slnFileName,'r')
	slnStr = slnFile.read()
	
	projectStartPos = 0
	projectEndPos = 0
	PROJECT_START_CONSTANT = 'Project("{'
	PROJECT_END_CONSTANT = 'EndProject'
	project_list = []
	while(1):
		projectStartPos = slnStr.find(PROJECT_START_CONSTANT,projectStartPos)
		if(projectStartPos<0):
			break;
		projectEndPos = slnStr.find(PROJECT_END_CONSTANT,projectStartPos)
		if(projectEndPos<0):
			print('NO EndProject closes the project')
			break;
		project_string = slnStr[projectStartPos:projectEndPos]
		project_list.append(Project(project_string, slnpath))
		
		projectStartPos = projectEndPos
		
	print("Total# of projects: %d"%(len(project_list)))
	
	
	guid2ProjectMap = {}
	for project in project_list:
		guid2ProjectMap[project.GUID] = project
	#update dependencyProjects
	for project in project_list:
		for dependGuid in project.dependencyList:
			if dependGuid in guid2ProjectMap:
				project.dependencyProjects.append(guid2ProjectMap[dependGuid])
			else:
				print('project %s depend on a project not in solution:%s'%(project.name, dependGuid))
	
	#generate DOT file
	dot_file_name = 'temp.dot'
	dot = open(dot_file_name,'w+')
	dot.write("digraph Tree {\n")
	#dot.write('node [shape=record color=blue fontname="bold"] ;\n')
	#generate ID for project
	project2IDMap = {}
	refProjectList = set([])
	i = 0
	for project in project_list:
		project2IDMap[project]=i
		i+=1;
	for project in project_list:
		if(len(project.dependencyProjects)>0):
			refProjectList.add(project)
			for dependProject in project.dependencyProjects:
				refProjectList.add(dependProject)
				
	singlefile = open('single.txt','w+')
	for project in project_list:
		if(project in refProjectList):
			if(project.name in projectsCommentMap):
				projectcomments = projectsCommentMap[project.name]
				dot.write(new_node_withcomment%(project2IDMap[project], project.name,projectcomments))
			else:
				dot.write(new_node_nocomment%(project2IDMap[project], project.name))
			if(len(project.dependencyProjects)>0):
				for depend_project in project.dependencyProjects:
					dot.write("%d -> %d ;\n"%(project2IDMap[depend_project],project2IDMap[project]))
		else:
			singlefile.write(project.name)
			singlefile.write('\n')
	dot.write("}")
	dot.close()
	singlefile.close()
	
