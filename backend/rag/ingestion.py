class KnowledgeIngestion:
    async def ingest_pdf(self, file_path):
        return {'status': 'pdf ingested', 'file': file_path}

    async def ingest_docx(self, file_path):
        return {'status': 'docx ingested', 'file': file_path}

    async def crawl_website(self, url):
        return {'status': 'website crawled', 'url': url}
