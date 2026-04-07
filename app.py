from flask import Flask, request, jsonify, send_file, render_template
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io, base64

app = Flask(__name__)

def fmt_fcfa(n):
    try:
        n = int(float(n))
        s = f"{n:,}".replace(",", ".")
        return f"{s} F"
    except:
        return str(n)

def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm)

    story = []
    violet = colors.HexColor('#7030A0')
    blue_header = colors.HexColor('#4472C4')
    light_blue = colors.HexColor('#EEF2FF')
    light_violet = colors.HexColor('#E8E0F0')
    light_pink = colors.HexColor('#FFE9E9')

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    title_p = Paragraph(
        f'<u><b>{data.get("titre","DEVIS DE COFFRAGE")}</b></u>',
        ps('title', fontName='Helvetica-Bold', fontSize=16, alignment=TA_CENTER, spaceAfter=20)
    )
    story.append(title_p)
    story.append(Spacer(1, 0.3*cm))

    col_widths = [8.5*cm, 2.5*cm, 3*cm, 3.5*cm]

    def hcell(txt):
        return Paragraph(f'<b>{txt}</b>',
            ps('hc', fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER,
               textColor=colors.white))

    header = [hcell('DESIGNATION'), hcell('QTE'), hcell('PU'), hcell('MONTANT')]
    table_data = [header]
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), blue_header),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#AAAAAA')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]

    row_idx = 1
    grand_total = 0

    for sec in data.get('sections', []):
        sec_total = 0
        items = sec.get('items', [])

        for i, item in enumerate(items):
            bg = colors.white if i % 2 == 0 else light_blue
            style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg))

            try:
                q = float(str(item.get('qte','')).replace(',','.') or 0)
                p = float(str(item.get('pu','')).replace(',','.') or 0)
                m = float(str(item.get('montant','')).replace(' ','').replace(',','.') or 0)
                montant = q * p if (q and p) else m
            except:
                montant = 0

            sec_total += montant

            def tcell(txt, align=TA_LEFT, bold=False):
                fn = 'Helvetica-Bold' if bold else 'Helvetica'
                return Paragraph(f'<font name="{fn}">{txt}</font>',
                    ps(f'tc{row_idx}', fontName=fn, fontSize=9, alignment=align))

            pu_str = fmt_fcfa(item.get('pu','')) if item.get('pu') else ''
            row = [
                tcell(str(item.get('designation','')), TA_LEFT),
                tcell(str(item.get('qte','')) if item.get('qte') else '', TA_CENTER),
                tcell(pu_str, TA_RIGHT),
                tcell(fmt_fcfa(montant) if montant else '', TA_RIGHT),
            ]
            table_data.append(row)
            row_idx += 1

        label = sec.get('label_total', f'TOTAL {sec.get("nom","").upper()}')
        tot_row = [
            Paragraph(f'<b>{label}</b>',
                ps(f'st{row_idx}', fontName='Helvetica-Bold', fontSize=9, textColor=violet)),
            Paragraph('', ps('x')),
            Paragraph('', ps('x')),
            Paragraph(f'<b>{fmt_fcfa(sec_total)}</b>',
                ps(f'sv{row_idx}', fontName='Helvetica-Bold', fontSize=9, alignment=TA_RIGHT, textColor=violet)),
        ]
        table_data.append(tot_row)
        style_cmds += [
            ('BACKGROUND', (0, row_idx), (-1, row_idx), light_violet),
            ('SPAN', (1, row_idx), (2, row_idx)),
        ]
        row_idx += 1
        grand_total += sec_total

    gt_row = [
        Paragraph('<b>TOTAL GÉNÉRAL DU DEVIS</b>',
            ps('gt', fontName='Helvetica-Bold', fontSize=11, textColor=violet, alignment=TA_CENTER)),
        Paragraph('', ps('x')),
        Paragraph('', ps('x')),
        Paragraph(f'<b>{fmt_fcfa(grand_total)}</b>',
            ps('gv', fontName='Helvetica-Bold', fontSize=11, alignment=TA_RIGHT, textColor=violet)),
    ]
    table_data.append(gt_row)
    style_cmds += [
        ('BACKGROUND', (0, row_idx), (-1, row_idx), light_pink),
        ('SPAN', (0, row_idx), (2, row_idx)),
        ('TOPPADDING', (0, row_idx), (-1, row_idx), 10),
        ('BOTTOMPADDING', (0, row_idx), (-1, row_idx), 10),
    ]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    pdf_buffer = generate_pdf(data)
    titre = data.get('titre', 'devis').replace(' ', '_').lower()
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{titre}.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
