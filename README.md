# XML Contract Data Importer for Django

A Django management command that automates the parsing and importing of contract award data from XML files into Django
models.

---

## Overview

This project provides a management command `import_xml_documents_data_to_database` for a Django application, allowing
structured XML contract
data (TED R2.0.9 and eForms 2021 UBL extension formats) to be automatically parsed and imported into the database.

It extracts key information such as contracting authority details, contract descriptions, awarded winners, and CPV
codes, mapping it to Django models like Authority, Contract, ContractObject, and more.


> ⚠️ **Warning**
>
> Currently, works only for documents with form F03

---

## Project Status: ❌ Abandoned

The project was eventually discontinued as it became redundant because [OpenTender](https://opentender.eu/) exists.
OpenTender provides much more comprehensive, structured, and up-to-date access to this information, complete with
analysis tools and datasets.

Despite this, the project served as a valuable learning experience.

---

## Features

- Automated XML Parsing: Scans a directory for .xml files and processes each.

- Duplicate Prevention: Skips already-processed files using unique DOC_ID.

- Structured Data Extraction:
    - Base contract details
    - Contracting authority info
    - Contract objects and items
    - Winner details
    - Original and main CPV codes

- Currency Conversion: Converts monetary values to EUR using a predefined exchange rate dictionary.
- Database Operations:
    - Ensures referential integrity via Django ORM.
- Atomic Transactions: Ensures consistent database state with rollback on error.
- Data Cleaning: Normalizes names, trims whitespace, and removes punctuation.
- Logging: Console outputs for progress, warnings, and successes.

---

## How It Works (High-Level Flow)

1. Command Execution:
    ```bash
    python manage.py import_xml_documents_data_to_database

2. Directory Traversal:
   Looks for `.xml` files inside:

   `[BASE_DIR]/api/management/test_documents`

3. Duplicate Check:
   Skips XMLs whose `DOC_ID` is already present in the database.

4. XML Parsing:
   Uses `xml.etree.ElementTree` for XML navigation.

5. Data Extraction:
   Helper functions handle different parts of the document:

    - `extract_base_contract_data`

    - `extract_authority_contract_data`

    - `extract_object_data`

    - `extract_award_contract_winner_data`

6. Data Structuring:
   Extracted values are mapped into structured dictionaries for clean model saving.

7. Model Saving

8. Logging:
   Informative success and warning messages are shown in the terminal.

---

## Models Involved

- Authority: Contracting body details
- Contract: Central contract record
- ContractObject: Summary of contract scope
- ContractObjectItem: Specific items/lots
- Winner: Awarded contractor details
- Category: CPV code mapping
- Country: Country code reference

---

## XML Structure Assumptions

The importer expects the following key XML elements and namespaces (TED/eForms-compliant):

- `<AWARD_CONTRACT>`

- `<ADDRESS_CONTRACTING_BODY>`

- `<CODED_DATA_SECTION>`

- `<NOTICE_DATA>`

- `<URI_LIST>`

- `<OBJECT_CONTRACT>`

- Monetary values: `<VAL_TOTAL>`, `<VAL_ESTIMATED_TOTAL>`, `<VAL_RANGE_TOTAL>`

- CPV codes: `<CPV_MAIN>`, `<CPV_ADDITIONAL>`

---

## Usage

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>

2. Create and Activate a Virtual Environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install Dependencies:

    ```bash
    pip install -r requirements.txt

4. Create a .env File:

   Create a .env file in the project root with the following required environment variables:

    ```bash
    APP_ENVIRONMENT=Development
    SECRET_KEY=your-secret-key
    
    # Database settings
    DB_NAME_DEV=your_db_name
    DB_USER_DEV=your_db_user
    DB_PASSWORD_DEV=your_db_password
    DB_HOST_DEV=your_db_host
    DB_PORT_DEV=your_db_port
    
    # Web and CORS settings
    ALLOWED_HOSTS=localhost 127.0.0.1
    
    
    # (Optional): only if you run it with the frontend
    AUTH_COOKIE_SECURE=False  # Set to True in production
    CORS_ALLOWED_ORIGINS=http://localhost:3000

   - Adjust the values according to your environment.

5. Apply Migrations:

    ```bash
    python manage.py migrate

6. Run the Development Server:

   ```bash
   python manage.py runserver

7. Import CPV codes to database:

    ```bash
   python manage.py import_cpv_codes_to_database

8. Place XML files into `[BASE_DIR]/api/management/test_documents` or change
   `root_directory = BASE_DIR / 'api' / 'management' / 'test_documents'` in `import_xml_documents_data_to_database.py`
   file to desirable destination


9. Start extracting:

    ```bash
   python manage.py import_xml_documents_data_to_database

## Project Context & Status

This project was initially created as an experiment to build a centralized database of public tender data from XML
documents. The goal was to:

- Learn how to parse and understand TED/eForms XML files manually.

- Build tooling around document parsing without relying on the official TED APIs.

- Create a foundation for tender analysis, comparisons, and public transparency.

The importer currently supports only F03 form documents (contract award notices).