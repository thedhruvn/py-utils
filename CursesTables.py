from util.ColorLogBase import ColorLogBase
from typing import List, Dict

class ClickReference():

	def __init__(self, value, get_value=None, on_update=None):
		#self._instance = instance
		self.value = value
		self._on_update = on_update
		self._get_value = get_value

	def set_on_click(self, on_click):
		self._on_update = on_click

	def set_get_value(self, get_value):
		self._get_value = get_value

	def _sync(self):
		if self._get_value:
			self.value = self._get_value()
			return True
		return False
		
	def get(self):
		self._sync()
		return self.value

	def update(self, new_value):
		if self._on_update:
			self._on_update(new_value)
		
		if not self._sync():
			# Manual update local value - no external call to get value
			self.value = new_value


class CursesTableStyle():

	def __init__(self, align="^", sep="|"):
		self.align = align
		self.sep = sep

class CursesTable(ColorLogBase):
	"""
	Very Basic Table: Field Header Names define width of table cells
	"""

    def __init__(self, posX: int , posY: int, field_list, title: str=None, style=None):
    	ColorLogBase.__init__(self)
        self.posX = posX
        self.posY = posY
        self.title = title
        self.style = style
        if not style:
        	self.style = CursesTableStyle()
        self.data = {}
        self.field_list = field_list
        self.row_list = []
        self.set_fields()


    def set_fields(self):
    	for field in self.field_list:
    		self.data[str(field)] = {'width': len(str(field)), 'rows': []}

    def set_rows(self, row_list, indexName = "ROWS", width=15):
    	self.row_list = row_list
    	self.data[indexName] = {'row_header': True, 'width': width, 'rows': row_list}

    def add_value(self, value, field, rowID = None, on_update=None, get_value=None):
    	if field in self.data:
    		 cr = ClickReference(value, get_value=get_value, on_update=on_update)
    		if rowID:
    			self.data[field]['rows'][rowID] = cr
    		else:
    			self.data[field]['rows'].append(cr)

    def add_values_to_rowID(self, values: List[ClickReference], rowID):
    	for field, value in zip(self.field_list, values):
    		self.data[field]['rows'][rowID] = value
    	return True

    def add_values_to_row(self, values, row):
    	if row in self.row_list:
    		return self.add_values_to_rowID(values, self.row_list.index(row))
    	return False

    def _get_header_row_key(self):
    	for key, value in self.data.items():
    		if 'row_header' in value:
    			return key
    	return None

    def _get_header_row_str(self):
    	key = self._get_header_row_key()
    	if key:
    		for 
    		outstr = f"{key:{self.style.align}{self.data[key]['width']}"

    def draw(self):


    #def load_row(self, row_dict: dict):
    #	for key, value in row_dict.items():
    #		if key in self.data:



        


class GenericTable(ColorLogBase):

    def __init__(self, posX: int , posY: int, data: PrettyTable = None, title: str =None, style=None):
        """
           Data Format (dictionary):
           {headerRowName: [column Name, column 2 Name, column 3 Name, etc.], dataRow1Name: [data1, data2, etc.]}

        """
        ColorLogBase.__init__(self)
        self.posX = posX
        self.posY = posY

        self.data = data if data else PrettyTable()
        self.title = title
        if style:
            self.style = style
        self.__set_format()
        self.title_row_skip = True

    def __set_format(self):
        self.data.set_style(MARKDOWN)

    def set_fields(self, field_list):
        self.data.field_names(field_list)

    def add_row(self, row):
        self.data.add_row(row)

    def reset_rows(self):
        self.data.clear_rows()

    def get_draw_strings(self):
        return self.data.get_string().split('\n')

    def draw(self, screen):
        if self.title:
            screen.addstr(self.posY-2, self.posX, self.title)
        i = 0
        for row in self.get_draw_strings():
            screen.addstr(self.posY+i, self.posX, row)
            i += 1


class InteractiveTable(GenericTable):

    def __init__(self, posX, posY, data, title=None):
        super().__init__(posX, posY, data, title)

    def on_double_click(self, click):
        xval = click[1] - self.posX
        yval = click[2] - self.posY - 1
        if yval > len(self.data._rows):
            return None

        def runsum(a, pad=self.data.padding_width, vsep=1):
            tot = 0
            for item in a:
                tot += pad
                tot += item
                tot += pad + vsep
                yield tot

        for idx, i in enumerate(runsum(self.data._widths)):
            if xval < i:
                return yval, idx