"""
Test the Chinese Excel parser with sample data.
"""

from src.parsers.chinese_excel_parser import ChineseExcelParser
import json


def main():
    parser = ChineseExcelParser()

    # Test with our sample Excel file
    file_path = "data/sample_restaurant_income_2025.xlsx"

    print("Testing Chinese Excel Parser")
    print("=" * 50)

    result = parser.parse_income_statement(file_path)

    print(f"Parsing status: {result['parsing_status']}")
    print(f"File: {result['file_path']}")

    if result['parsing_status'] == 'success':
        print(f"\nStructure analysis:")
        structure = result['structure']
        print(f"  Sheet shape: {structure['shape']}")
        print(f"  Non-empty rows: {structure['non_empty_rows']}")
        print(f"  Detected header row: {structure['detected_header_row']}")

        print(f"\nExtracted periods:")
        for period in result['periods']:
            print(f"  - {period}")

        print(f"\nFinancial data preview:")
        financial_data = result['financial_data']
        for key, data in list(financial_data.items())[:5]:
            print(f"  {key}:")
            print(f"    Chinese: {data['chinese_term']}")
            print(f"    Values: {data['values']}")

        print(f"\nTotal line items extracted: {len(financial_data)}")

    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\nSupported term mappings:")
    for chinese, english in list(parser.get_supported_terms().items())[:10]:
        print(f"  {chinese} -> {english}")


if __name__ == "__main__":
    main()