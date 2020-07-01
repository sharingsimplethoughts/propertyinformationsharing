from django import forms

def is_whitespaces(string):
	string_a = string.replace('&nbsp;', '')
	string_b = 	string_a.replace('<p>' , '')
	string_c = 	string_b.replace('</p>' , '')
	string_d = string_c.replace('\r\n' , '')
	string_e = string_d.strip()
	print(string_e,'sdfggggggggggg')
	if string_e =='':
		return True
	else:
		return False

class SettingsManagementEditForm(forms.Form):
	servicedesc	= forms.CharField(required=False)
	# terms 		= forms.CharField(required=False)
	# contact_us 	= forms.CharField(required=False)

	def clean(self):
		if is_whitespaces(self.cleaned_data.get('servicedesc')):
			raise forms.ValidationError('Whitespaces are not allowed in input fields')

		return self.cleaned_data
