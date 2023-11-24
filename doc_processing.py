# import libraries
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import confid

# https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?view=doc-intel-4.0.0&preserve-view=true&pivots=programming-language-python#general-document-model

# set `<your-endpoint>` and `<your-key>` variables with the values from the Azure portal
endpoint = confid.endpoint
key = confid.key

def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join("Page #{}: {}".format(region.page_number, format_polygon(region.polygon)) for region in bounding_regions)

def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])


def read_file_from_url(file_url):
    import requests

    response = requests.get(file_url)
    if response.status_code == 200:
        file_content = response.content
        return file_content
    else:
        raise Exception(f"Failed to download file from URL: {file_url}")

def read_file_from_local(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
    return file_content

def analyze_invoice(invoice):
    print("--------Recognizing invoice--------")

    fields_to_extract = [
        "VendorName", "InvoiceId", "InvoiceDate", "DueDate", "Items",
        "SubTotal", "TotalTax", "InvoiceTotal"
    ]

    for field_name in fields_to_extract:
        field = invoice.fields.get(field_name)
        if field:
            if field_name == "Items":
                print("Invoice items:")
                for idx, item in enumerate(field.value):
                    print(f"...Item #{idx + 1}")
                    for item_field_name, item_field in item.value.items():
                        print(f"......{item_field_name}: {item_field.value}")
            else:
                print(f"{field_name}: {field.value}")

def analyze_invoice_file(file_content):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-invoice", document=file_content
    )
    invoices = poller.result()

    for idx, invoice in enumerate(invoices.documents):
        analyze_invoice(invoice)


def process_pdf_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")

            file_content = read_file_from_local(file_path)
            analyze_invoice_file(file_content)
            print("----------------------------------------")


if __name__ == "__main__":
    directory_path = "/Users/docha/Library/CloudStorage/GoogleDrive-mob37256213753@gmail.com/Мой диск/Bonus/test"
    process_pdf_files_in_directory(directory_path)