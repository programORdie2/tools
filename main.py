import os, time, glob, scratchattach
from fileinput import filename
from flask import *
from pathlib import Path
import zipfile
import shutil
from os.path import splitext
from threading import Thread

from HCwebpage_content_all import *

app = Flask(__name__)


@app.route('/')
def homepagereal():
  return '<html><link rel="icon" type="image/png" href="../static/faveicon.png" /><a href="/qr">QRcode Generator</a><br><a href="/hc">ScratchProject Code Hider</a></html>'


def remove(file):
  time.sleep(10)
  os.remove(file)


@app.route('/scratch-qr/<encoded>')
def from_scratch(encoded: str):
  d = scratchattach.Encoding.decode(encoded)
  print(d)
  _, data, colors, bgcolors = d.split('&')
  return '''<body><center>
<form onload="autoSubmit();" name="myform" id="myform" action="/qr/generate" method="POST">
  <p>
  <input name="data" value="'''+data+'''" type="hidden" />
  <input name="colors" value="'''+colors+'''" type="hidden" />
  <input name="bgcolors" value="'''+bgcolors+'''" type="hidden" />
  </p>
  <p>
    <input type="submit" name="submit" value="See QRcode" />
  </p>
</form>
<script type="text/javascript">
function autoSubmit() {
                document.forms["myform"].submit();
            }
window.onload = autoSubmit();
</script></center>
</body>
    '''

@app.route('/qr', methods=['GET'])
def qr():
  return render_template('qr.html')


@app.route('/qr/generate', methods=['POST'])
def qr_generate():
  bg = request.form['bgcolors']
  mc = request.form['colors']
  url = request.form['data']
  r = gen_qr(bg, mc, url)
  dlink = f'/qr/download?d={url}&c={mc}&b={bg}'
  Thread(target=remove, args=[r]).start()
  r = f'https://tools.programordie.repl.co/{r}'
  return render_template('qrcodepage.html', image=r, download=dlink)

@app.route('/qr/download')
def dwnload():
  bg = request.args['b']
  mc = request.args['c']
  url = request.args['d']
  r = gen_qr(bg, mc, url)
  Thread(target=remove, args=[r]).start()
  return send_file(r, as_attachment=True)


@app.route('/hc')
def main():
  for file in glob.glob('*.sb3'):
    os.remove(file)
  return hcmainsite


@app.route('/hc/upload', methods=['POST'])
def upload():
  if request.method == 'POST':
    f = request.files['file']
    f.save(f.filename)
    of = hide(f.filename)
    return dpage(of)


@app.route('/hc/download', methods=["POST"])
def dwnld():
  if request.method == "POST":
    d = str(request.form.get("download"))
    Thread(target=remove, args=[d]).start()
    return send_file(d, as_attachment=True)


from PIL import Image
import random, qrcode

logo = Image.open('static/qrcodelogo.png')
basewidth = 50
wpercent = (basewidth / float(logo.size[0]))
hsize = int((float(logo.size[1]) * float(wpercent)))
logo = logo.resize((basewidth, hsize), Image.LANCZOS)


def gen_qr(bg, mc, url):
  QRID = f'static/QRcode{random.randint(0, 99999999999999999999999999)}'
  QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
  QRcode.add_data(url)
  QRcode.make()
  QRcode = QRcode.make_image(fill_color=mc, back_color=bg).convert('RGB')
  pos = ((QRcode.size[0] - logo.size[0]) // 2,
         (QRcode.size[1] - logo.size[1]) // 2)
  QRcode.paste(logo, pos)
  QRcode.save(f'{QRID}.png')
  return f'{QRID}.png'


def hide(name):
  name = splitext(name)[0]
  if os.path.isdir("files"):
    shutil.rmtree('files')
  os.mkdir('files')
  file_path = Path(rf"{name}.sb3")
  new_file_path = file_path.with_suffix(".zip")
  try:
    renamed_path = file_path.rename(new_file_path)
  except FileNotFoundError:
    print(f"Error: could not find the '{file_path}' file.")
  except FileExistsError:
    print(f"Error: the '{new_file_path}' target file already exists.")
  else:
    print(f"Changed extension of '{file_path.name}' to '{renamed_path.name}'.")
  file_name = f"{name}.zip"
  with zipfile.ZipFile(file_name, "r") as zip:
    zip.extractall("files")
  with open('files/project.json') as fp:
    data = fp.read()
    data = data.replace('"shadow":false', '"shadow":true')

  def assign_variable_value_to_file(variable_name, file_name):
    with open(file_name, "w") as f:
      f.write(variable_name)

  variable_name = data
  file_name = "files/project.json"
  assign_variable_value_to_file(variable_name, file_name)
  with open(file_name, "r") as f:
    assert f.read() == variable_name

  def create_sb3_archive(directory, archive_path):
    archive = zipfile.ZipFile(archive_path, "w")
    try:
      project_json_path = os.path.join(directory, "project.json")
      archive.write(project_json_path, "project.json")
      assets_dir = os.path.join(directory, "assets")
      for root, dirs, files in os.walk(assets_dir):
        for file in files:
          file_path = os.path.join(root, file)
          archive_path = os.path.relpath(file_path, directory)
          archive.write(file_path, archive_path)
    finally:
      archive.close()

  directory = "files"
  archive_path = f"{name} - No Code!.sb3"
  create_sb3_archive(directory, archive_path)
  shutil.rmtree('files')
  if os.path.isfile(f"{name}.zip"):
    os.remove(f"{name}.zip")
  return archive_path


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080)
