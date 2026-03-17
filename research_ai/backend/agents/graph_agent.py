import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
import json

class GraphAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.idea_prompt = PromptTemplate(
            template="""You are a Research Data Visualization Expert.
            Based on the research topic provided, suggest 3-4 specific ideas for graphs or charts that would be highly impactful in a research paper.
            1. Provide a Title.
            2. Provide a Description of what the graph shows. Ensure there are no unescaped quotes.
            3. Specify the Type (e.g., Bar Chart, Line Graph, Scatter Plot, Heatmap).
            4. Provide Mock Data (X and Y values) as a list of dictionaries that can be easily parsed for plotting.
               - For Bar, Line, Scatter: {{"x": ["A", "B"], "y": [10, 20]}}
               - For Heatmap: {{"matrix": [[1, 2], [3, 4]], "x_labels": ["C1", "C2"], "y_labels": ["R1", "R2"]}}
            If custom data is provided below, base the mock data strictly on the actual trends/values found in that data.
            
            Topic: {topic}
            Custom Data (if provided): {custom_data}
            
            Format the output strictly as a JSON object containing an "ideas" array:
            {{
                "ideas": [
                    {{
                        "title": "Title",
                        "description": "Description",
                        "type": "Type",
                        "mock_data": {{"x": ["A", "B", "C"], "y": [10, 20, 30]}}
                    }}
                ]
            }}
            """,
            input_variables=["topic", "custom_data"]
        )

    def generate_ideas(self, topic, custom_data=None):
        chain = self.idea_prompt | self.llm
        res = chain.invoke({"topic": topic, "custom_data": custom_data or "None provided."})
        
        print(f"Raw graph idea response: {res.content}")
        
        raw_content = res.content.strip()
        start = raw_content.find("{")
        end = raw_content.rfind("}")
        
        if start != -1 and end != -1:
            clean_json = raw_content[start : end + 1]
        else:
            clean_json = raw_content
            
        try:
            parsed = json.loads(clean_json.strip())
            return parsed.get("ideas", [])
        except Exception as e:
            print(f"Error parsing graph ideas: {e}")
            import re
            
            # Fallback regex extraction if the JSON object parsing fails
            try:
                start_arr = raw_content.find("[")
                end_arr = raw_content.rfind("]")
                if start_arr != -1 and end_arr != -1:
                    arr_json = raw_content[start_arr : end_arr + 1]
                    return json.loads(arr_json)
            except Exception as e2:
                print(f"Fallback parsing failed: {e2}")
            return []

    def generate_graph(self, idea, output_dir):
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="darkgrid")
        
        title = idea.get("title", "Research Graph")
        data = idea.get("mock_data", {})
        g_type = idea.get("type", "Bar Chart").lower()
        
        x = data.get("x", [])
        y = data.get("y", [])
        
        if "bar" in g_type:
            sns.barplot(x=x, y=y, palette="viridis")
        elif "line" in g_type:
            sns.lineplot(x=x, y=y, marker="o", color="blue")
        elif "scatter" in g_type:
            sns.scatterplot(x=x, y=y, color="red")
        elif "heatmap" in g_type:
            matrix = data.get("matrix", [])
            x_labels = data.get("x_labels", [])
            y_labels = data.get("y_labels", [])
            if matrix:
                sns.heatmap(matrix, annot=True, xticklabels=x_labels, yticklabels=y_labels, cmap="YlGnBu")
        else:
            sns.barplot(x=x, y=y)
            
        plt.title(title, fontsize=15, color="white")
        plt.xticks(rotation=45, color="#94a3b8")
        plt.yticks(color="#94a3b8")
        
        fn = f"{title.replace(' ', '_').lower()}.png"
        path = os.path.join(output_dir, fn)
        os.makedirs(output_dir, exist_ok=True)
        
        # Make transparent background for premium feel
        plt.savefig(path, transparent=True, bbox_inches='tight')
        plt.close()
        return fn

    def plot_csv_directly(self, csv_content, output_dir):
        """Intelligently parse CSV and plot the best possible graph."""
        import pandas as pd
        import io
        
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            if df.empty: return None
            
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="darkgrid")
            
            cols = df.columns
            if len(cols) >= 2:
                # Try to find numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 1:
                    x_col = cols[0]
                    y_col = numeric_cols[0]
                    
                    # If x is also numeric, maybe scatter, else bar
                    if pd.api.types.is_numeric_dtype(df[x_col]):
                        sns.lineplot(data=df, x=x_col, y=y_col, marker="o")
                        g_type = "Line"
                    else:
                        sns.barplot(data=df, x=x_col, y=y_col, palette="magma")
                        g_type = "Bar"
                    
                    title = f"Direct Plot: {y_col} vs {x_col}"
                else:
                    # Just plot counts if no numeric
                    sns.countplot(data=df, x=cols[0])
                    title = f"Direct Plot: Count of {cols[0]}"
                    g_type = "Count"
            else:
                sns.countplot(data=df, x=cols[0])
                title = f"Direct Plot: Count of {cols[0]}"
                g_type = "Count"

            plt.title(title, fontsize=15, color="white")
            plt.xticks(rotation=45, color="#94a3b8")
            plt.yticks(color="#94a3b8")
            
            fn = f"direct_plot_{int(os.path.getmtime(output_dir) if os.path.exists(output_dir) else 0)}.png" # simplistic unique name
            path = os.path.join(output_dir, fn)
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(path, transparent=True, bbox_inches='tight')
            plt.close()
            return fn
        except Exception as e:
            print(f"Error plotting CSV: {e}")
            return None
