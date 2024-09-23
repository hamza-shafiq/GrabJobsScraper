from PyPDF2 import PdfReader

class PDFParser():

    def __init__(self, file_name):
        self.file_name = file_name
    
    def extract_text(self):
        resume_content = ""
        reader = PdfReader(self.file_name)
        for page in reader.pages:
            resume_content = resume_content + page.extract_text()
        
        return resume_content
