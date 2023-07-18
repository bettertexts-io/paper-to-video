import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def pdf_to_text(path):
    resource_manager = PDFResourceManager()
    file_handle = io.StringIO()
    converter = TextConverter(resource_manager, file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    
    with open(path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            
        text = file_handle.getvalue()
    
    # close open handles
    converter.close()
    file_handle.close()

    if text:
        return text


if __name__ == "__main__":
    # Test case: print the text of the paper
    print(pdf_to_text('paper-example.pdf'))
