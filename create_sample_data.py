"""
Create sample Excel files for testing the Chinese financial parser.
"""

import pandas as pd
from pathlib import Path


def create_sample_income_statement():
    """Create a sample Chinese restaurant income statement."""
    data = {
        "2025年利润表（样本餐厅）": [
            "项目",
            "一、营业收入",
            "食品收入",
            "酒水收入",
            "甜品/糖水收入",
            "其他（碳餐盒等）收入",
            "折扣",
            "减:主营业务成本",
            "食品成本",
            "酒水成本",
            "甜品/糖水成本",
            "二、毛利",
            "毛利率",
            "食品毛利率：",
            "酒水毛利率：",
            "甜品/糖水毛利率：",
            "四、营业费用",
            "其中：人工成本",
            "工资",
            "社保/商业保险",
            "其中：租赁费用",
            "门面房租",
            "宿舍租金",
            "物业费/垃圾清运"
        ],
        "2024年12月-2025年2月": [
            "2024年12月-2025年2月",
            603327.65,
            499031.37,
            24353.30,
            62802.92,
            17140.06,
            -48539.35,
            231058.39,
            220609.57,
            10448.82,
            16391.50,
            372269.26,
            0.617,
            0.607,
            0.571,
            0.677,
            269320.99,
            119699.00,
            119699.00,
            0,
            30999.96,
            27993.60,
            1400.00,
            1606.36
        ],
        "占比": [
            "占比",
            1.0,
            0.827,
            0.040,
            0.104,
            0.028,
            -0.080,
            0.383,
            0.366,
            0.017,
            0.027,
            0.617,
            None,
            None,
            None,
            None,
            0.446,
            0.198,
            0.198,
            0,
            0.051,
            0.046,
            0.002,
            0.003
        ],
        "3月": [
            "3月",
            491511.22,
            406926.69,
            19870.16,
            50691.60,
            14022.77,
            -77977.78,
            158368.08,
            133760.08,
            8216.50,
            13400.91,
            333143.14,
            0.678,
            0.671,
            0.586,
            0.683,
            158632.62,
            72992.36,
            71576.00,
            1416.36,
            16049.98,
            13996.80,
            1250.00,
            803.18
        ],
        "占比_1": [
            "占比",
            1.0,
            0.828,
            0.040,
            0.103,
            0.029,
            -0.159,
            0.322,
            0.272,
            0.017,
            0.027,
            0.678,
            None,
            None,
            None,
            None,
            0.323,
            0.149,
            0.146,
            0.003,
            0.033,
            0.028,
            0.003,
            0.002
        ],
        "4月": [
            "4月",
            433546.90,
            363965.57,
            14132.45,
            42318.85,
            13130.03,
            -68741.10,
            157917.43,
            137624.62,
            6891.90,
            14444.50,
            275629.47,
            0.636,
            0.622,
            0.512,
            0.726,
            155415.27,
            79569.36,
            78339.00,
            1230.36,
            16049.98,
            13996.80,
            1250.00,
            803.18
        ]
    }

    return pd.DataFrame(data)


def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Create sample income statement
    df = create_sample_income_statement()

    # Save to Excel
    output_path = data_dir / "sample_restaurant_income_2025.xlsx"
    df.to_excel(output_path, index=False, sheet_name="2025年利润表（样本餐厅）")

    print(f"Created sample Excel file: {output_path}")
    print("\nData preview:")
    print(df.head(10))

    # Also create a CSV for easier inspection
    csv_path = data_dir / "sample_restaurant_income_2025.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"Created CSV file: {csv_path}")


if __name__ == "__main__":
    main()