from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self,filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename,pagesize = letter)
        self.elements = []
        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Heading1"],
            fontSize = 24,
            textColor = colors.HexColor("#2c3e50"),
            spaceAfter = 30,
            alignment = TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            "CustomHeading",
            parent = self.styles["Heading2"],
            fontSize = 16,
            textColor = colors.HexColor("#34495e"),
            spaceAfter = 12,
            spaceBefore = 12
        )

        self.normal_style = self.styles["Normal"]

    def add_title(self,title):
        self.elements.append(Paragraph(title,self.title_style))
        self.elements.append(Spacer(1,0.2*inch))

    def add_heading(self,heading):
        self.elements.append(Paragraph(heading,self.heading_style))
        self.elements.append(Spacer(1,0.1*inch))

    def add_paragraph(self,text):
        self.elements.append(Paragraph(text,self.normal_style))
        self.elements.append(Spacer(1,0.1*inch))

    def add_spacer(self,height=0.2):
        self.elements.append(Spacer(1,height*inch))

    def add_table(self,data,col_widths=None):
        if not data:
            return
        table = Table(data,colWidths=col_widths)
        table.setStyle(
            TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#34495e")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),

            ])
        )
        self.elements.append(table)
        self.elements.append(Spacer(1,0.2*inch))

    def add_image(self,image_path,width=6*inch,height=4*inch):
        if os.path.exists(image_path):
            img = Image(image_path,width=width,height=height)
            self.elements.append(img)
            self.elements.append(Spacer(1,0.2*inch))

    def add_page_break(self):
        self.elements.append(PageBreak())

    def add_line(self):
        from reportlab.platypus import HRFlowable
        self.elements.append(HRFlowable(width="100%",thickness=1,
                                        color=colors.HexColor("#bdc3c7")))
        self.elements.append(Spacer(1,0.1*inch))

    def build(self):
        self.doc.build(self.elements)
