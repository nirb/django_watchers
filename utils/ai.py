from openai import OpenAI
import PyPDF2
import os

# Function to extract text from PDF


def extract_text_from_pdf(pdf_path, fd):
    if fd == None:
        fd = open(pdf_path, 'rb')
    reader = PyPDF2.PdfReader(fd)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    # print("extract_text_from_pdf", text)
    return text

# Function to analyze the extracted text using OpenAI API with completion


def analyze_pdf_text(pre_text, text):
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    # print("analyze_pdf_text start")
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are finance specialist."
            },
            {
                "role": "user",
                "content": f"{pre_text} - {text}."
            }
        ]
    )

    # print("analyze_pdf_text start", response.choices[0].message.content)

    return response.choices[0].message.content

# Main function to process PDF and get analysis as JSON


def analyze_pdf(pre_text, pdf_path, fd):
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path, fd)

    # Call OpenAI to analyze the text
    analysis_result = analyze_pdf_text(pre_text, pdf_text)

    return analysis_result


def analyze_doc(pre_text, file_path, fd=None):
    print(f"analyzing {file_path=} {fd=}")
    analysis_result = analyze_pdf(pre_text, file_path, fd)
    return analysis_result
