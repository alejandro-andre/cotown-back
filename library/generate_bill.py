# ######################################################
# Imports
# ######################################################

from io import BytesIO
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

# ######################################################
# Generate bill
# ######################################################

def generate_bill(context, template):

  # Jinja environment
  env = Environment(
      loader=FileSystemLoader('./'),
      autoescape=select_autoescape(['html', 'xml'])
  )

  # Generate HTML
  tpl = env.get_template(template)
  result = tpl.render(data=context)

  # Generate PDF
  file = BytesIO()
  html = HTML(string=result)
  html.write_pdf(file)
  file.seek(0)
  return file