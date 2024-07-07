import json

def document_to_dict(doc):
    return {
        'page_content': doc.page_content,
        'metadata': doc.metadata
    }


def documents_to_json(documents):
    documents_dict = [document_to_dict(doc) for doc in documents]
    return json.dumps(documents_dict, indent=2)