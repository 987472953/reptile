from PyPDF2 import PdfReader

# 打开 PDF 文件
pdf_file = 'yinghuang/1/music-theory-grade-1-sample-model-answers-200825.pdf'

# 创建 PDF 阅读器对象
pdf_reader = PdfReader(pdf_file)

# 获取 PDF 文件的总页数
total_pages = len(pdf_reader.pages)
print(f'Total pages: {total_pages}')

# 遍历每一页并提取文本
for page_num in range(total_pages):
    page = pdf_reader.pages[page_num]
    text = page.extract_text()
    print(f'Page {page_num + 1}:\n{text}\n')

# 关闭 PDF 文件（不再需要显式关闭）
