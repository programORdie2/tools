style2 = open('HC.css').read()
style=style2.replace('50px', '5px')
style = style.replace('blue', '#8633FF')
footer = open('HCfooter.html').read()
def dpage(n):
    return f'''<html><head>{style2}<link rel="icon" type="image/png" href="../static/faveicon.png" /></head><body><center><h1>Removed code!</h1><br><br><br><form action="/hc/download" method="post"><button type="submit" value="{n}" name="download">Download</button></form></center></body>{footer}</html>'''
hcmainsite = f'''<html><head>{style}<link rel="icon" type="image/png" href="../static/faveicon.png" /></head><body><center><h1>Hide the code of a Scratch Project!</h1><br><form id="FileUploadForm" action="/hc/upload" method="post" enctype="multipart/form-data"><input type="file" name="file" id="FileUploadHidedButton" accept=".sb3" onChange="document.getElementById('FileUploadForm').submit();" style="display:none;" /><button type="button" onclick="document.getElementById('FileUploadHidedButton').click();">Upload a Project From Your Computer</button></form></center></body>{footer}</html>
'''
