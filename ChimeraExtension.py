from chimera.extension import EMO, manager

class PyRy3D_EMO(EMO):

	def name(self):
		return 'PyRy3D Extension'
	def description(self):
		return 'Macromolecular modeling tool'
	def categories(self):
		return ['Utilities']
	def icon(self):
		return None
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').PyRyDialog.name)
		return None

manager.registerExtension(PyRy3D_EMO(__file__))
