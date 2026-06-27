import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.call_llm import call_llm

def read_csv_file(file_path: str) -> list| None:
    suffix = Path(file_path).suffix
    if suffix == '.csv':
        data = pd.read_csv(file_path)
        summary = data.describe() # make a statistic summary of the csv file data
        data_value_count = data.value_counts() # return unique values
        
        return {"summary": summary, "value_ccounts": data_value_count}
    else:
        print('The input file its not a CSV file.')
        return None

def generate_text_file(text_content: str) -> str | None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents = True, exist_ok = True)
    output_file_path = output_dir / f"../output/{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
         with open(output_file_path, "w", encoding = "utf-8") as file:
            if text_content:
                file.write(text_content)
                return f"File succesfully {output_file_path} created!"
            
    except FileNotFoundError:
        print("Directory not found.")
    except UnicodeEncodeError:
        print("Encoding error.")
    except OSError:
        print("Operational System error")
    except Exception as e:
        print(f"Unexpected error: {e}")



def report(file_path: str) -> str| None:
    if file_path:
        prompt = f"""
            You are an expert Data Analyst.
            You will receive a list with two elements:

            * `data[0]`: Statistical summary of a CSV dataset (similar to `pandas.DataFrame.describe(include="all")`).
            * `data[1]`: Unique values for each column (may be truncated).

            Using **only** the provided information, generate a detailed statistical analysis.

            Include:

            * Dataset overview.
            * Data quality (missing values, cardinality, constant columns, inconsistencies).
            * Analysis of each numerical column (distribution, variability, outliers, skewness).
            * Analysis of each categorical column (cardinality, frequency concentration, dominant values).
            * Insights from unique values (invalid values, formatting issues, placeholders).
            * Key patterns, anomalies, and business insights.
            * Actionable recommendations for data cleaning, preprocessing, feature engineering, and further analysis.
            * A brief section describing the limitations of drawing conclusions from summary statistics alone.

            Requirements:

            * Do not invent or assume missing information.
            * Clearly separate facts from hypotheses.
            * Use Markdown headings and tables when appropriate.
            * If information is unavailable, explicitly state that it cannot be determined.

            List:

            {read_csv_file(file_path)}
            """
        text_content = call_llm(prompt)
        return generate_text_file(text_content)

    else:
        raise FileNotFoundError(f'Could not find the file path: {file_path}')
